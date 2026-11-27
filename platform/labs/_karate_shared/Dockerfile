FROM python:3.12-alpine

WORKDIR /app
COPY app.py /app/app.py

RUN adduser -D -H -u 10001 labuser
USER labuser

ENV PORT=8080
EXPOSE 8080
CMD ["python3", "/app/app.py"]
