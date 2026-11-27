FROM mysql:8.0@sha256:7dcddc01f13bab2f15cde676d44d01f61fc9f99fe7785e86196dfc07d358ae2b

# Set root password
ENV MYSQL_ROOT_PASSWORD=rootpass
ENV MYSQL_DATABASE=shopdb
ENV MYSQL_USER=webapp
ENV MYSQL_PASSWORD=webapp123

# Create database schema and data
COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306
