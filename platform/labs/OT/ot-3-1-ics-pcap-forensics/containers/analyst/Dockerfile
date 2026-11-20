FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Tshark is the analysis tool. It is installed without the setuid dumpcap
# helper: students read captures, they do not capture live traffic.
RUN echo "wireshark-common wireshark-common/install-setuid boolean false" | debconf-set-selections && \
    apt-get update && apt-get install -y --no-install-recommends \
      openssh-server \
      sudo \
      tshark \
      tcpdump \
      python3 \
      python3-pip \
      iproute2 \
      net-tools \
      less \
      nano \
      jq \
      curl \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Analyst account. The password is a training fixture documented in lab.yaml.
RUN useradd -m -s /bin/bash analyst && \
    echo 'analyst:P4ck3t_4n4lys1s' | chpasswd && \
    usermod -aG sudo analyst && \
    printf 'analyst ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/90-analyst && \
    chmod 0440 /etc/sudoers.d/90-analyst

# Evidence and the case brief. The paths match the commands in the guide.
COPY data/ /home/analyst/data/
COPY case_brief.txt CHALLENGES.md /home/analyst/
RUN chown -R analyst:analyst /home/analyst && mkdir -p /run/sshd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
