import random
import csv


def determine_status(temperature, vibration, current):
    if temperature >= 48 or vibration >= 0.28 or current >= 5.7:
        return "FAILURE RISK"
    elif temperature >= 45 or vibration >= 0.22 or current >= 5.2:
        return "WARNING"
    else:
        return "NORMAL"


def generate_sample(target_status):
    while True:
        if target_status == "NORMAL":
            temperature = random.uniform(35, 45)
            vibration = random.uniform(0.05, 0.22)
            current = random.uniform(3.0, 5.2)

        elif target_status == "WARNING":
            temperature = random.uniform(40, 48)
            vibration = random.uniform(0.15, 0.28)
            current = random.uniform(4.0, 5.7)

        else:
            temperature = random.uniform(45, 90)
            vibration = random.uniform(0.20, 1.0)
            current = random.uniform(4.5, 12.0)

        temperature = round(temperature, 2)
        vibration = round(vibration, 2)
        current = round(current, 2)

        actual_status = determine_status(
            temperature,
            vibration,
            current
        )

        if actual_status == target_status:
            return temperature, vibration, current, actual_status


output_file = "data/training_data.csv"

statuses = ["NORMAL", "WARNING", "FAILURE RISK"]

with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "temperature",
        "vibration",
        "current",
        "status"
    ])

    for i in range(10000):
        target_status = statuses[i % 3]

        temperature, vibration, current, status = generate_sample(
            target_status
        )

        writer.writerow([
            temperature,
            vibration,
            current,
            status
        ])

print("Balanced training dataset created successfully.")    