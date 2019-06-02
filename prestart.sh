#! /usr/bin/env sh
set -e

while ! psql $DATABASE_URL -c "SELECT version();" > /dev/null 2>&1; do
    echo 'Waiting for connection with db...'
    sleep 1;
done;
echo 'Connected to db...';

cd /app; alembic upgrade head;

exec "$@"