import json

from jinja2.utils import generate_lorem_ipsum
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import StreamingResponse

from app.globals import templates
from app.merlin.core.tables import PageManager


class Page(HTTPEndpoint):
    def get_page(self, page_path: str):
        try:
            return PageManager.from_slug_parts(page_path.split("/"))
        except:
            raise HTTPException(404)

    async def get(self, request):
        page_path = request.path_params["page_path"]
        page = self.get_page(page_path)

        if request.headers.get("content-type") == "application/x-ndjson":
            return await self.ndjson(request, page)

        template = "page.html"
        context = {"request": request, "page": page}
        return templates.TemplateResponse(template, context)

    def as_ndjson(self, attr, contents):
        data = {"data_attr": attr, "contents": contents}
        return f"{json.dumps(data)}\n"

    async def get_stream(self, request, page):
        yield self.as_ndjson("title", page.title)
        yield self.as_ndjson("main-content", generate_lorem_ipsum(2))
        yield self.as_ndjson("author", "Stuart George")

        ancestors = ""
        for p in page.ancestors:
            url = request.url_for("merlin:page", page_path=p.url)
            li = f"<li><a data-fetch href='{url}'>{p.title}</a></li>"
            ancestors = ancestors + li

        yield self.as_ndjson("ancestors", ancestors)

    async def ndjson(self, request, page):
        stream = self.get_stream(request, page)
        return StreamingResponse(stream, media_type="application/x-ndjson")
 