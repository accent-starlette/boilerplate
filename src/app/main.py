import starlette_admin
import starlette_auth
import starlette_core
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app import admin, db, endpoints, globals, handlers, settings

# config
starlette_admin.config.logout_url = "/auth/logout"
starlette_auth.config.change_pw_template = "starlette_admin/auth/change_password.html"
starlette_auth.config.login_template = "starlette_admin/auth/login.html"
starlette_auth.config.reset_pw_template = "starlette_admin/auth/reset_password.html"
starlette_auth.config.reset_pw_done_template = (
    "starlette_admin/auth/reset_password_done.html"
)
starlette_auth.config.reset_pw_confirm_template = (
    "starlette_admin/auth/reset_password_confirm.html"
)
starlette_auth.config.reset_pw_complete_template = (
    "starlette_admin/auth/reset_password_complete.html"
)
starlette_auth.config.reset_pw_email_subject_template = (
    "starlette_admin/auth/password_reset_subject.txt"
)
starlette_auth.config.reset_pw_email_template = (
    "starlette_admin/auth/password_reset_body.txt"
)
starlette_auth.config.secret_key = settings.SECRET_KEY
starlette_auth.config.templates = globals.templates
starlette_core.config.email_default_from_address = settings.EMAIL_DEFAULT_FROM_ADDRESS
starlette_core.config.email_default_from_name = settings.EMAIL_DEFAULT_FROM_NAME
starlette_core.config.email_host = settings.EMAIL_HOST
starlette_core.config.email_port = settings.EMAIL_PORT
starlette_core.config.email_use_tls = settings.EMAIL_USE_TLS
starlette_core.config.email_username = settings.EMAIL_USERNAME
starlette_core.config.email_password = settings.EMAIL_PASSWORD

# base app
app = Starlette(debug=settings.DEBUG)

# routes
app.add_route("/", endpoints.Home, methods=["GET"], name="home")

# sub apps
app.mount(path="/admin", app=admin.adminsite, name=admin.adminsite.name)
app.mount(path="/auth", app=starlette_auth.app, name="auth")

# static app
app.mount(
    path="/static",
    app=StaticFiles(directory="static", packages=["starlette_admin"]),
    name="static",
)

# middleware
app.add_middleware(AuthenticationMiddleware, backend=starlette_auth.ModelAuthBackend())
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_HOSTS)
app.add_middleware(starlette_core.middleware.DatabaseMiddleware)

# exception handlers
app.add_exception_handler(404, handlers.not_found)
app.add_exception_handler(500, handlers.server_error)

# sentry
if settings.SENTRY_DSN:
    try:
        from sentry_asgi import SentryMiddleware
        import sentry_sdk

        sentry_sdk.init(str(settings.SENTRY_DSN))
        app = SentryMiddleware(app)
    except ImportError:
        pass
