from pathlib import Path
import json
import random

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/disease/plantvillage/extracted/raw/color")
MODEL_DIR = Path("models/disease")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "crop_disease_model_v2.keras"
CLASS_NAMES_PATH = MODEL_DIR / "crop_disease_classes_v2.json"


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

INITIAL_EPOCHS = 5
FINE_TUNE_EPOCHS = 5


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)


# ============================================================
# SUPPORTED CLASSES
# ============================================================

SUPPORTED_CROPS = {
    "Apple",
    "Corn_(maize)",
    "Grape",
    "Orange"
}


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


print("\n========================================")
print("DISEASE MODEL V2")
print("========================================")

print("\nClasses:")

for i, name in enumerate(classes):
    print(f"{i}: {name}")

print(f"\nTotal classes: {len(classes)}")


# ============================================================
# COLLECT IMAGE FILES
# ============================================================

image_extensions = {
    ".jpg",
    ".jpeg",
    ".JPG",
    ".JPEG"
}


records = []

for class_index, class_name in enumerate(classes):

    class_dir = DATA_DIR / class_name

    files = [
        p for p in class_dir.iterdir()
        if p.is_file() and p.suffix in image_extensions
    ]

    random.Random(SEED).shuffle(files)

    total = len(files)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_files = files[:train_end]
    val_files = files[train_end:val_end]
    test_files = files[val_end:]

    for file_path in train_files:
        records.append(
            (str(file_path), class_index, "train")
        )

    for file_path in val_files:
        records.append(
            (str(file_path), class_index, "validation")
        )

    for file_path in test_files:
        records.append(
            (str(file_path), class_index, "test")
        )

    print(
        f"{class_name}: "
        f"train={len(train_files)}, "
        f"val={len(val_files)}, "
        f"test={len(test_files)}"
    )


# ============================================================
# CREATE DATASETS
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

    return image, label


def create_dataset(split):

    paths = [
        path
        for path, label, current_split in records
        if current_split == split
    ]

    labels = [
        label
        for path, label, current_split in records
        if current_split == split
    ]

    dataset = tf.data.Dataset.from_tensor_slices(
        (paths, labels)
    )

    if split == "train":
        dataset = dataset.shuffle(
            len(paths),
            seed=SEED
        )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=tf.data.AUTOTUNE
    )

    dataset = dataset.batch(
        BATCH_SIZE
    )

    dataset = dataset.prefetch(
        tf.data.AUTOTUNE
    )

    return dataset


train_dataset = create_dataset("train")
validation_dataset = create_dataset("validation")
test_dataset = create_dataset("test")


# ============================================================
# DATA AUGMENTATION
# ============================================================

augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.10),
    layers.RandomContrast(0.10)
])


# ============================================================
# MOBILENETV2
# ============================================================

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False


# ============================================================
# BUILD MODEL
# ============================================================

inputs = keras.Input(
    shape=(224, 224, 3)
)

x = augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(
    x
)

x = base_model(
    x,
    training=False
)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.30)(x)

outputs = layers.Dense(
    len(classes),
    activation="softmax"
)(x)

model = keras.Model(
    inputs,
    outputs
)


# ============================================================
# PHASE 1
# ============================================================

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


print("\n========================================")
print("PHASE 1: TRAINING")
print("========================================")


model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=INITIAL_EPOCHS
)


# ============================================================
# PHASE 2 — FINE TUNING
# ============================================================

print("\n========================================")
print("PHASE 2: FINE-TUNING")
print("========================================")


base_model.trainable = True


for layer in base_model.layers[:-30]:
    layer.trainable = False


for layer in base_model.layers:

    if isinstance(
        layer,
        layers.BatchNormalization
    ):
        layer.trainable = False


model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.00001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


callbacks = [

    keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=2,
        restore_best_weights=True
    ),

    keras.callbacks.ModelCheckpoint(
        MODEL_PATH,
        monitor="val_accuracy",
        save_best_only=True
    )
]


model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=FINE_TUNE_EPOCHS,
    callbacks=callbacks
)


# ============================================================
# LOAD BEST MODEL
# ============================================================

model = keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# FINAL TEST
# ============================================================

print("\n========================================")
print("INDEPENDENT TEST")
print("========================================")


test_loss, test_accuracy = model.evaluate(
    test_dataset,
    verbose=1
)


# ============================================================
# SAVE CLASS NAMES
# ============================================================

with open(
    CLASS_NAMES_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        classes,
        file,
        indent=4
    )


# ============================================================
# RESULTS
# ============================================================

print("\n========================================")
print("MODEL V2 COMPLETE")
print("========================================")

print(
    f"Independent Test Loss: "
    f"{test_loss:.4f}"
)

print(
    f"Independent Test Accuracy: "
    f"{test_accuracy:.4f}"
)

print("\nModel saved:")
print(MODEL_PATH)

print("\nClasses saved:")
print(CLASS_NAMES_PATH)

print("\nSupported crops:")
print("Apple")
print("Maize")
print("Grape")
print("Orange")

print("\nChilli/Mirchi: NOT INCLUDED")