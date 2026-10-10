import joblib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "crop_model.joblib"

data = joblib.load(MODEL_PATH)

model = data["model"]
features = data["features"]

sample = [[
    90,      # N
    42,      # P
    43,      # K
    25.5,    # temperature
    80.0,    # humidity
    6.5,     # pH
    200.0    # rainfall
]]

prediction = model.predict(sample)

print("Features used:")
print(features)

print("\nInput values:")
print(sample[0])

print("\nRecommended Crop:")
print(prediction[0])