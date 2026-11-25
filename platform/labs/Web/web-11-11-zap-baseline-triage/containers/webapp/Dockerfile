FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir flask==3.0.3 werkzeug==3.0.6

COPY app.py .
COPY files ./files

EXPOSE 80

CMD ["python", "app.py"]
