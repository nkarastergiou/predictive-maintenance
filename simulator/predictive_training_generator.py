import random
import csv
import os

TOTAL_READINGS = 100000
LOOKBACK = 10
PREDICTION_HORIZON = 30

output_file = "data/predictive_training_data.csv"

os.makedirs(os.path.dirname(output_file), exist_ok=True)


def determine_status(temperature, vibration, current):
    if temperature >= 48 or vibration >= 0.28 or current >= 5.7:
        return "FAILURE RISK"
    elif temperature >= 45 or vibration >= 0.22 or current >= 5.2:
        return "WARNING"
    else:
        return "NORMAL"


def reset_machine():
    return {
        "temperature": random.uniform(39.0, 42.0),
        "vibration": random.uniform(0.08, 0.15),
        "current": random.uniform(4.0, 4.6)
    }


def degrade_machine(machine):
    machine["temperature"] += random.uniform(-0.08, 0.18)
    machine["vibration"] += random.uniform(-0.004, 0.008)
    machine["current"] += random.uniform(-0.03, 0.07)

    machine["temperature"] = max(35, min(machine["temperature"], 90))
    machine["vibration"] = max(0.05, min(machine["vibration"], 1.0))
    machine["current"] = max(3.0, min(machine["current"], 12.0))

    return machine

readings = []

machine = reset_machine()

for i in range(TOTAL_READINGS):
    machine = degrade_machine(machine)

    temperature = round(machine["temperature"], 2)
    vibration = round(machine["vibration"], 3)
    current = round(machine["current"], 2)

    status = determine_status(
        temperature,
        vibration,
        current
    )

    readings.append({
        "temperature": temperature,
        "vibration": vibration,
        "current": current,
        "status": status
    })

    if status == "FAILURE RISK":
        machine = reset_machine()

rows = []

for i in range(LOOKBACK, len(readings) - PREDICTION_HORIZON):
    current_reading = readings[i]

    past_readings = readings[i - LOOKBACK:i]

    future_readings = readings[
        i + 1:i + 1 + PREDICTION_HORIZON
    ]

    temp_values = [r["temperature"] for r in past_readings]
    vibration_values = [r["vibration"] for r in past_readings]
    current_values = [r["current"] for r in past_readings]

    temp_avg_10 = sum(temp_values) / LOOKBACK
    vibration_avg_10 = sum(vibration_values) / LOOKBACK
    current_avg_10 = sum(current_values) / LOOKBACK

    temp_change_10 = (
        current_reading["temperature"] - temp_values[0]
    )

    vibration_change_10 = (
        current_reading["vibration"] - vibration_values[0]
    )

    current_change_10 = (
        current_reading["current"] - current_values[0]
    )

    future_failure = int(
        any(
            r["status"] == "FAILURE RISK"
            for r in future_readings
        )
    )

    rows.append([
        current_reading["temperature"],
        current_reading["vibration"],
        current_reading["current"],
        round(temp_change_10, 3),
        round(vibration_change_10, 4),
        round(current_change_10, 3),
        round(temp_avg_10, 3),
        round(vibration_avg_10, 4),
        round(current_avg_10, 3),
        future_failure
    ])

with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "temperature",
        "vibration",
        "current",
        "temp_change_10",
        "vibration_change_10",
        "current_change_10",
        "temp_avg_10",
        "vibration_avg_10",
        "current_avg_10",
        "future_failure"
    ])

    writer.writerows(rows)

print(f"Predictive dataset created: {len(rows)} rows")            