FROM alpine:3.18@sha256:de0eb0b3f2a47ba1eb89389859a9bd88b28e82f5826b6969ad604979713c2d4f

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apk add --no-cache curl

COPY attack-loop.sh /attack-loop.sh
RUN chmod +x /attack-loop.sh

CMD ["/bin/sh", "/attack-loop.sh"]
