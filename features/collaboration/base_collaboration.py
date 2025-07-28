from abc import ABC, abstractmethod

class BaseCollaboration(ABC):
    @abstractmethod
    def add_member(self, team_id: str, member_id: str) -> bool:
        """
        Add a member to a collaboration team.
        """
        pass

    @abstractmethod
    def remove_member(self, team_id: str, member_id: str) -> bool:
        """
        Remove a member from a collaboration team.
        """
        pass

    @abstractmethod
    def get_team_status(self, team_id: str) -> dict:
        """
        Get the current status of a collaboration team.
        """
        pass
