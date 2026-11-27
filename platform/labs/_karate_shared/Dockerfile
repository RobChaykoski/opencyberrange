FROM python:3.12-alpine@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89

WORKDIR /app
COPY app.py /app/app.py

RUN adduser -D -H -u 10001 labuser
USER labuser

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "/app/app.py"]
