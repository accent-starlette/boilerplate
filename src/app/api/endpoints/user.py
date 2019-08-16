from fastapi import Depends
from starlette_auth.tables import User
from starlette_core.database import Session

from app.api import schemas
from app.api.auth import get_oauth_user
from app.api.main import app


@app.get("/users/me", response_model=schemas.User)
async def read_user_me(current_user: User = Depends(get_oauth_user)):
    return current_user
