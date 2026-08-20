import joblib
import pandas as pd

model = joblib.load("models/random_forest_model.pkl")

sample = pd.DataFrame(
    [[55.0, 0.40, 6.5]],
    columns=["temperature", "vibration", "current"]
)

prediction = model.predict(sample)

print("Prediction:", prediction[0])