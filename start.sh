#! /usr/bin/env sh
set -e

export APP_MODULE=app.main:app

DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}

# Start Gunicorn
exec gunicorn -k uvicorn.workers.UvicornWorker -c "$GUNICORN_CONF" "$APP_MODULE"