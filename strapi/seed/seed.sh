#!/usr/bin/env bash
#
# Bootstraps a fresh Strapi volume into the ContentBridge demo state.
#
# Two different kinds of state, two different mechanisms (same split as
# wordpress/seed/seed.sh):
#  - The admin account is environment-specific (its own email/password from
#    .env) and created directly via `strapi admin:create-user`, every time —
#    idempotent because that command itself errors out if the email already
#    exists, which we treat as a no-op rather than a failure.
#  - Actual catalog content (Products, Certifications, Standards) is
#    restored from catalog-seed.json via seed-content.js, which is itself
#    idempotent via a Core Store flag (contentbridge_catalog_seeded) — the
#    direct analog of WordPress's contentbridge_seeded wp_options row.
#
# Runs automatically via the `strapi-seed` one-shot service in
# docker-compose.yml. Safe to re-run manually too.

set -euo pipefail

APP_DIR="/opt/app"
cd "$APP_DIR"

: "${STRAPI_ADMIN_EMAIL:?STRAPI_ADMIN_EMAIL not set}"
: "${STRAPI_ADMIN_PASSWORD:?STRAPI_ADMIN_PASSWORD not set}"

echo "==> Ensuring Strapi admin account exists"
set +e
CREATE_OUTPUT=$(npx strapi admin:create-user \
  -e "$STRAPI_ADMIN_EMAIL" \
  -p "$STRAPI_ADMIN_PASSWORD" \
  -f Admin -l User 2>&1)
CREATE_EXIT=$?
set -e
echo "$CREATE_OUTPUT"
if [ $CREATE_EXIT -ne 0 ] && ! echo "$CREATE_OUTPUT" | grep -q "already exists"; then
  echo "==> Failed to create admin account (see output above)."
  exit 1
fi

echo "==> Seeding catalog content"
node seed/seed-content.js

echo "==> Done."
