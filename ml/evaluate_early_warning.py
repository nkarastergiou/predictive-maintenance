import pandas as pd
import joblib
import numpy as np

DATA_PATH = "data/predictive_training_data.csv"
MODEL_PATH = "models/predictive_failure_model.pkl"

data = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)

features = [
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

# Same chronological 80/20 split used during training
split_index = int(len(data) * 0.8)

test_data = data.iloc[split_index:].reset_index(drop=True)

X_test = test_data[features]
y_test = test_data["future_failure"]

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

test_data["prediction"] = predictions
test_data["failure_probability"] = probabilities


# Find continuous future_failure=1 windows.
# Each window represents the period leading up to an upcoming failure.
failure_windows = []

in_window = False
start_index = None

for i, value in enumerate(y_test):
    if value == 1 and not in_window:
        start_index = i
        in_window = True

    elif value == 0 and in_window:
        end_index = i - 1

        failure_windows.append(
            (start_index, end_index)
        )

        in_window = False

# Handle a window that reaches the end of the dataset
if in_window:
    failure_windows.append(
        (start_index, len(y_test) - 1)
    )


lead_times = []
missed_failures = 0

for start, end in failure_windows:
    window_predictions = predictions[start:end + 1]

    positive_indices = np.where(
        window_predictions == 1
    )[0]

    if len(positive_indices) == 0:
        missed_failures += 1
        continue

    first_warning_position = positive_indices[0]

    # Number of readings remaining before the failure
    lead_time = (end - start) - first_warning_position + 1

    lead_times.append(lead_time)


print("===================================")
print("Early Warning Evaluation")
print("===================================")

print(f"\nFailure episodes: {len(failure_windows)}")
print(f"Detected episodes: {len(lead_times)}")
print(f"Missed episodes: {missed_failures}")

if len(failure_windows) > 0:
    detection_rate = (
        len(lead_times) / len(failure_windows)
    ) * 100

    print(
        f"Episode detection rate: "
        f"{detection_rate:.2f}%"
    )

if lead_times:
    print(
        f"\nAverage early warning: "
        f"{np.mean(lead_times):.2f} readings"
    )

    print(
        f"Median early warning: "
        f"{np.median(lead_times):.2f} readings"
    )

    print(
        f"Minimum early warning: "
        f"{np.min(lead_times)} readings"
    )

    print(
        f"Maximum early warning: "
        f"{np.max(lead_times)} readings"
    )

    print(
        f"\nWarnings >= 20 readings early: "
        f"{sum(x >= 20 for x in lead_times)}"
    )

    print(
        f"Warnings >= 10 readings early: "
        f"{sum(x >= 10 for x in lead_times)}"
    )


print("\nExample predictions:")
print(
    test_data[
        [
            "temperature",
            "vibration",
            "current",
            "future_failure",
            "prediction",
            "failure_probability"
        ]
    ].head(20)
)