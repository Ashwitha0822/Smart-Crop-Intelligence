from pathlib import Path
import json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path("data/disease/plantvillage/extracted/raw/color")
MODEL_DIR = Path("models/disease")

MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "crop_disease_model_finetuned.keras"
CLASS_NAMES_PATH = MODEL_DIR / "crop_disease_classes.json"


# ============================================================
# SETTINGS
# ============================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 64
SEED = 42

INITIAL_EPOCHS = 3
FINE_TUNE_EPOCHS = 5


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

print("\nSupported disease classes:")

for i, name in enumerate(classes):
    print(f"{i}: {name}")

print(f"\nTotal classes: {len(classes)}")


# ============================================================
# LOAD TRAINING DATA
# ============================================================

train_dataset = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    labels="inferred",
    label_mode="int",
    class_names=classes,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    validation_split=0.20,
    subset="training",
    seed=SEED,
    shuffle=True
)


# ============================================================
# LOAD VALIDATION DATA
# ============================================================

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    labels="inferred",
    label_mode="int",
    class_names=classes,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    validation_split=0.20,
    subset="validation",
    seed=SEED,
    shuffle=False
)


# ============================================================
# DATA PIPELINE
# ============================================================

AUTOTUNE = tf.data.AUTOTUNE

train_dataset = train_dataset.prefetch(AUTOTUNE)
validation_dataset = validation_dataset.prefetch(AUTOTUNE)


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
# PRETRAINED MOBILENETV2
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

x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

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
# FIRST TRAINING PHASE
# ============================================================

model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=0.001
    ),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


print("\n========================================")
print("PHASE 1: TRAINING CLASSIFIER")
print("========================================")


model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=INITIAL_EPOCHS
)


# ============================================================
# FINE-TUNING
# ============================================================

print("\n========================================")
print("PHASE 2: FINE-TUNING MOBILENETV2")
print("========================================")


base_model.trainable = True


# Freeze the earlier layers.
# Only the later layers will be fine-tuned.

for layer in base_model.layers[:-30]:
    layer.trainable = False


# Keep BatchNormalization layers frozen.
for layer in base_model.layers:
    if isinstance(layer, layers.BatchNormalization):
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
# FINAL EVALUATION
# ============================================================

loss, accuracy = model.evaluate(
    validation_dataset,
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
print("FINE-TUNED MODEL COMPLETE")
print("========================================")

print(f"Validation Loss: {loss:.4f}")
print(f"Validation Accuracy: {accuracy:.4f}")

print("\nModel saved to:")
print(MODEL_PATH)

print("\nClasses saved to:")
print(CLASS_NAMES_PATH)

print("\nSupported crops:")
print("Apple")
print("Maize")
print("Grape")
print("Orange")

print("\nChilli/Mirchi: NOT INCLUDED")