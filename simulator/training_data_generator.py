import random
import csv

def generate_sample(status):
    if status == "NORMAL":
        temperature = random.uniform(35, 48)
        vibration = random.uniform(0.05, 0.22)
        current = random.uniform(3.0, 5.2)

    elif status == "WARNING":
        temperature = random.uniform(45, 65)
        vibration = random.uniform(0.20, 0.60)
        current = random.uniform(5.0, 8.0)

    else:
        temperature = random.uniform(60, 90)
        vibration = random.uniform(0.55, 1.00)
        current = random.uniform(7.5, 12.0)

    return (
        round(temperature, 2),
        round(vibration, 2),
        round(current, 2),
        status
    )

output_file = "data/training_data.csv"

statuses = [
    "NORMAL",
    "WARNING",
    "FAILURE RISK"
]

with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
        "temperature",
        "vibration",
        "current",
        "status"
    ])

    for _ in range(10000):
        status = random.choice(statuses)
        sample = generate_sample(status)
        writer.writerow(sample)

print("Training dataset created successfully.")        