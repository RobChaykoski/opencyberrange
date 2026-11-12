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

# A dead tap looks like "the capture is empty" from inside a lab, which is
# easily mistaken for a slow beacon or a filter mistake.  Probe the listener
# instead of the capture stream so the check costs no packets.
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD netstat -ltn 2>/dev/null | grep -q ':9999' || exit 1

ENTRYPOINT ["/entrypoint.sh"]
