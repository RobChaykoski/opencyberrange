FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
RUN apt-get update && apt-get install -y mysql-server && rm -rf /var/lib/apt/lists/*

# Configure MySQL for remote access and file reading (override loaded after mysqld.cnf).
# Enumeration exercises open many aborted connections (mysql-enum, repeated
# client attempts), so raise the host-block threshold well above the default
# 100.  With the default, MySQL returns error 1129 for the student's IP and the
# lab looks broken until the host cache is flushed.
RUN printf '[mysqld]\nbind-address = 0.0.0.0\nsecure-file-priv =\nmax_connect_errors = 1000000\nskip_name_resolve = ON\ndefault-authentication-plugin = mysql_native_password\n' > /etc/mysql/mysql.conf.d/zzz-override.cnf

# Create remote user and seed flag database
RUN service mysql start && sleep 2 && \
    mysql -e "CREATE USER 'sa'@'%' IDENTIFIED WITH mysql_native_password BY 'password'; GRANT ALL PRIVILEGES ON *.* TO 'sa'@'%'; FLUSH PRIVILEGES;" && \
    mysql -e "CREATE DATABASE target_db; USE target_db; CREATE TABLE secrets (id INT AUTO_INCREMENT PRIMARY KEY, content TEXT); INSERT INTO secrets (content) VALUES ('OCR{mssql_v3rs10n}');" && \
    service mysql stop

RUN printf '%s' "OCR{mssql_v3rs10n}" > /tmp/flag.txt && chmod 644 /tmp/flag.txt
EXPOSE 3306
CMD service mysql start && tail -f /dev/null
