from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

from ml.maintenance_intelligence import assess_machine

import psycopg2
import os


app = FastAPI()

model = joblib.load("models/random_forest_model.pkl")
predictive_model = joblib.load("models/predictive_failure_model.pkl")

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "predictive_maintenance",
    "user": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD")
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

class MaintenanceActionRequest(BaseModel):
    machine_id: str

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

    prediction = str(model.predict(sample)[0])

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

@app.post("/maintenance/start")
def start_maintenance(data: MaintenanceActionRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE maintenance_actions
            SET
                status = 'IN PROGRESS',
                started_at = CURRENT_TIMESTAMP
            WHERE id = (
                SELECT id
                FROM maintenance_actions
                WHERE machine_id = %s
                  AND status = 'OPEN'
                ORDER BY created_at DESC
                LIMIT 1
            )
            RETURNING id;
            """,
            (data.machine_id,)
        )

        result = cursor.fetchone()

        if result is None:
            conn.rollback()
            raise HTTPException(
                status_code=404,
                detail="No OPEN maintenance action found for this machine"
            )

        conn.commit()

        return {
            "message": "Maintenance started",
            "action_id": result[0],
            "machine_id": data.machine_id,
            "status": "IN PROGRESS"
        }

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()


@app.post("/maintenance/complete")
def complete_maintenance(data: MaintenanceActionRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE maintenance_actions
            SET
                status = 'COMPLETED',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = (
                SELECT id
                FROM maintenance_actions
                WHERE machine_id = %s
                  AND status = 'IN PROGRESS'
                ORDER BY created_at DESC
                LIMIT 1
            )
            RETURNING id;
            """,
            (data.machine_id,)
        )

        result = cursor.fetchone()

        if result is None:
            conn.rollback()
            raise HTTPException(
                status_code=404,
                detail="No IN PROGRESS maintenance action found for this machine"
            )

        conn.commit()

        return {
            "message": "Maintenance completed",
            "action_id": result[0],
            "machine_id": data.machine_id,
            "status": "COMPLETED"
        }

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()

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

@app.get("/maintenance/active")
def get_active_maintenance():

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                machine_id,
                priority,
                risk_driver,
                recommended_action,
                health_score,
                failure_probability,
                status,
                created_at,
                started_at
            FROM maintenance_actions
            WHERE status IN ('OPEN', 'IN PROGRESS')
            ORDER BY
                CASE priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    ELSE 3
                END,
                created_at DESC;
            """
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "machine_id": row[1],
                "priority": row[2],
                "risk_driver": row[3],
                "recommended_action": row[4],
                "health_score": row[5],
                "failure_probability": row[6],
                "status": row[7],
                "created_at": row[8],
                "started_at": row[9]
            }
            for row in rows
        ]

    finally:
        cursor.close()
        conn.close() 

@app.get("/maintenance/history")
def get_maintenance_history(limit: int = 50):

    if limit < 1 or limit > 500:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 500"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                machine_id,
                priority,
                status,
                created_at,
                started_at,
                completed_at
            FROM maintenance_actions
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "machine_id": row[1],
                "priority": row[2],
                "status": row[3],
                "created_at": row[4],
                "started_at": row[5],
                "completed_at": row[6]
            }
            for row in rows
        ]

    finally:
        cursor.close()
        conn.close()           