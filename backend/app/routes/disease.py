from pathlib import Path
import json

import numpy as np
import tensorflow as tf
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image


router = APIRouter(
    prefix="/api/disease",
    tags=["Disease Detection"]
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "disease"
    / "crop_disease_model_v2.keras"
)

CLASS_NAMES_PATH = (
    BASE_DIR
    / "models"
    / "disease"
    / "crop_disease_classes_v2.json"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = None
class_names = None


def load_disease_model():

    global model
    global class_names

    if model is None:

        if not MODEL_PATH.exists():
            raise RuntimeError(
                f"Disease model not found: {MODEL_PATH}"
            )

        if not CLASS_NAMES_PATH.exists():
            raise RuntimeError(
                f"Class file not found: {CLASS_NAMES_PATH}"
            )

        model = tf.keras.models.load_model(
            MODEL_PATH
        )

        with open(
            CLASS_NAMES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            class_names = json.load(file)


# ============================================================
# DISEASE PREDICTION
# ============================================================

@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload an image."
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".JPG",
        ".JPEG",
        ".PNG"
    }

    suffix = Path(
        file.filename
    ).suffix

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, and PNG images are supported."
        )

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    try:

        load_disease_model()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    # --------------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------------

    try:

        contents = await file.read()

        image = Image.open(
            __import__("io").BytesIO(contents)
        )

        image = image.convert("RGB")

        image = image.resize(
            (224, 224)
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid image file."
        )

    # --------------------------------------------------------
    # PREPARE IMAGE
    # --------------------------------------------------------

    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    # IMPORTANT:
    # Do NOT call MobileNetV2 preprocess_input()
    # here.
    #
    # The trained model already contains
    # MobileNetV2 preprocessing internally.

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    predictions = model.predict(
        image_array,
        verbose=0
    )[0]

    top_indices = np.argsort(
        predictions
    )[::-1][:3]

    best_index = int(
        top_indices[0]
    )

    best_class = class_names[
        best_index
    ]

    confidence = float(
        predictions[best_index] * 100
    )

    # --------------------------------------------------------
    # SPLIT CROP / DISEASE
    # --------------------------------------------------------

    if "___" in best_class:

        crop, diagnosis = best_class.split(
            "___",
            1
        )

    else:

        crop = "Unknown"
        diagnosis = best_class

    # --------------------------------------------------------
    # TOP 3
    # --------------------------------------------------------

    top3 = []

    for index in top_indices:

        class_name = class_names[
            int(index)
        ]

        probability = float(
            predictions[index] * 100
        )

        if "___" in class_name:

            crop_name, disease_name = (
                class_name.split("___", 1)
            )

        else:

            crop_name = "Unknown"
            disease_name = class_name

        top3.append({
            "crop": crop_name,
            "diagnosis": disease_name,
            "confidence": round(
                probability,
                2
            )
        })

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "success": True,
        "crop": crop,
        "diagnosis": diagnosis,
        "confidence": round(
            confidence,
            2
        ),
        "top3": top3,
        "supported_crops": [
            "Apple",
            "Corn_(maize)",
            "Grape",
            "Orange"
        ],
        "chilli_included": False
    }