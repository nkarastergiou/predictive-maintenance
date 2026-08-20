from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

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

@app.post("/predict")
def predict(data: SensorData):
    sample = pd.DataFrame(
        [[data.temperature, data.vibration, data.current]],
        columns=["temperature", "vibration", "current"]
    )

    prediction = model.predict(sample)[0]

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

    prediction = int(predictive_model.predict(sample)[0])

    probability = float(
        predictive_model.predict_proba(sample)[0][1]
    )

    return {
        "future_failure": prediction,
        "failure_probability": round(probability, 4)
    }    