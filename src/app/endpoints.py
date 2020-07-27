from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from .scheduler import event_scheduler

class Home(HTTPEndpoint):
    async def get(self, request):
        return JSONResponse({"foo": "bar"})

    async def post(self, request):
        content = await request.json()
        response = event_scheduler(content)
        return JSONResponse(response)
