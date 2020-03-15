import starlette_admin
import starlette_auth
import starlette_core
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from app import admin, db, endpoints, globals, handlers, settings

starlette_admin.config.templates = globals.templates
starlette_auth.config.templates = globals.templates

static = StaticFiles(directory="static", packages=["starlette_admin"])

middleware = [
    Middleware(starlette_core.middleware.DatabaseMiddleware),
    Middleware(CORSMiddleware, allow_origins=settings.ALLOWED_HOSTS),
    Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
    Middleware(AuthenticationMiddleware, backend=starlette_auth.ModelAuthBackend()),
]

routes = [
    Route("/", endpoints.Home, methods=["GET"], name="home"),
    Mount("/admin", app=admin.adminsite, name=admin.adminsite.name),
    Mount("/auth", app=starlette_auth.app, name="auth"),
    Mount("/static", app=static, name="static"),
]

app = Starlette(debug=settings.DEBUG, middleware=middleware, routes=routes)

app.add_exception_handler(404, handlers.not_found)
app.add_exception_handler(500, handlers.server_error)

if settings.SENTRY_DSN:
    try:
        from sentry_asgi import SentryMiddleware
        import sentry_sdk

        sentry_sdk.init(str(settings.SENTRY_DSN))
        app = SentryMiddleware(app)
    except ImportError:
        pass
