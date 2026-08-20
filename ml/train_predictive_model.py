import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
import joblib
import os

data = pd.read_csv("data/predictive_training_data.csv")

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

X = data[features]
y = data["future_failure"]

split_index = int(len(data) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\nTraining target distribution:")
print(y_train.value_counts())

print("\nTesting target distribution:")
print(y_test.value_counts())

print("\nTraining predictive model...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print(f"\nAccuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, predictions))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nFeature Importance:")

importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print(importance)

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/predictive_failure_model.pkl"
)

print("\nPredictive model saved to:")
print("models/predictive_failure_model.pkl")