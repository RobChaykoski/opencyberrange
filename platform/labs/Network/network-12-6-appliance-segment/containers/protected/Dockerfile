# Pinned serving base. The flag is copied into the image so its mode does not
# depend on the host umask (a 027 umask otherwise leaves it unreadable by the
# nginx worker).
FROM nginx:1.29-alpine@sha256:5616878291a2eed594aee8db4dade5878cf7edcb475e59193904b198d9b830de

COPY --chmod=0444 flag /usr/share/nginx/html/flag
COPY --chmod=0755 entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
