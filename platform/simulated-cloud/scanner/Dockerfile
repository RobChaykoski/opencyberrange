FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir \
    boto3==1.35.36 \
    PyYAML==6.0.2 \
    requests==2.32.3

COPY scan.py /app/scan.py

ENTRYPOINT ["python", "/app/scan.py"]
