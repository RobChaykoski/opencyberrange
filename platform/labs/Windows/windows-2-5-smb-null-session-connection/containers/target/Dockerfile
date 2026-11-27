FROM ubuntu:22.04@sha256:b000e69a50ff940390233025e7a337fb8469b509e2334fa4d018ac30f3e18cdb

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y samba && rm -rf /var/lib/apt/lists/*

# Configure Samba with null session support
# Flag embedded in server string - visible during null session enumeration
# NOTE: Do NOT manually define [IPC$] - Samba creates it automatically
RUN echo "[global]" > /etc/samba/smb.conf && \
    echo "workgroup = WORKGROUP" >> /etc/samba/smb.conf && \
    echo "server string = Windows Server - Null Session: OCR{smb_null_c0nn3ct}" >> /etc/samba/smb.conf && \
    echo "security = user" >> /etc/samba/smb.conf && \
    echo "map to guest = Bad User" >> /etc/samba/smb.conf && \
    echo "guest account = nobody" >> /etc/samba/smb.conf

EXPOSE 445

CMD ["smbd", "-F", "--no-process-group"]
