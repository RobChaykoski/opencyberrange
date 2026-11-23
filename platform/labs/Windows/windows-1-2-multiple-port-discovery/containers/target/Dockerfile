FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLAG=OCR{mult1pl3_p0rts}

WORKDIR /srv

COPY server.py /srv/server.py

EXPOSE 80 445 3389

CMD ["python", "/srv/server.py"]
