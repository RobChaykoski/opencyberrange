FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN pip install --no-cache-dir flask

COPY app.py /app/app.py

WORKDIR /app

EXPOSE 80

CMD ["python3", "app.py"]
