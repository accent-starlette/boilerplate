FROM        accent/starlette-docker:3.7-alpine

ARG         REQUIREMENTS_FILE=/requirements/base.txt

RUN         apk add supervisor

ENV         APP_MODULE=app.main:app \
            ALLOWED_HOSTS="*" \
            DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/appdb \
            SECRET_KEY="***** change me *****" \
            EMAIL_HOST=mail \
            EMAIL_PORT=1025 \
            EMAIL_DEFAULT_FROM_ADDRESS=mail@example.com \
            EMAIL_DEFAULT_FROM_NAME=Mail

COPY        supervisord.conf /supervisord.conf
COPY        supervisord.dev.conf /supervisord.dev.conf

EXPOSE      81

CMD         ["supervisord", "-n", "-c", "/supervisord.conf"]
