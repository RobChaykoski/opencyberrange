FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py /app/app.py

# The target is dependency-free and runs unprivileged. Compose makes the root
# filesystem read-only and mounts a small tmpfs for the command-injection flag.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

USER 10001
EXPOSE 8080

CMD ["python", "/app/app.py"]
