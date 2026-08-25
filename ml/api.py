from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

from ml.maintenance_intelligence import assess_machine


app = FastAPI()

model = joblib.load("models/random_forest_model.pkl")
predictive_model = joblib.load("models/predictive_failure_model.pkl")


class SensorData(BaseModel):
    temperature: float
    vibration: float
    current: float


class PredictiveSensorData(BaseModel):
    temperature: float
    vibration: float
    current: float

    temp_change_10: float
    vibration_change_10: float
    current_change_10: float

    temp_avg_10: float
    vibration_avg_10: float
    current_avg_10: float

    current_status: str


@app.post("/predict")
def predict(data: SensorData):

    sample = pd.DataFrame(
        [[
            data.temperature,
            data.vibration,
            data.current
        ]],
        columns=[
            "temperature",
            "vibration",
            "current"
        ]
    )

    prediction = int(model.predict(sample)[0])

    return {
        "prediction": prediction
    }


@app.post("/predict-failure")
def predict_failure(data: PredictiveSensorData):

    sample = pd.DataFrame(
        [[
            data.temperature,
            data.vibration,
            data.current,
            data.temp_change_10,
            data.vibration_change_10,
            data.current_change_10,
            data.temp_avg_10,
            data.vibration_avg_10,
            data.current_avg_10
        ]],
        columns=[
            "temperature",
            "vibration",
            "current",
            "temp_change_10",
            "vibration_change_10",
            "current_change_10",
            "temp_avg_10",
            "vibration_avg_10",
            "current_avg_10"
        ]
    )

    prediction = int(
        predictive_model.predict(sample)[0]
    )

    probability = float(
        predictive_model.predict_proba(sample)[0][1]
    )

    # Convert ML output into an operational predictive state
    if data.current_status == "FAILURE RISK":
        predictive_state = "ALREADY FAILED"

    elif prediction == 1:
        predictive_state = "PREDICTED FAILURE"

    else:
        predictive_state = "NO IMMINENT FAILURE"

    # Maintenance Intelligence layer
    assessment = assess_machine(
        temperature=data.temperature,
        vibration=data.vibration,
        current=data.current,
        current_status=data.current_status,
        predictive_state=predictive_state,
        failure_probability=probability
    )

    return {
        "future_failure": prediction,
        "failure_probability": round(probability, 4),

        "predictive_state": predictive_state,

        "maintenance": {
            "health_score": assessment.health_score,
            "maintenance_priority":
                assessment.maintenance_priority,
            "risk_driver":
                assessment.risk_driver,
            "recommended_action":
                assessment.recommended_action
        }
    }