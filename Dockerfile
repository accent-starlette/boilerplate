FROM        accent/starlette-docker:3.7-alpine

ARG         REQUIREMENTS_FILE=/requirements/base.txt

ENV         APP_MODULE=app.main:app \
            ALLOWED_HOSTS="*" \
            DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/appdb \
            SECRET_KEY="***** change me *****" \
            EMAIL_HOST=mail \
            EMAIL_PORT=1025 \
            EMAIL_DEFAULT_FROM_ADDRESS=mail@example.com \
            EMAIL_DEFAULT_FROM_NAME=Mail
