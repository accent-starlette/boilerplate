FROM        python:3.7-alpine as base

RUN         set -ex \
            && apk update \
            && apk add --no-cache \
                jpeg-dev \
                libmagic \
                libpq \
                make \
                zlib-dev

# install package requirements into a copy of the base image
# this will include a butt load of cache

FROM        base as builder

ARG         REQUIREMENTS_FILE=/requirements/base.txt

RUN         mkdir /install

WORKDIR     /install

COPY        requirements /requirements

RUN         set -ex \
            && apk update \
            && apk add --no-cache --virtual .build-deps \
                gcc \
                git \
                libc-dev \
                linux-headers \
                musl-dev \
                postgresql-dev \
            && PYTHONUSERBASE=/install pip install --user --no-warn-script-location -r $REQUIREMENTS_FILE \
            && apk del .build-deps

# get a fresh copy of the base image and copy in packages without all the cache

FROM        base

COPY        --from=builder /install /usr/local

COPY        ./src /app

COPY        prestart.sh /prestart.sh
COPY        start.sh /start.sh
COPY        start-reload.sh /start-reload.sh
COPY        gunicorn_conf.py /gunicorn_conf.py

WORKDIR     /app

# Django configuration:

ENV         PYTHONUNBUFFERED=1 \
            PYTHONPATH=/app \
            ALLOWED_HOSTS="*" \
            DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/appdb \
            SECRET_KEY="***** change me *****" \
            EMAIL_HOST=mail \
            EMAIL_PORT=1025 \
            EMAIL_DEFAULT_FROM_ADDRESS=mail@example.com \
            EMAIL_DEFAULT_FROM_NAME=Mail

# Entry:

EXPOSE      80

ENTRYPOINT  ["/prestart.sh"]

CMD         ["/start.sh"]
