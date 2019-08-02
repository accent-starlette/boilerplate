import starlette_admin
import starlette_auth
import starlette_core
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app import admin, db, endpoints, globals, handlers, settings
from app.media import config as media_config

# config
starlette_admin.config.templates = globals.templates
starlette_auth.config.templates = globals.templates

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

# media app
app.mount(
    path="/media",
    app=StaticFiles(directory=media_config.root_directory, check_dir=False),
    name="media",
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
