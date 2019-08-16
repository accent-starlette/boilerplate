def test_requires_login(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_logged_in_grants_access(token, client):
    response = client.get("/api/users/me", headers={"Authorization": token})
    assert response.status_code == 200


def test_response(user, token, client):
    response = client.get("/api/users/me", headers={"Authorization": token})
    assert response.json() == {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
    }
