def test_can_login(user, client):
    response = client.post(
        "/auth/login", data={"email": user.email, "password": "password"}
    )
    assert response.status_code == 302
    assert response.next.url == "http://testserver/"
