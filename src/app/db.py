from starlette_core.database import Database, metadata

from app import settings
from app.ws.data_notify import DataNotify

# setup database url
if settings.DATABASE_URL.driver == "psycopg2":
    engine_kwargs = {"pool_size": 20, "max_overflow": 0}
else:
    engine_kwargs = {}

db = Database(settings.DATABASE_URL, engine_kwargs=engine_kwargs)

# print all running queries to the console
# see https://docs.sqlalchemy.org/en/13/core/engines.html
# db.engine.echo = True

# import project and external tables
from starlette_auth import tables as auth_tables  # noqa isort:skip

# register the models for ws data updates
DataNotify.register_model(auth_tables.Scope)
DataNotify.register_model(auth_tables.User)
