from starlette.applications import Starlette
from starlette.routing import Route

from app import endpoints, settings

routes = [
    Route("/", endpoints.Home, methods=["GET","POST"], name="home"),
]

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
)

if settings.SENTRY_DSN:
    try:
        from sentry_asgi import SentryMiddleware
        import sentry_sdk

        sentry_sdk.init(str(settings.SENTRY_DSN))
        app = SentryMiddleware(app)
    except ImportError:
        pass
