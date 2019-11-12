FROM        accent/starlette-docker:3.7-alpine

ARG         REQUIREMENTS_FILE=/requirements/base.txt

ENV         APP_MODULE=app.main:app \
            ALLOWED_HOSTS="*" \
            DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/appdb \
            SECRET_KEY="***** change me *****" \
            EMAIL_HOST=mail \
            EMAIL_PORT=1025 \
            EMAIL_DEFAULT_FROM_ADDRESS=mail@example.com \
            EMAIL_DEFAULT_FROM_NAME=Mail \
            CHANGE_PW_TEMPLATE="starlette_admin/auth/change_password.html" \
            LOGIN_TEMPLATE="starlette_admin/auth/login.html" \
            RESET_PW_TEMPLATE="starlette_admin/auth/reset_password.html" \
            RESET_PW_DONE_TEMPLATE="starlette_admin/auth/reset_password_done.html" \
            RESET_PW_CONFIRM_TEMPLATE="starlette_admin/auth/reset_password_confirm.html" \
            RESET_PW_COMPLETE_TEMPLATE="starlette_admin/auth/reset_password_complete.html" \
            RESET_PW_EMAIL_SUBJECT_TEMPLATE="starlette_admin/auth/password_reset_subject.txt" \
            RESET_PW_EMAIL_TEMPLATE="starlette_admin/auth/password_reset_body.txt"
