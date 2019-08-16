from fastapi import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED


async def get_request_user(request: Request):
    """
    Use to secure endpoints that only require access via logged in users
    using basic sessions.
    """

    user = request.user
    if user and user.is_authenticated and user.is_active:
        return user
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
