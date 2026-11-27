FROM alpine:3.19@sha256:6baf43584bcb78f2e5847d1de515f23499913ac9f12bdf834811a3145eb11ca1

RUN apk add --no-cache dnsmasq python3

COPY dnsmasq.conf /etc/dnsmasq.conf
COPY index.html /srv/index.html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 53/udp 53/tcp 80

ENTRYPOINT ["/entrypoint.sh"]
