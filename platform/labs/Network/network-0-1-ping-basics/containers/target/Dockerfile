FROM python:3.12-alpine

WORKDIR /srv

COPY index.html /srv/index.html

EXPOSE 80

CMD ["python3", "-m", "http.server", "80", "--bind", "0.0.0.0"]
