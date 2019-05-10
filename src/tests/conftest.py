import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.config import environ

environ["TESTING"] = "TRUE"

from app import db, settings  # noqa isort:skip
from starlette_auth.tables import User  # noqa isort:skip
from starlette_core.database import Session  # noqa isort:skip


@pytest.fixture(scope="session", autouse=True)
def database():
    url = str(settings.DATABASE_URL)

    if database_exists(url):
        drop_database(url)

    create_database(url)

    db.db.drop_all()
    db.db.create_all()

    # create a default test user
    user = User(email="test@example.com", first_name="Test", last_name="User")
    user.set_password("password")
    user.save()

    return db


@pytest.yield_fixture(scope="function", autouse=True)
def session():
    db_session = Session()
    db_session.begin_nested()

    yield db_session

    db_session.rollback()
