FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py /app/app.py

# The target is deliberately small and dependency-free. Run it unprivileged
# and read-only; the compose file drops every capability as well.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

USER 10001
EXPOSE 8080
CMD ["python", "/app/app.py"]
