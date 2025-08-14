from apps.surge.core.modules.decision_engine import DecisionEngine


class AIService:
    def __init__(self) -> None:
        self.decision_engine = DecisionEngine()

    def assess_patient_risk(self, patient_data):
        return self.decision_engine.assess_risk(patient_data)

    def get_recommendations(self, patient_data):
        return self.decision_engine.provide_recommendations(patient_data)

    def predict_patient_outcome(self, patient_data):
        return self.decision_engine.predict_outcome(patient_data)

    def generate_patient_alerts(self, patient_data):
        return self.decision_engine.generate_alerts(patient_data)
