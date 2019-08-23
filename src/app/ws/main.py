from starlette.applications import Starlette

from . import data_notify

app = Starlette()
app.add_websocket_route("/data", data_notify.DataSocket)
