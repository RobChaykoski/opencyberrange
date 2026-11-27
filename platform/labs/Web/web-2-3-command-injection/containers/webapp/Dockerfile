FROM ubuntu:22.04@sha256:b000e69a50ff940390233025e7a337fb8469b509e2334fa4d018ac30f3e18cdb

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir flask

RUN mkdir -p /app /opt/cloudping/config

COPY app.py /app/app.py

# Token 1. application config
RUN printf 'cmd\n' > /opt/cloudping/config/token.txt

# Token 2. root flag
RUN printf '1nj3ct3d\n' > /root/flag.txt && chmod 644 /root/flag.txt

WORKDIR /app
EXPOSE 80
CMD ["python3", "app.py"]
