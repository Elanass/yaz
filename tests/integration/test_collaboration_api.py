import pytest
from fastapi.testclient import TestClient
from api.v1.medical_consolidated import app

client = TestClient(app)

def test_add_member():
    response = client.post("/collaboration/team1/add_member", json={"member_id": "member1"})
    assert response.status_code == 200
    assert response.json()["message"] == "Member added successfully"

def test_remove_member():
    client.post("/collaboration/team1/add_member", json={"member_id": "member1"})
    response = client.post("/collaboration/team1/remove_member", json={"member_id": "member1"})
    assert response.status_code == 200
    assert response.json()["message"] == "Member removed successfully"

def test_get_team_status():
    client.post("/collaboration/team1/add_member", json={"member_id": "member1"})
    response = client.get("/collaboration/team1/status")
    assert response.status_code == 200
    assert response.json() == {"team_id": "team1", "members": ["member1"]}
