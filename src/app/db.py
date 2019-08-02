from starlette_core.database import Database, metadata

from app.settings import DATABASE_URL

# set db config options
if DATABASE_URL.driver == "psycopg2":
    engine_kwargs = {"pool_size": 20, "max_overflow": 0}
else:
    engine_kwargs = {}

# setup database url
db = Database(DATABASE_URL, engine_kwargs=engine_kwargs)

# print all running queries to the console
# see https://docs.sqlalchemy.org/en/13/core/engines.html
# db.engine.echo = True

# The following will need to be added to your first revision to enable the
# uuid extension. Using this will mean packages that interact with the db
# will not need to worry about setting a default uuid. I have seen cases where
# default=uuid.uuid4 does not work.

# op.execute("create EXTENSION if not EXISTS \"uuid-ossp\"")

# change the id pk's to a postgres uuid type
# from sqlalchemy import Column, text  # noqa isort:skip
# from sqlalchemy.dialects.postgresql import UUID  # noqa isort:skip
# from starlette_core.database import Base  # noqa isort:skip

# Base.id = Column(
#     UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
# )

# import project and external tables
from starlette_auth import tables  # noqa isort:skip
from app.media import tables  # noqa isort:skip
