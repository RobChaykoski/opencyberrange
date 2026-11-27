FROM python:3.12-alpine@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89

WORKDIR /srv

COPY index.html /srv/index.html

EXPOSE 80

CMD ["python3", "-m", "http.server", "80", "--bind", "0.0.0.0"]
