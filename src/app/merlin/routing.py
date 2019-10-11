from starlette.routing import Route, Router

from .core.endpoints import Page

router = Router(
    [Route("/{page_path:path}", endpoint=Page, methods=["GET"], name="page")]
)
