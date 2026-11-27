FROM ubuntu:22.04@sha256:b000e69a50ff940390233025e7a337fb8469b509e2334fa4d018ac30f3e18cdb

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    python3 \
    python3-pip \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Install scapy for PCAP generation
RUN pip3 install --no-cache-dir scapy

# Create SSH directory
RUN mkdir -p /var/run/sshd

# Create analyst user
RUN useradd -m -s /bin/bash analyst && \
    echo "analyst:MediCare2024#" | chpasswd

# Create captures directory
RUN mkdir -p /home/analyst/captures && \
    chown analyst:analyst /home/analyst/captures

# Copy PCAP generation script
COPY generate_smtp_pcap.py /tmp/generate_smtp_pcap.py

# Generate the PCAP file
RUN python3 /tmp/generate_smtp_pcap.py /home/analyst/captures/email-exfiltration.pcap && \
    chown analyst:analyst /home/analyst/captures/email-exfiltration.pcap

# Configure SSH
RUN echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

# Create flag file
RUN echo "OCR{smtp_d4t4_3xf1ltr4t10n}" > /root/flag.txt


CMD ["/usr/sbin/sshd", "-D", "-e"]
