from abc import ABC, abstractmethod

class BaseAnalysis(ABC):
    @abstractmethod
    def analyze(self, data: dict) -> dict:
        """
        Perform analysis on the provided data.
        """
        pass

    @abstractmethod
    def validate_data(self, data: dict) -> bool:
        """
        Validate the input data for analysis.
        """
        pass
