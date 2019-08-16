def test_can_get_oauth_token(user, client):
    response = client.post(
        "/api/token", data={"username": user.email, "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_invalid_oauth_credentials(user, client):
    response = client.post(
        "/api/token", data={"username": user.email, "password": "password1"}
    )
    assert response.status_code == 401
