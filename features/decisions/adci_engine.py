from .base_decision_engine import BaseDecisionEngine
import asyncio
from features.protocols.flot_analyzer import FLOTAnalyzer

class ADCIEngine(BaseDecisionEngine):
    def predict(self, patient_data: dict) -> dict:
        """
        Predict outcomes using the ADCI algorithm.
        """
        # Validate input
        if not self.validate_input(patient_data):
            raise ValueError("Invalid input data for ADCI Engine")
        # Base ADCI prediction
        adci_base = {"confidence_score": 0.95, "recommendation": "Proceed with surgery"}
        # Perform FLOT protocol analysis
        flot_analyzer = FLOTAnalyzer()
        flot_result = asyncio.run(
            flot_analyzer.analyze_gastric_surgery_case(patient_data)
        )
        return {
            "adci": adci_base,
            "flot_analysis": flot_result
        }

    def validate_input(self, patient_data: dict) -> bool:
        """
        Validate input data for the ADCI engine.
        """
        # Example validation logic
        required_fields = ["age", "diagnosis", "lab_results"]
        return all(field in patient_data for field in required_fields)
