#!/usr/bin/env bash
#
# Snapshots the current content tables to content-dump.sql, so whatever you
# just built in wp-admin (a new post, an edited page, a new category, a nav
# change...) becomes reproducible on a fresh volume via seed.sh.
#
# Run after making content changes, then commit the updated .sql file:
#   docker compose exec wordpress bash wp-content/seed/dump.sh
#   git add wordpress/seed/content-dump.sql && git commit -m "..."
#
# Deliberately excludes wp_options and wp_users/wp_usermeta:
#  - wp_options holds environment-specific stuff (site URL, admin email)
#    that must stay driven by env vars, not frozen into a snapshot.
#  - wp_users/wp_usermeta holds the admin account's password hash — that
#    must never end up committed to git, hashed or not.
# It also can't capture .htaccess, because that's a file, not a DB row —
# see the comment in seed.sh.

set -euo pipefail

WP_PATH="/var/www/html"
WP="wp --allow-root --path=$WP_PATH"
DUMP_FILE="$WP_PATH/wp-content/seed/content-dump.sql"
PREFIX=$($WP db prefix)

echo "==> Exporting content tables to content-dump.sql"
$WP db export "$DUMP_FILE" --tables="${PREFIX}posts,${PREFIX}postmeta,${PREFIX}comments,${PREFIX}commentmeta,${PREFIX}terms,${PREFIX}term_taxonomy,${PREFIX}term_relationships,${PREFIX}termmeta"

echo "==> Done: wp-content/seed/content-dump.sql"
