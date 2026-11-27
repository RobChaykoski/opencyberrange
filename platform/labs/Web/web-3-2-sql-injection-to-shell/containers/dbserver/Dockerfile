FROM mysql:8.0@sha256:7dcddc01f13bab2f15cde676d44d01f61fc9f99fe7785e86196dfc07d358ae2b

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV MYSQL_ROOT_PASSWORD=r00tV3rt3x_Int3rn4l#
ENV MYSQL_DATABASE=vertex_portal

COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306
