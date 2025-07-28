from .base_collaboration import BaseCollaboration

class TeamCollaboration(BaseCollaboration):
    def __init__(self):
        self.teams = {}

    def add_member(self, team_id: str, member_id: str) -> bool:
        """
        Add a member to a collaboration team.
        """
        if team_id not in self.teams:
            self.teams[team_id] = []
        if member_id not in self.teams[team_id]:
            self.teams[team_id].append(member_id)
            return True
        return False

    def remove_member(self, team_id: str, member_id: str) -> bool:
        """
        Remove a member from a collaboration team.
        """
        if team_id in self.teams and member_id in self.teams[team_id]:
            self.teams[team_id].remove(member_id)
            return True
        return False

    def get_team_status(self, team_id: str) -> dict:
        """
        Get the current status of a collaboration team.
        """
        if team_id in self.teams:
            return {"team_id": team_id, "members": self.teams[team_id]}
        return {"team_id": team_id, "members": []}
