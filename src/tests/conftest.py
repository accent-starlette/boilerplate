import pytest
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.config import environ
from starlette.testclient import TestClient
from starlette_auth.tables import User

environ["TESTING"] = "TRUE"

from app.db import db  # noqa isort:skip
from app.main import app  # noqa isort:skip
from app.settings import DATABASE_URL  # noqa isort:skip

LocalSession = scoped_session(sessionmaker())
LocalSession.configure(bind=db.engine)
db_session = LocalSession()


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
    yield db_session
    db.truncate_all()


@pytest.yield_fixture(scope="function", autouse=False)
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=False)
def user():
    data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}

    try:
        return db_session.query(User).query.filter(User.email == data["email"]).one()
    except:
        usr = User(**data)
        usr.set_password("password")
        db_session.add(usr)
        db_session.commit()
        return usr


@pytest.fixture(scope="function", autouse=False)
def login(user, client):
    client.post("/auth/login", data={"email": user.email, "password": "password"})
