FROM alpine:3.19

# Passive lab capture sidecar.  The platform attaches this container to a lab
# bridge as a second interface (eth1) and mirrors every lab container's veth
# into it with a TC ingress filter.  Students consume the live pcap stream:
#
#   nc <network-tap> 9999 | tcpdump -r - -nn
#
RUN apk add --no-cache tcpdump socat

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 9999
ENTRYPOINT ["/entrypoint.sh"]
