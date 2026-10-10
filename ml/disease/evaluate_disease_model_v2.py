from pathlib import Path
import json
import random

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(
    "data/disease/plantvillage/extracted/raw/color"
)

MODEL_PATH = Path(
    "models/disease/crop_disease_model_v2.keras"
)

CLASS_NAMES_PATH = Path(
    "models/disease/crop_disease_classes_v2.json"
)


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15


# ============================================================
# SUPPORTED CROPS
# ============================================================

SUPPORTED_CROPS = {
    "Apple",
    "Corn_(maize)",
    "Grape",
    "Orange"
}


# ============================================================
# CHECK FILES
# ============================================================

if not MODEL_PATH.exists():
    print("ERROR: Model not found:")
    print(MODEL_PATH)
    raise SystemExit(1)


if not CLASS_NAMES_PATH.exists():
    print("ERROR: Class names file not found:")
    print(CLASS_NAMES_PATH)
    raise SystemExit(1)


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("========================================")
print("LOADING DISEASE MODEL V2")
print("========================================")

model = tf.keras.models.load_model(
    MODEL_PATH
)

with open(
    CLASS_NAMES_PATH,
    "r",
    encoding="utf-8"
) as file:
    class_names = json.load(file)

print("Model loaded.")
print(f"Classes: {len(class_names)}")


# ============================================================
# FIND CLASSES
# ============================================================

all_classes = sorted([
    folder.name
    for folder in DATA_DIR.iterdir()
    if folder.is_dir()
])

classes = [
    name
    for name in all_classes
    if name.split("___")[0] in SUPPORTED_CROPS
]


print()
print("Creating the same test split used during training...")


# ============================================================
# COLLECT TEST FILES
# ============================================================

image_extensions = {
    ".jpg",
    ".jpeg",
    ".JPG",
    ".JPEG"
}

test_records = []


for class_index, class_name in enumerate(classes):

    class_dir = DATA_DIR / class_name

    files = [
        p
        for p in class_dir.iterdir()
        if p.is_file()
        and p.suffix in image_extensions
    ]

    # Same shuffle method as training script
    random.Random(SEED).shuffle(files)

    total = len(files)

    train_end = int(
        total * TRAIN_RATIO
    )

    val_end = (
        train_end
        + int(total * VAL_RATIO)
    )

    test_files = files[val_end:]

    print(
        f"{class_name}: "
        f"test={len(test_files)}"
    )

    for file_path in test_files:

        test_records.append(
            (
                str(file_path),
                class_index
            )
        )


# ============================================================
# IMAGE LOADER
# ============================================================

def load_image(path, label):

    image = tf.io.read_file(path)

    image = tf.image.decode_image(
        image,
        channels=3,
        expand_animations=False
    )

    image = tf.image.resize(
        image,
        IMAGE_SIZE
    )

    image = tf.cast(
        image,
        tf.float32
    )

    # IMPORTANT:
    # Do NOT call MobileNetV2 preprocess_input() here.
    #
    # The trained model already contains:
    #
    # MobileNetV2 preprocess_input()
    #
    # inside the model.

    return image, label


# ============================================================
# CREATE TEST DATASET
# ============================================================

test_paths = [
    path
    for path, label in test_records
]

test_labels = [
    label
    for path, label in test_records
]


test_dataset = tf.data.Dataset.from_tensor_slices(
    (
        test_paths,
        test_labels
    )
)

test_dataset = test_dataset.map(
    load_image,
    num_parallel_calls=tf.data.AUTOTUNE
)

test_dataset = test_dataset.batch(
    BATCH_SIZE
)

test_dataset = test_dataset.prefetch(
    tf.data.AUTOTUNE
)


# ============================================================
# RUN PREDICTIONS
# ============================================================

print()
print("========================================")
print("RUNNING TEST PREDICTIONS")
print("========================================")

predictions = model.predict(
    test_dataset,
    verbose=1
)

predicted_labels = np.argmax(
    predictions,
    axis=1
)

actual_labels = np.array(
    test_labels
)


# ============================================================
# PER-CLASS PERFORMANCE
# ============================================================

print()
print("========================================")
print("PER-CLASS PERFORMANCE")
print("========================================")

report = classification_report(
    actual_labels,
    predicted_labels,
    target_names=class_names,
    digits=4,
    zero_division=0
)

print(report)


# ============================================================
# CONFUSION MATRIX
# ============================================================

matrix = confusion_matrix(
    actual_labels,
    predicted_labels
)


print()
print("========================================")
print("TOP CONFUSIONS")
print("========================================")


confusions = []


for actual_index in range(
    len(class_names)
):

    for predicted_index in range(
        len(class_names)
    ):

        if actual_index == predicted_index:
            continue

        count = matrix[
            actual_index,
            predicted_index
        ]

        if count > 0:

            confusions.append(
                (
                    count,
                    class_names[actual_index],
                    class_names[predicted_index]
                )
            )


confusions.sort(
    reverse=True
)


if confusions:

    for count, actual, predicted in confusions[:20]:

        print(
            f"{actual}"
            f"  -->  "
            f"{predicted}"
            f"  : {count}"
        )

else:

    print("No misclassifications found.")


# ============================================================
# CROP-LEVEL ACCURACY
# ============================================================

print()
print("========================================")
print("CROP-LEVEL ACCURACY")
print("========================================")


correct_crop_predictions = 0


for actual, predicted in zip(
    actual_labels,
    predicted_labels
):

    actual_crop = (
        class_names[actual]
        .split("___")[0]
    )

    predicted_crop = (
        class_names[predicted]
        .split("___")[0]
    )

    if actual_crop == predicted_crop:

        correct_crop_predictions += 1


crop_accuracy = (
    correct_crop_predictions
    / len(actual_labels)
) * 100


print(
    f"Crop-level accuracy: "
    f"{crop_accuracy:.2f}%"
)


# ============================================================
# KNOWN APPLE SCAB IMAGE
# ============================================================

known_filename = (
    "00075aa8-d81a-4184-8541-b692b78d398a___FREC_Scab 3335.JPG"
)


print()
print("========================================")
print("KNOWN APPLE SCAB IMAGE")
print("========================================")


found = False


for path, label in test_records:

    if Path(path).name == known_filename:

        found = True

        actual_class = class_names[label]

        test_index = test_paths.index(path)

        predicted_index = predicted_labels[
            test_index
        ]

        predicted_class = class_names[
            predicted_index
        ]

        confidence = (
            predictions[test_index][
                predicted_index
            ] * 100
        )

        print(
            f"Image: {path}"
        )

        print(
            f"Actual class: {actual_class}"
        )

        print(
            f"Prediction: {predicted_class}"
        )

        print(
            f"Confidence: {confidence:.2f}%"
        )

        break


if not found:

    print(
        "Known Apple Scab image is "
        "not in the test split."
    )


# ============================================================
# FINAL
# ============================================================

print()
print("========================================")
print("EVALUATION COMPLETE")
print("========================================")