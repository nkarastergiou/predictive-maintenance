import pandas as pd

data = pd.read_csv("data/predictive_training_data.csv")

print("Dataset shape:")
print(data.shape)

print("\nFuture failure distribution:")
print(data["future_failure"].value_counts())

print("\nFuture failure percentage:")
print(
    data["future_failure"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("\nAverage values by future_failure:")
print(
    data.groupby("future_failure")[
        [
            "temperature",
            "vibration",
            "current",
            "temp_change_10",
            "vibration_change_10",
            "current_change_10"
        ]
    ].mean()
)