from starlette_core.database import Database, metadata

from app import settings

# setup database url
db = Database(settings.DATABASE_URL, engine_kwargs={"pool_size": 20, "max_overflow": 0})

# print all running queries to the console
# see https://docs.sqlalchemy.org/en/13/core/engines.html
# db.engine.echo = True

# import project and external tables
from starlette_auth import tables  # noqa isort:skip
