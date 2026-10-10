from pathlib import Path
import json
import sys

import numpy as np
import tensorflow as tf


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path(
    "models/disease/crop_disease_model_v2.keras"
)

CLASS_NAMES_PATH = Path(
    "models/disease/crop_disease_classes_v2.json"
)


# ============================================================
# CHECK INPUT
# ============================================================

if len(sys.argv) < 2:
    print("Usage:")
    print(
        "py -3.14 ml\\disease\\predict_disease.py <image_path>"
    )
    sys.exit(1)


IMAGE_PATH = Path(sys.argv[1])


# ============================================================
# CHECK FILES
# ============================================================

if not IMAGE_PATH.exists():
    print("ERROR: Image not found:")
    print(IMAGE_PATH)
    sys.exit(1)


if not MODEL_PATH.exists():
    print("ERROR: Model not found:")
    print(MODEL_PATH)
    sys.exit(1)


if not CLASS_NAMES_PATH.exists():
    print("ERROR: Class file not found:")
    print(CLASS_NAMES_PATH)
    sys.exit(1)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading disease model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)


with open(
    CLASS_NAMES_PATH,
    "r",
    encoding="utf-8"
) as file:

    class_names = json.load(file)


print("Model loaded successfully.")


# ============================================================
# LOAD IMAGE
# ============================================================

print("Loading image...")


image = tf.keras.utils.load_img(
    IMAGE_PATH,
    target_size=(224, 224)
)


image_array = tf.keras.utils.img_to_array(
    image
)


image_array = np.expand_dims(
    image_array,
    axis=0
)


# IMPORTANT:
# DO NOT call preprocess_input() here.
#
# The trained model already contains:
# MobileNetV2 preprocess_input()
# inside the model itself.


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(
    image_array,
    verbose=0
)[0]


top_indices = np.argsort(
    predictions
)[::-1][:3]


best_index = top_indices[0]

best_class = class_names[
    best_index
]


confidence = (
    predictions[best_index] * 100
)


# ============================================================
# SPLIT CROP AND DISEASE
# ============================================================

if "___" in best_class:

    crop, diagnosis = best_class.split(
        "___",
        1
    )

else:

    crop = "Unknown"
    diagnosis = best_class


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("========================================")
print("DISEASE PREDICTION")
print("========================================")

print(
    f"Crop       : {crop}"
)

print(
    f"Diagnosis  : {diagnosis}"
)

print(
    f"Confidence : {confidence:.2f}%"
)

print()

print("Top 3 Predictions:")


for index in top_indices:

    class_name = class_names[
        index
    ]

    probability = (
        predictions[index] * 100
    )

    print(
        f"{class_name} -> "
        f"{probability:.2f}%"
    )


print("========================================")