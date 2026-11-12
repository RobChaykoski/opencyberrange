# syntax=docker/dockerfile:1

FROM python:3.11-slim AS build

WORKDIR /app

# Build-only toolchain. The runtime image does not keep gcc or headers.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim

ARG PLATFORM_VERSION=3
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

# Runtime-only packages. curl and gnupg are used only to add the Docker apt
# repository; postgresql-client provides pg_dump/pg_restore for backups.
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client curl gnupg && \
    rm -rf /var/lib/apt/lists/*

# Docker CLI for lab orchestration. The backend talks to a socket proxy over
# DOCKER_HOST; it does not need the host socket mounted into the container.
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin docker-buildx-plugin && \
    rm -rf /var/lib/apt/lists/*

# Python wheels built in the build stage.
COPY --from=build /install /usr/local

COPY . /app/

# Non-root runtime user. Named volumes created from these directories inherit
# the ownership, so /app/backups and /workbook stay writable after a mount.
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin ocr && \
    mkdir -p /app/backups /workbook && \
    chown -R ocr:ocr /app/backups /workbook

USER ocr

EXPOSE 8000

# Single worker is the supported production shape: shared rate-limit storage,
# scheduler leader election, and pool sizing are all documented against it.
# Scale out by setting OCR_UVICORN_WORKERS explicitly and raising
# DB_POOL_SIZE/DB_MAX_OVERFLOW so (pool + overflow) x workers stays below
# PostgreSQL max_connections.
CMD ["sh", "-c", "W=${OCR_UVICORN_WORKERS:-1}; echo \"Starting uvicorn with $W worker(s)\"; exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $W"]
