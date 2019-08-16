import starlette_admin
import starlette_auth
import starlette_core
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from app import admin, db, endpoints, globals, handlers, settings
from app.api.main import app as api_app

starlette_admin.config.templates = globals.templates
starlette_auth.config.templates = globals.templates

static = StaticFiles(directory="static", packages=["starlette_admin"])
staticapp = GZipMiddleware(static)

routes = [
    Route("/", endpoints.Home, methods=["GET"], name="home"),
    Mount("/admin", app=admin.adminsite, name=admin.adminsite.name),
    Mount("/api", app=api_app, name="api"),
    Mount("/auth", app=starlette_auth.app, name="auth"),
    Mount("/static", app=staticapp, name="static"),
]

middleware = [
    Middleware(starlette_core.middleware.DatabaseMiddleware),
    Middleware(CORSMiddleware, allow_origins=settings.ALLOWED_HOSTS),
    Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
    Middleware(AuthenticationMiddleware, backend=starlette_auth.ModelAuthBackend()),
]

exception_handlers = {
    404: handlers.not_found,
    500: handlers.server_error,
}

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    middleware=middleware,
    exception_handlers=exception_handlers,  # type: ignore
)

if settings.SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        sentry_sdk.init(str(settings.SENTRY_DSN))
        app.add_middleware(SentryAsgiMiddleware)
    except ImportError:
        pass
