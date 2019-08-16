from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette_auth.tables import User

from app import settings
from app.api.schemas import TokenData

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def create_access_token(data: dict):
    """ Create an access token using jwt """

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, str(settings.SECRET_KEY), algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """ Decode a jwt to return the original data that was passed in to create it """

    return jwt.decode(token, str(settings.SECRET_KEY), algorithms=[ALGORITHM])


async def get_oauth_user(token: str = Depends(oauth2_scheme)):
    """
    Use to secure endpoints that require jwt auth like mobile or external 
    apps not running internally with this site.
    """

    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except jwt.PyJWTError:
        raise credentials_exception

    user = User.query.filter_by(email=token_data.username).one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception

    return user
