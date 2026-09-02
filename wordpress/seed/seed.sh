#!/usr/bin/env bash
#
# Bootstraps a fresh WordPress volume into the ContentBridge demo state.
#
# Two different kinds of state, two different mechanisms:
#  - Environment-specific stuff (admin account, plugin activation, permalink
#    structure + .htaccess) is driven by env vars / explicit wp-cli commands
#    below, every time — these must NOT come from a frozen dump, because a
#    dump would bake in a specific URL/port or a committed password hash.
#  - Actual content (pages, posts, categories, nav) is restored from
#    content-dump.sql, produced by dump.sh. That file is regenerated whenever
#    content changes in wp-admin, so nothing here needs to know what the
#    content *is* — only how to load it.
#
# Runs automatically via the `wordpress-seed` one-shot service in
# docker-compose.yml. Safe to re-run manually too — no-ops once the
# `contentbridge_seeded` option is set.

set -euo pipefail

WP_PATH="/var/www/html"
WP="wp --allow-root --path=$WP_PATH"
DUMP_FILE="$WP_PATH/wp-content/seed/content-dump.sql"

: "${WP_URL:?WP_URL not set}"
: "${WP_TITLE:?WP_TITLE not set}"
: "${WP_ADMIN_USER:?WP_ADMIN_USER not set}"
: "${WP_ADMIN_PASSWORD:?WP_ADMIN_PASSWORD not set}"
: "${WP_ADMIN_EMAIL:?WP_ADMIN_EMAIL not set}"

echo "==> Waiting for the database to accept connections"
until $WP db check >/dev/null 2>&1; do sleep 2; done

echo "==> Ensuring WordPress core is installed"
if ! $WP core is-installed >/dev/null 2>&1; then
  $WP core install \
    --url="$WP_URL" \
    --title="$WP_TITLE" \
    --admin_user="$WP_ADMIN_USER" \
    --admin_password="$WP_ADMIN_PASSWORD" \
    --admin_email="$WP_ADMIN_EMAIL" \
    --skip-email
else
  echo "    already installed, skipping"
fi

if $WP option get contentbridge_seeded >/dev/null 2>&1; then
  echo "==> contentbridge_seeded option already set. Nothing to do."
  exit 0
fi

echo "==> Activating ContentBridge Fields plugin"
$WP plugin activate contentbridge-fields

echo "==> Enabling pretty permalinks"
$WP rewrite structure '/%postname%/' --hard
# WP-CLI's own rewrite flush does not reliably write real mod_rewrite rules
# inside this container (leaves only empty BEGIN/END markers) — write the
# standard WordPress ruleset ourselves. This is a filesystem fact, not a DB
# row, so no dump could ever have covered it either.
cat > "$WP_PATH/.htaccess" << 'HTACCESS'
# BEGIN WordPress
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
# END WordPress
HTACCESS

if [ -s "$DUMP_FILE" ]; then
  echo "==> Restoring content from content-dump.sql"
  PREFIX=$($WP db prefix)
  # wp core install above creates its own defaults (Hello World post,
  # Uncategorized term, ...) in these same tables. Truncate first so the
  # dump's rows land in a clean table instead of colliding on primary keys.
  $WP db query "SET FOREIGN_KEY_CHECKS=0; \
    TRUNCATE TABLE ${PREFIX}posts; \
    TRUNCATE TABLE ${PREFIX}postmeta; \
    TRUNCATE TABLE ${PREFIX}comments; \
    TRUNCATE TABLE ${PREFIX}commentmeta; \
    TRUNCATE TABLE ${PREFIX}terms; \
    TRUNCATE TABLE ${PREFIX}term_taxonomy; \
    TRUNCATE TABLE ${PREFIX}term_relationships; \
    TRUNCATE TABLE ${PREFIX}termmeta; \
    SET FOREIGN_KEY_CHECKS=1;"
  $WP db import "$DUMP_FILE"

  # show_on_front / page_on_front live in wp_options, which we deliberately
  # don't dump (see dump.sh) — re-derive the front page from the imported
  # content by slug instead of a hardcoded ID.
  HOME_ID=$($WP post list --post_type=page --name=home --field=ID)
  if [ -n "$HOME_ID" ]; then
    $WP option update show_on_front page
    $WP option update page_on_front "$HOME_ID"
  fi
else
  echo "==> No content-dump.sql found yet — skipping content restore."
  echo "    (Build content in wp-admin, then run dump.sh to create one.)"
fi

echo "==> Marking site as seeded"
$WP option add contentbridge_seeded 1 --autoload=no

echo "==> Done. Visit $WP_URL"
