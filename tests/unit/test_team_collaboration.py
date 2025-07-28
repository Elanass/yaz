import pytest
from features.collaboration.team_collaboration import TeamCollaboration

@pytest.fixture
def team_collaboration():
    return TeamCollaboration()

def test_add_member(team_collaboration):
    assert team_collaboration.add_member("team1", "member1") is True
    assert team_collaboration.add_member("team1", "member1") is False  # Duplicate member

def test_remove_member(team_collaboration):
    team_collaboration.add_member("team1", "member1")
    assert team_collaboration.remove_member("team1", "member1") is True
    assert team_collaboration.remove_member("team1", "member1") is False  # Member not found

def test_get_team_status(team_collaboration):
    team_collaboration.add_member("team1", "member1")
    status = team_collaboration.get_team_status("team1")
    assert status == {"team_id": "team1", "members": ["member1"]}
