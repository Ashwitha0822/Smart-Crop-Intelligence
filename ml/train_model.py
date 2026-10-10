from pathlib import Path
import json
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "Crop_recommendation.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]

TARGETS = [
    "label",
    "crop",
    "Crop",
    "crop_type"
]

if not DATA.exists():
    raise FileNotFoundError(
        f"{DATA} not found. Make sure Crop_recommendation.csv exists in the data folder."
    )

df = pd.read_csv(DATA)

df.columns = [c.strip() for c in df.columns]

target = next(
    (c for c in TARGETS if c in df.columns),
    None
)

if target is None:
    raise ValueError(
        f"Target column not found. Columns: {df.columns.tolist()}\n"
        f"Expected one of {TARGETS}"
    )

missing = [
    c for c in FEATURES
    if c not in df.columns
]

if missing:
    raise ValueError(
        f"Missing feature columns: {missing}"
    )

df = df[FEATURES + [target]].dropna().copy()

for c in FEATURES:
    df[c] = pd.to_numeric(
        df[c],
        errors="coerce"
    )

df = df.dropna()

X = df[FEATURES]
y = df[target].astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

metrics = {
    "rows": int(len(df)),
    "classes": int(y.nunique()),
    "accuracy": float(
        accuracy_score(y_test, pred)
    ),
    "precision_weighted": float(
        precision_score(
            y_test,
            pred,
            average="weighted",
            zero_division=0
        )
    ),
    "recall_weighted": float(
        recall_score(
            y_test,
            pred,
            average="weighted",
            zero_division=0
        )
    ),
    "f1_weighted": float(
        f1_score(
            y_test,
            pred,
            average="weighted",
            zero_division=0
        )
    ),
    "features": FEATURES,
    "target": target,
    "classification_report": classification_report(
        y_test,
        pred,
        output_dict=True,
        zero_division=0
    )
}

joblib.dump(
    {
        "model": model,
        "features": FEATURES
    },
    MODEL_DIR / "crop_model.joblib"
)

(MODEL_DIR / "metrics.json").write_text(
    json.dumps(metrics, indent=2),
    encoding="utf-8"
)

print(
    json.dumps(
        {
            k: v
            for k, v in metrics.items()
            if k != "classification_report"
        },
        indent=2
    )
)

print(
    f"Saved model to "
    f"{MODEL_DIR / 'crop_model.joblib'}"
)