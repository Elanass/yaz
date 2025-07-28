from abc import ABC, abstractmethod

class BaseDecisionEngine(ABC):
    @abstractmethod
    def predict(self, patient_data: dict) -> dict:
        """
        Predict outcomes based on patient data.
        """
        pass

    @abstractmethod
    def validate_input(self, patient_data: dict) -> bool:
        """
        Validate input data for the decision engine.
        """
        pass
