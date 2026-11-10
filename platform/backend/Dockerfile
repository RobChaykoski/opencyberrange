FROM python:3.11-slim

ARG PLATFORM_VERSION=2.5.5
ARG BUILD_REVISION=unknown

ENV OCR_BUILD_REVISION=${BUILD_REVISION}

LABEL org.opencontainers.image.title="SWOCTS Cyber Range backend" \
      org.opencontainers.image.description="SWOCTS Cyber Range API and lab orchestration service" \
      org.opencontainers.image.version="${PLATFORM_VERSION}" \
      org.opencontainers.image.revision="${BUILD_REVISION}" \
      org.opencontainers.image.source="https://github.com/RobChaykoski/opencyberrange" \
      org.opencontainers.image.licenses="LicenseRef-PolyForm-Noncommercial-1.0.0"

WORKDIR /app

# Enforce UTC timezone for consistent datetime handling
ENV TZ=UTC

# Install system dependencies including Docker CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for managing lab containers)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin docker-buildx-plugin && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose port
EXPOSE 8000

# Readiness probe: /health checks the database, matching the Compose healthcheck.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Run the application
# Workers auto-scale: (2 × CPU cores) + 1, capped at 9 to leave headroom for lab containers
CMD ["sh", "-c", "CORES=$(nproc); W=$(( (CORES * 2) + 1 )); [ $W -gt 9 ] && W=9; echo \"Starting uvicorn with $W workers ($CORES cores)\"; exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $W"]
