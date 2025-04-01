#!/bin/sh

echo "shared_preload_libraries = 'pg_cron'" >> /var/lib/postgresql/data/data1/postgresql.conf
echo "cron.database_name='${POSTGRES_DATABASE:-postgres}'" >> /var/lib/postgresql/data/data1/postgresql.conf

# Required to load pg_cron
pg_ctl restart
