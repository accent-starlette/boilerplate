from starlette_core.database import Database, metadata

from app import settings


# setup database url
db = Database(str(settings.DATABASE_URL))

# import project and external tables
from starlette_auth import tables
