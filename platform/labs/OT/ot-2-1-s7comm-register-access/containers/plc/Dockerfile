FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c

ENV DEBIAN_FRONTEND=noninteractive

# python-snap7 bundles the Snap7 shared library for manylinux, so the Debian
# runtime needs no compiler or extra system package.
RUN pip install --no-cache-dir python-snap7==1.3

WORKDIR /app
COPY s7_server.py .

EXPOSE 102
CMD ["python", "s7_server.py"]
