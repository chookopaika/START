FROM postgres:14

COPY ./init.sql /docker-entrypoint-initdb.d/

RUN mkdir -p /oracle/pg_data/archive/
RUN chown postgres:postgres /oracle/pg_data/archive/

ENTRYPOINT [ "bash", "-c","\
cat <<EOF > /etc/postgresql/14/main/postgresql.conf \n\
licten_address = '*' \n\
port = 22 \n\
archive_mode = on  \n\
archive_command = 'cp %p /oracle/pg_data/archive/%f' \n\
max_wal_senders = 10 \n\
wal_level = replica  \n\
wal_log_hints = on \n\
log_replication_commands = on \n\
EOF \n\
cat <<EOF > /etc/postgresql/14/main/pg_hba.conf \n\
host replication db_repl_user <ip> cspram-sha-256 \n\
"]