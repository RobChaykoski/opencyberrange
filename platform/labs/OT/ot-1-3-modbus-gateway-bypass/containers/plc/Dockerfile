FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c

WORKDIR /app

RUN pip install --no-cache-dir pymodbus==3.6.9

COPY modbus_server.py .

EXPOSE 502

CMD ["python", "modbus_server.py"]
