#! /usr/bin/env sh
set -e

cd /app; python app/wait_for_db.py;
cd /app; alembic upgrade head;

exec "$@"