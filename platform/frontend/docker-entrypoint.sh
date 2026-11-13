#!/bin/sh
# Auto-detect TLS certificates and swap nginx config accordingly.
# If /etc/nginx/certs/selfsigned.crt exists, use the SSL config.
# Otherwise, serve HTTP-only (Cloudflare Tunnel or dev mode).

if [ -f /etc/nginx/certs/selfsigned.crt ] && [ -f /etc/nginx/certs/selfsigned.key ]; then
    echo "[entrypoint] TLS certificates found — enabling HTTPS on port 443"
    if [ -f /etc/nginx/conf.d/nginx-ssl.conf ]; then
        cp /etc/nginx/conf.d/nginx-ssl.conf /etc/nginx/conf.d/default.conf
        rm -f /etc/nginx/conf.d/nginx-ssl.conf
    fi
else
    echo "[entrypoint] No TLS certificates — serving HTTP only on port 80"
    rm -f /etc/nginx/conf.d/nginx-ssl.conf
fi

# Allow the app origin to frame a wiki served from a separate hostname. Empty
# keeps the wiki same-origin, the default for single-host installs.
if [ -f /etc/nginx/conf.d/default.conf ]; then
    if [ -n "${WIKI_FRAME_ANCESTOR:-}" ]; then
        sed -i "s|__WIKI_FRAME_ANCESTORS__|${WIKI_FRAME_ANCESTOR}|g" /etc/nginx/conf.d/default.conf
    else
        sed -i "s| __WIKI_FRAME_ANCESTORS__||g" /etc/nginx/conf.d/default.conf
    fi
fi

exec nginx -g 'daemon off;'
