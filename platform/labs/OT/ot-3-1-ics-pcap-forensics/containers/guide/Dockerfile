FROM nginx:alpine
COPY site/ /usr/share/nginx/html/
# The build context comes from a umask-protected checkout; nginx runs as an
# unprivileged user and must be able to read every page.
RUN chmod -R a+rX /usr/share/nginx/html
