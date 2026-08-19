import pandas as pd

data = pd.read_csv("data/training_data.csv")

print("Dataset shape:")
print(data.shape)

print("\nClass distribution:")
print(data["status"].value_counts())

print("\nBasic statistics:")
print(data.describe())

print("\nAverage values per status:")
print(
    data.groupby("status")[
        ["temperature", "vibration", "current"]
    ].mean()
)