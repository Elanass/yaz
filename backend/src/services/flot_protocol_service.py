class FLOTProtocolService:
    def assess_eligibility(self, patient):
        # Example logic to assess FLOT eligibility
        if patient.tumor_staging and patient.tumor_staging.stage in ["II", "III"]:
            return {"eligible": True, "reason": "Stage II or III tumor"}
        return {"eligible": False, "reason": "Ineligible tumor stage"}

    def model_impact(self, patient):
        # Example logic to model FLOT's perioperative impact
        return {
            "survival_rate": 0.75,
            "complication_risk": 0.2,
            "confidence": 0.9
        }
