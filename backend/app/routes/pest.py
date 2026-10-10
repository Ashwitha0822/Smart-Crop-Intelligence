from pathlib import Path
import io
import json

import numpy as np
from PIL import Image
from fastapi import APIRouter, File, HTTPException, UploadFile
import tensorflow as tf


router = APIRouter(
    prefix="/api/pest",
    tags=["Pest Detection"]
)


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    ROOT
    / "models"
    / "pest"
    / "crop_pest_model.keras"
)

CLASSES_PATH = (
    ROOT
    / "models"
    / "pest"
    / "crop_pest_classes.json"
)


IMG_SIZE = (160, 160)

# Below this confidence, show a warning.
WARNING_THRESHOLD = 70.0


# ============================================================
# LAZY MODEL LOADING
# ============================================================

_model = None
_classes = None


def get_model():

    global _model

    if _model is None:

        if not MODEL_PATH.exists():

            raise HTTPException(
                status_code=500,
                detail=(
                    "Pest model not found. "
                    "Train ml/pest/train_pest_model.py first."
                )
            )

        _model = tf.keras.models.load_model(
            MODEL_PATH
        )

    return _model


def get_classes():

    global _classes

    if _classes is None:

        if not CLASSES_PATH.exists():

            raise HTTPException(
                status_code=500,
                detail="Pest class file not found."
            )

        with open(
            CLASSES_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            _classes = json.load(f)

    return _classes


# ============================================================
# PREDICTION
# ============================================================

@router.post("/predict")
async def predict_pest(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="Please upload an image."
        )

    if not file.content_type.startswith("image/"):

        raise HTTPException(
            status_code=400,
            detail="Only image files are supported."
        )

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    try:

        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded image."
        )

    # --------------------------------------------------------
    # Resize
    # --------------------------------------------------------

    image = image.resize(
        IMG_SIZE
    )

    image_array = np.array(
        image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    # IMPORTANT:
    # The trained model already contains
    # MobileNetV2 preprocess_input().
    # Do NOT preprocess the image again here.

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    model = get_model()
    classes = get_classes()

    predictions = model.predict(
        image_array,
        verbose=0
    )[0]

    top_indices = np.argsort(
        predictions
    )[::-1][:3]

    top3 = []

    for index in top_indices:

        confidence = float(
            predictions[index] * 100
        )

        top3.append(
            {
                "pest": classes[index],
                "confidence": round(
                    confidence,
                    2
                )
            }
        )

    best_index = int(
        top_indices[0]
    )

    pest_name = classes[
        best_index
    ]

    confidence = float(
        predictions[best_index] * 100
    )

    # --------------------------------------------------------
    # Confidence warning
    # --------------------------------------------------------

    if confidence < WARNING_THRESHOLD:

        warning = (
            "Low confidence prediction. "
            "Please verify the pest visually "
            "or consult local agricultural guidance."
        )

    else:

        warning = (
            "Prediction confidence is relatively high, "
            "but visual or agricultural verification is "
            "still recommended."
        )

    return {
        "success": True,
        "pest": pest_name,
        "confidence": round(
            confidence,
            2
        ),
        "top3": top3,
        "supported_pests": classes,
        "confidence_warning": warning,
        "chilli_included": False
    }