FROM mysql:8.0@sha256:7dcddc01f13bab2f15cde676d44d01f61fc9f99fe7785e86196dfc07d358ae2b

ENV MYSQL_ROOT_PASSWORD=r00tN0v4T3ch_Int3rn4l#
ENV MYSQL_DATABASE=novatech

COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306
