import random
import time
import csv
import os
from datetime import datetime
import paho.mqtt.client as mqtt
import sys

MACHINE_ID = sys.argv[1] if len(sys.argv) > 1 else "machine01"

VALID_MACHINES = ["machine01", "machine02", "machine03"]

if MACHINE_ID not in VALID_MACHINES:
    print(f"Invalid machine ID: {MACHINE_ID}")
    print("Valid options: machine01, machine02, machine03")
    sys.exit(1)

MACHINE_PROFILES = {
    "machine01": {
        "temperature_start": 42.0,
        "vibration_start": 0.15,
        "current_start": 4.5,
        "temp_drift": (-0.3, 0.5),
        "vibration_drift": (-0.02, 0.03),
        "current_drift": (-0.1, 0.15),
    },

    "machine02": {
        "temperature_start": 40.0,
        "vibration_start": 0.20,
        "current_start": 4.8,
        "temp_drift": (-0.2, 0.6),
        "vibration_drift": (-0.01, 0.04),
        "current_drift": (-0.08, 0.18),
    },

    "machine03": {
        "temperature_start": 44.0,
        "vibration_start": 0.12,
        "current_start": 4.2,
        "temp_drift": (-0.1, 0.7),
        "vibration_drift": (-0.015, 0.05),
        "current_drift": (-0.05, 0.20),
    }
}

profile = MACHINE_PROFILES.get(
    MACHINE_ID,
    MACHINE_PROFILES["machine01"]
)

temperature = profile["temperature_start"]
vibration = profile["vibration_start"]
current = profile["current_start"]

failure_duration = 0
machine_failed = False

csv_file = "data/sensor_data.csv"

os.makedirs(os.path.dirname(csv_file), exist_ok=True)

if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp","machine_id", "temperature", "vibration", "current", "status"])

def determine_status(temperature, vibration, current):
    if temperature >= 48 or vibration >= 0.28 or current >= 5.7:
        return "FAILURE RISK"
    elif temperature >= 45 or vibration >= 0.22 or current >= 5.2:
        return "WARNING"
    else:
        return "NORMAL"

def generate_sensor_data(temperature, vibration, current):
    temperature += random.uniform(*profile["temp_drift"])
    vibration += random.uniform(*profile["vibration_drift"])
    current += random.uniform(*profile["current_drift"])

    temperature = round(temperature, 2)
    vibration = round(vibration, 2)
    current = round(current, 2)

    temperature = max(35, min(temperature, 90))
    vibration = max(0.05, min(vibration, 1.0))
    current = max(3.0, min(current, 12.0))

    return temperature, vibration, current

def save_to_csv(csv_file, timestamp, machine_id, temperature, vibration, current, status):
    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp,machine_id, temperature, vibration, current, status])


def display_reading(timestamp, machine_id, temperature, vibration, current, status):
    print(f"Timestamp: {timestamp}")
    print(f"Machine ID: {machine_id}")
    print(f"Temperature: {temperature} °C")
    print(f"Vibration: {vibration} g")
    print(f"Current: {current} A")
    print(f"Status: {status}")
    print("--------------------")

mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883, 60)

while True:
    temperature, vibration, current = generate_sensor_data(
        temperature,
        vibration,
        current
)

    if machine_failed:
        status = "FAILURE RISK"
    else:
        status = determine_status(temperature, vibration, current)

        if status == "FAILURE RISK":
            machine_failed = True
    
    if status == "FAILURE RISK":
        failure_duration += 1
    else:
        failure_duration = 0

    if failure_duration >= 10:
        print("Maintenance performed - machine reset")
        print("--------------------")

        mqtt_client.publish(
            f"factory/{MACHINE_ID}/maintenance",
            "RESET"
        )

        temperature = profile["temperature_start"]
        vibration = profile["vibration_start"]
        current = profile["current_start"]

        failure_duration = 0
        machine_failed = False

        mqtt_client.publish(
            f"factory/{MACHINE_ID}/temperature",
            temperature
        )

        mqtt_client.publish(
            f"factory/{MACHINE_ID}/vibration",
            vibration
        )

        mqtt_client.publish(
            f"factory/{MACHINE_ID}/current",
            current
        )

        mqtt_client.publish(
            f"factory/{MACHINE_ID}/status",
            "NORMAL"
        )

        time.sleep(1)
        continue


    mqtt_client.publish(
    f"factory/{MACHINE_ID}/temperature",
    temperature
)

    mqtt_client.publish(
    f"factory/{MACHINE_ID}/vibration",
    vibration
)

    mqtt_client.publish(
    f"factory/{MACHINE_ID}/current",
    current
)

    mqtt_client.publish(
    f"factory/{MACHINE_ID}/status",
    status
)
    

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    save_to_csv(
    csv_file,
    timestamp,
    MACHINE_ID,
    temperature,
    vibration,
    current,
    status
)

    display_reading(
    timestamp,
    MACHINE_ID,
    temperature,
    vibration,
    current,
    status
)

    time.sleep(1)

