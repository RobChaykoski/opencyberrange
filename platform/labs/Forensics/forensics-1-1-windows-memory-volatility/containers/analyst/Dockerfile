FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    curl \
    ca-certificates \
    p7zip-full \
    xz-utils \
    python3 \
    python3-pip \
    procps \
    less \
    && rm -rf /var/lib/apt/lists/*

# Volatility 3 and its Python dependencies. The `vol` console script is
# installed in /usr/local/bin and is available to every account.
RUN pip3 install --no-cache-dir volatility3==2.28.2 pycryptodome

# Analyst account. The password is intentionally simple for a training
# container and is documented in the lab metadata.
RUN useradd -m -s /bin/bash analyst && \
    echo 'analyst:M3m0ry_4n4lys1s' | chpasswd && \
    usermod -aG sudo analyst && \
    printf 'analyst ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/90-analyst && \
    chmod 0440 /etc/sudoers.d/90-analyst

# Symbol table for the Windows Server 2008 SP1 x86 kernel.
#
# The converted Volatility JSON is generated here, at image-build time, from
# the public Microsoft symbol server. It is deliberately not committed to the
# repository: Microsoft's symbol terms do not grant redistribution rights.
# Building this image means the operator accepts those terms. If you publish a
# prebuilt image, review Microsoft's symbol terms first.
RUN PDB_CONV=$(python3 -c "import os, volatility3; print(os.path.join(os.path.dirname(volatility3.__file__), 'framework', 'symbols', 'windows', 'pdbconv.py'))") && \
    mkdir -p /home/analyst/symbols/windows/ntkrpamp.pdb && \
    python3 "$PDB_CONV" \
        -g 37D328E3BAE5460F8E662756ED80951D2 \
        -p ntkrpamp.pdb \
        -o /home/analyst/symbols/windows/ntkrpamp.pdb/37D328E3BAE5460F8E662756ED80951D-2.json && \
    xz -9 /home/analyst/symbols/windows/ntkrpamp.pdb/37D328E3BAE5460F8E662756ED80951D-2.json

# Download the training memory image, verify its published MD5, and unpack it.
# The image is approximately 512 MB after extraction.
RUN mkdir -p /home/analyst/evidence && \
    curl -fsSL --retry 3 -o /tmp/memdump.7z \
      https://samsclass.info/121/proj/memdump.7z && \
    echo "364fed484bcdd1a1f81a3538a4b1cd9a  /tmp/memdump.7z" | md5sum -c - && \
    7z x -y -o/home/analyst/evidence /tmp/memdump.7z >/dev/null && \
    rm -f /tmp/memdump.7z && \
    test -f /home/analyst/evidence/memdump.mem && \
    chown -R analyst:analyst /home/analyst/evidence /home/analyst/symbols

COPY case_brief.txt /home/analyst/evidence/case_brief.txt
RUN chown analyst:analyst /home/analyst/evidence/case_brief.txt

RUN mkdir -p /run/sshd
COPY start.sh /start.sh
RUN chmod +x /start.sh

USER analyst

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD bash -c '</dev/tcp/127.0.0.1/22' || exit 1

CMD ["sudo", "/start.sh"]
