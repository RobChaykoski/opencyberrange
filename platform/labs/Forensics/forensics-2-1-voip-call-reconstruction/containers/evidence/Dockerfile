FROM nginx:alpine

COPY voip-call.pcap /usr/share/nginx/html/voip-call.pcap
COPY reconstruct.py /usr/share/nginx/html/reconstruct.py
COPY README.txt /usr/share/nginx/html/README.txt

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD wget -q -O /dev/null http://127.0.0.1/README.txt || exit 1

EXPOSE 80
