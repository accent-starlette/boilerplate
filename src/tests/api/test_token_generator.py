import time

from app.api.auth.oauth import create_access_token, decode_access_token


def test_token():
    data = {"hello": "world"}

    token = create_access_token(data)
    assert isinstance(token, bytes)

    decoded = decode_access_token(token)
    assert isinstance(decoded, dict)
    assert decoded["hello"] == "world"
    assert decoded["exp"] > int(time.time())
