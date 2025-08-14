def test_canary(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "")
