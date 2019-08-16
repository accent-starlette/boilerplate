from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from starlette_auth.tables import User


def test_no_default_user_exists_when_not_called():
    assert User.query.count() == 0


def test_default_test_user_exists_when_called(user):
    assert User.query.count() == 1


def test_user_exists_in_db_for_app(user):
    def create_app():
        app = Starlette()

        @app.route("/count")
        def count(request):
            return JSONResponse({"count": User.query.count()})

        app.add_route("/count", count)

        return app

    with TestClient(create_app()) as client:
        response = client.get("/count")
        assert response.status_code == 200
        assert response.json() == {"count": 1}
