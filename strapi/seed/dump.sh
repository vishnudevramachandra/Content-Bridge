#!/usr/bin/env bash
#
# Thin wrapper around dump-content.js — mirrors the wordpress/seed/dump.sh
# entrypoint style so both sides of the project are invoked the same way:
#   docker compose exec strapi bash seed/dump.sh
#   docker compose exec wordpress bash wp-content/seed/dump.sh

set -euo pipefail

cd /opt/app
node seed/dump-content.js
