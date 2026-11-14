FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (using lock file for reproducible builds)
RUN npm ci

# Copy source files
COPY . .

# Optional separate origin for the wiki. Empty keeps the wiki same-origin.
ARG WIKI_BASE_URL=""
ENV VITE_WIKI_BASE_URL=${WIKI_BASE_URL}

# Build the application
RUN npm run build

# Production stage - serve with nginx.
# Pin the multi-arch index digest so a base-image refresh cannot change the
# runtime silently. Renovate updates the digest with the tag.
FROM nginx:alpine@sha256:713fc2ebfd92e8217db451477182ee91944b123d2b1ee9fd5a8c6e91ca6c3a11

ARG PLATFORM_VERSION=4
ARG BUILD_REVISION=unknown

LABEL org.opencontainers.image.title="SWOCTS Cyber Range frontend" \
      org.opencontainers.image.description="SWOCTS Cyber Range web interface" \
      org.opencontainers.image.version="${PLATFORM_VERSION}" \
      org.opencontainers.image.revision="${BUILD_REVISION}" \
      org.opencontainers.image.source="https://github.com/RobChaykoski/opencyberrange" \
      org.opencontainers.image.licenses="LicenseRef-PolyForm-Noncommercial-1.0.0"

# Used by the compose healthcheck; nginx:alpine does not guarantee curl across
# base-image updates.
RUN apk add --no-cache curl

# CyberChef is a static, client-side tool. Serve the pinned release from the
# same origin so the tool panel works on an isolated range with no internet
# access and without widening the SPA's frame policy to a third-party origin.
# The release asset name is content-hashed; keep the version, asset name, and
# SHA256 in step when upgrading.
ARG CYBERCHEF_VERSION=11.5.0
ARG CYBERCHEF_ZIP_NAME=CyberChef_8cd426dd4f40f1423912d5fad91b578a86a65112.zip
ARG CYBERCHEF_ZIP_SHA256=f6478925d3eaa16ec08626a85f5b85eed10d531a5e18700615fed7ecb024cccf

RUN set -eux; \
    apk add --no-cache unzip; \
    curl -fsSL --retry 3 -o /tmp/cyberchef.zip \
        "https://github.com/gchq/CyberChef/releases/download/v${CYBERCHEF_VERSION}/${CYBERCHEF_ZIP_NAME}"; \
    echo "${CYBERCHEF_ZIP_SHA256}  /tmp/cyberchef.zip" | sha256sum -c -; \
    mkdir -p /usr/share/nginx/html/tools/cyberchef; \
    unzip -q /tmp/cyberchef.zip -d /usr/share/nginx/html/tools/cyberchef; \
    mv "/usr/share/nginx/html/tools/cyberchef/CyberChef_v${CYBERCHEF_VERSION}.html" \
        /usr/share/nginx/html/tools/cyberchef/index.html; \
    find /usr/share/nginx/html/tools/cyberchef -name '*.br' -delete; \
    find /usr/share/nginx/html/tools/cyberchef -name '*.gz' -delete; \
    find /usr/share/nginx/html/tools/cyberchef -name '*.map' -delete; \
    rm -f /tmp/cyberchef.zip; \
    apk del unzip

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy pre-built wiki and download binaries if they exist in the build context.
# On a fresh clone without wiki/ or binaries/, the build creates empty placeholder
# dirs via the .dockerignore-safe pattern below. If the dirs exist, their contents
# are copied into the image.
# Wiki content is a single namespaced tree: wiki/range/<slug>/, wiki/course/<slug>/,
# and wiki/index.html. One COPY bakes it all in. The [i] glob keeps the build from
# failing on a fresh clone without the wiki/ dir.
# The workbook wiki lives in the wiki_data volume built by the wiki-builder
# service. Keep only a placeholder here so nginx has a file to serve before the
# first build.
RUN mkdir -p /usr/share/nginx/wiki /usr/share/nginx/downloads && \
    printf '%s\n' '<!doctype html><title>Workbook wiki</title><p>The workbook wiki has not been built yet. Run scripts/build-wiki.sh.</p>' > /usr/share/nginx/wiki/index.html
COPY binaries/ /usr/share/nginx/downloads/

# Copy nginx configuration (HTTP default + SSL variant)
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-ssl.conf /etc/nginx/conf.d/nginx-ssl.conf
COPY security-headers.conf /etc/nginx/snippets/security-headers.conf
COPY lti-embed-headers.conf /etc/nginx/snippets/lti-embed-headers.conf
COPY cyberchef-headers.conf /etc/nginx/snippets/cyberchef-headers.conf
COPY kasm-headers.conf /etc/nginx/snippets/kasm-headers.conf

# Entrypoint auto-detects TLS certs and swaps config
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=5 \
    CMD curl -fsS -o /dev/null http://127.0.0.1/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]

