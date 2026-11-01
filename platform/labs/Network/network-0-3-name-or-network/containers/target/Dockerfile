FROM alpine:3.19

RUN apk add --no-cache dnsmasq python3

COPY dnsmasq.conf /etc/dnsmasq.conf
COPY index.html /srv/index.html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 53/udp 53/tcp 80

ENTRYPOINT ["/entrypoint.sh"]
