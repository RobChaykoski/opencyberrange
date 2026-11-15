# syntax=docker/dockerfile:1

# Pin the multi-arch index digest so a base-image refresh cannot change the
# build silently; Renovate updates the digest with the tag. OS packages are
# refreshed with apt-get upgrade below because a pinned base still goes stale.
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS build

WORKDIR /app

# Build-only toolchain. The runtime image does not keep gcc or headers. curl and
# gnupg are here only to fetch the Docker apt key for the runtime stage.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    libxml2-dev \
    libxslt1-dev \
    libxmlsec1-dev \
    libssl-dev \
    curl \
    gnupg && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg \
        | gpg --dearmor -o /keyrings/docker-archive-keyring.gpg

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

ARG PLATFORM_VERSION=4
ARG BUILD_REVISION=unknown

ENV OCR_BUILD_REVISION=${BUILD_REVISION}
ENV TZ=UTC
# Bind-mounted development trees are read-only to the non-root runtime user.
ENV PYTHONDONTWRITEBYTECODE=1

LABEL org.opencontainers.image.title="SWOCTS Cyber Range backend" \
      org.opencontainers.image.description="SWOCTS Cyber Range API and lab orchestration service" \
      org.opencontainers.image.version="${PLATFORM_VERSION}" \
      org.opencontainers.image.revision="${BUILD_REVISION}" \
      org.opencontainers.image.source="https://github.com/RobChaykoski/opencyberrange" \
      org.opencontainers.image.licenses="LicenseRef-PolyForm-Noncommercial-1.0.0"

WORKDIR /app

# Runtime-only packages. postgresql-client provides pg_dump/pg_restore for
# backups. There is deliberately no curl or GPG toolchain in the runtime image:
# the Docker apt key is downloaded in the build stage. Application code uses
# the Python requests client, and the healthcheck uses the image's Python.
#
# apt-get upgrade refreshes the Debian point release: the base digest is pinned
# for reproducibility, but security updates that landed after that digest still
# need to be pulled in at build time.
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    libxml2 \
    libxslt1.1 \
    libxmlsec1 \
    libxmlsec1-openssl && \
    rm -rf /var/lib/apt/lists/*

# Docker CLI for lab orchestration. The backend talks to a socket proxy over
# DOCKER_HOST; it does not need the host socket mounted into the container.
COPY --from=build /keyrings/docker-archive-keyring.gpg /usr/share/keyrings/docker-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin docker-buildx-plugin && \
    rm -rf /var/lib/apt/lists/*

# Python wheels built in the build stage.
COPY --from=build /install /usr/local

# The application never installs packages at runtime, so pip, setuptools, and
# wheel are removed from the shipped image. This also removes their bundled
# dependencies (for example jaraco-context) from the vulnerability surface.
RUN python -m pip uninstall -y pip setuptools wheel && \
    rm -rf /usr/local/lib/python3.13/site-packages/pip* \
           /usr/local/lib/python3.13/site-packages/setuptools* \
           /usr/local/lib/python3.13/site-packages/wheel* \
           /usr/local/lib/python3.13/site-packages/pkg_resources

COPY . /app/

# Non-root runtime user. Named volumes created from these directories inherit
# the ownership, so /app/backups and /workbook stay writable after a mount.
# The recursive chmod also makes every copied source file readable by the
# runtime user: a host umask of 027 can leave new files mode 640, which the
# image would otherwise preserve as root-owned and unreadable to UID 10001.
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin ocr && \
    mkdir -p /app/backups /workbook && \
    chown -R ocr:ocr /app/backups /workbook && \
    chmod -R a+rX /app

USER ocr

EXPOSE 8000

# Single worker is the supported production shape: shared rate-limit storage,
# scheduler leader election, and pool sizing are all documented against it.
# Scale out by setting OCR_UVICORN_WORKERS explicitly and raising
# DB_POOL_SIZE/DB_MAX_OVERFLOW so (pool + overflow) x workers stays below
# PostgreSQL max_connections.
#
# nginx is the only client of this port. Trust its X-Forwarded-For/Proto so
# request.client.host is the real learner address: otherwise every login,
# registration, and forgot-username limit shares one global bucket and every
# audit row records the proxy address. Only private bridge ranges are trusted,
# so a client cannot spoof the header by reaching the backend directly.
CMD ["sh", "-c", "W=${OCR_UVICORN_WORKERS:-1}; echo \"Starting uvicorn with $W worker(s)\"; exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $W --proxy-headers --forwarded-allow-ips \"${FORWARDED_ALLOW_IPS:-127.0.0.1,172.16.0.0/12}\""]
