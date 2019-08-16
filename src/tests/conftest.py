import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.config import environ
from starlette.testclient import TestClient
from starlette_auth.tables import User
from starlette_core.database import Session

environ["TESTING"] = "TRUE"

from app.db import db  # noqa isort:skip
from app.main import app  # noqa isort:skip
from app.settings import DATABASE_URL  # noqa isort:skip


@pytest.fixture(scope="session", autouse=True)
def database():
    url = str(DATABASE_URL)

    if database_exists(url):
        drop_database(url)

    create_database(url)

    db.create_all()

    return db


@pytest.yield_fixture(scope="function", autouse=True)
def session():
    db_session = Session()
    yield db_session
    Session.remove()
    db.truncate_all()


@pytest.yield_fixture(scope="function", autouse=False)
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=False)
def user():
    data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}

    try:
        return User.query.filter(User.email == data["email"]).one()
    except:
        usr = User(**data)
        usr.set_password("password")
        usr.save()
        return usr


@pytest.fixture(scope="function", autouse=False)
def login(user, client):
    client.post("/auth/login", data={"email": user.email, "password": "password"})


@pytest.yield_fixture(scope="function", autouse=False)
def token(user, client):
    response = client.post(
        "/api/token", data={"username": user.email, "password": "password"}
    )
    assert response.status_code == 200
    bearer = response.json()["access_token"]
    return f"Bearer {bearer}"
