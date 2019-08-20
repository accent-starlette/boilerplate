from starlette.testclient import TestClient

from app import handlers, main, settings


def test_404(client):
    response = client.get("/invalid-url")
    assert response.status_code == 404
    assert response.template.name == "404.html"
    assert "request" in response.context


def test_500():
    # ensure the exception is not raised in the test
    # so that the handler runs as expected
    client = TestClient(main.app, raise_server_exceptions=False)
    client.app.debug = False

    async def force_error(request):
        raise RuntimeError()

    client.app.add_route("/force-error", force_error)

    response = client.get("/force-error")
    assert response.status_code == 500
    assert response.template.name == "500.html"
    assert "request" in response.context

    # re-enable debug
    client.app.debug = True
