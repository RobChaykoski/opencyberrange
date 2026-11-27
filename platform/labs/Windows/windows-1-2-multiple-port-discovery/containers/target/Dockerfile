FROM python:3.12-alpine@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLAG=OCR{mult1pl3_p0rts}

WORKDIR /srv

COPY server.py /srv/server.py

EXPOSE 80 445 3389

CMD ["python", "/srv/server.py"]
