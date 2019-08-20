def test_home_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "home.html"
    assert "request" in response.context
