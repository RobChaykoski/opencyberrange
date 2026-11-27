FROM ubuntu:22.04@sha256:b000e69a50ff940390233025e7a337fb8469b509e2334fa4d018ac30f3e18cdb

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
RUN apt-get update && apt-get install -y xrdp openssh-server && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/run/sshd
RUN useradd -m -s /bin/bash rdpuser && echo "rdpuser:password123" | chpasswd
RUN echo "OCR{rdp_v3rs10n}" > /home/rdpuser/flag.txt
EXPOSE 3389
CMD service ssh start && service xrdp start && tail -f /dev/null
