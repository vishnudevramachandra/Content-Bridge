FROM wordpress:6.7-php8.3-apache

# `wp db export/import/query` shell out to the mysql/mysqldump binaries —
# not bundled in the base image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Bake WP-CLI into the image itself (not the /var/www/html volume) so it
# survives `docker compose down` + `up` without needing a manual reinstall.
RUN curl -sSL https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar -o /usr/local/bin/wp \
    && chmod +x /usr/local/bin/wp \
    && wp --allow-root --info
