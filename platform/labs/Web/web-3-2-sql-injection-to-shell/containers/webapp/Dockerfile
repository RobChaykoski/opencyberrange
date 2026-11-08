FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# PyMySQL is MIT-licensed. Do not swap it for mysqlclient, which links the
# GPL-2.0 MySQL client library.
RUN pip3 install --no-cache-dir flask pymysql

# ── Application ──────────────────────────────────────────────────────
RUN mkdir -p /app
COPY app.py /app/app.py

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
