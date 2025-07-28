from fastapi import APIRouter, HTTPException
from features.collaboration.team_collaboration import TeamCollaboration

router = APIRouter()
team_collaboration = TeamCollaboration()

@router.post("/collaboration/{team_id}/add_member")
def add_member(team_id: str, member_id: str):
    """
    API endpoint to add a member to a collaboration team.
    """
    success = team_collaboration.add_member(team_id, member_id)
    if not success:
        raise HTTPException(status_code=400, detail="Member already exists in the team")
    return {"message": "Member added successfully"}

@router.post("/collaboration/{team_id}/remove_member")
def remove_member(team_id: str, member_id: str):
    """
    API endpoint to remove a member from a collaboration team.
    """
    success = team_collaboration.remove_member(team_id, member_id)
    if not success:
        raise HTTPException(status_code=400, detail="Member not found in the team")
    return {"message": "Member removed successfully"}

@router.get("/collaboration/{team_id}/status")
def get_team_status(team_id: str):
    """
    API endpoint to get the current status of a collaboration team.
    """
    status = team_collaboration.get_team_status(team_id)
    return status
