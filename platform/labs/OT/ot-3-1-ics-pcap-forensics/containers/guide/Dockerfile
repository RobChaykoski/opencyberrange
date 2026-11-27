FROM nginx:alpine@sha256:7fc0fb4af7bf006aeb31aea88069976060f8f0a0a86b667126742cc17f4e31ae
COPY site/ /usr/share/nginx/html/
# The build context comes from a umask-protected checkout; nginx runs as an
# unprivileged user and must be able to read every page.
RUN chmod -R a+rX /usr/share/nginx/html
