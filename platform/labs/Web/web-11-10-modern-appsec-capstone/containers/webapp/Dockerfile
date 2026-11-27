FROM python:3.11-slim@sha256:61e01f72680f86a5279ad510818ab7b2ee9f049822589d4e34e33e044360356c
WORKDIR /app
COPY app.py /app/app.py
RUN pip install --no-cache-dir flask==3.0.3
EXPOSE 80
CMD ["python", "app.py"]
