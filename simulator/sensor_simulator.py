import random
import time
import csv
import os
from datetime import datetime

temperature = 42.0
vibration = 0.15
current = 4.5

csv_file = "data/sensor_data.csv"

if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "temperature", "vibration", "current", "status"])

def determine_status(temperature, vibration, current):
    if temperature >= 48 or vibration >= 0.28 or current >= 5.7:
        return "FAILURE RISK"
    elif temperature >= 45 or vibration >= 0.22 or current >= 5.2:
        return "WARNING"
    else:
        return "NORMAL"

def generate_sensor_data(temperature, vibration, current):
    temperature += random.uniform(-0.3, 0.5)
    vibration += random.uniform(-0.02, 0.03)
    current += random.uniform(-0.1, 0.15)

    temperature = round(temperature, 2)
    vibration = round(vibration, 2)
    current = round(current, 2)

    temperature = max(35, min(temperature, 90))
    vibration = max(0.05, min(vibration, 1.0))
    current = max(3.0, min(current, 12.0))

    return temperature, vibration, current

def save_to_csv(csv_file, timestamp, temperature, vibration, current, status):
    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, temperature, vibration, current, status])


def display_reading(timestamp, temperature, vibration, current, status):
    print(f"Timestamp: {timestamp}")
    print(f"Temperature: {temperature} °C")
    print(f"Vibration: {vibration} g")
    print(f"Current: {current} A")
    print(f"Status: {status}")
    print("--------------------")

while True:
    temperature, vibration, current = generate_sensor_data(
        temperature,
        vibration,
        current
)

    status = determine_status(temperature, vibration, current)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    save_to_csv(
    csv_file,
    timestamp,
    temperature,
    vibration,
    current,
    status
)

    display_reading(
    timestamp,
    temperature,
    vibration,
    current,
    status
)

    time.sleep(2)

