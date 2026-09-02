FROM node:20-bookworm-slim

# better-sqlite3 (DATABASE_CLIENT=sqlite) ships prebuilt binaries for common
# platforms, but falls back to compiling from source via node-gyp if none
# match — python3/make/g++ make that fallback work instead of failing.
# curl is for the compose healthcheck (debian-slim doesn't include it).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 make g++ curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

# Install dependencies from just the lockfile inputs first, so this layer
# (the slow one) is only rebuilt when package.json/package-lock.json change —
# not on every content-type/schema edit.
COPY package.json package-lock.json ./
RUN npm ci

# Then copy the rest of the app: config, src (content-types, controllers,
# etc), database migrations, public assets.
COPY . .

EXPOSE 1337

# Watch mode: picks up schema.json / controller / service edits (bind-mounted
# in via docker-compose) with a server restart, no image rebuild needed.
CMD ["npm", "run", "develop"]
