from fastapi import APIRouter, HTTPException
from features.decisions.adci_engine import ADCIEngine

router = APIRouter()
adci_engine = ADCIEngine()

@router.post("/adci/predict")
def predict_adci(patient_data: dict):
    """
    API endpoint to predict outcomes using the ADCI engine.
    """
    if not adci_engine.validate_input(patient_data):
        raise HTTPException(status_code=400, detail="Invalid input data")

    prediction = adci_engine.predict(patient_data)
    return prediction
