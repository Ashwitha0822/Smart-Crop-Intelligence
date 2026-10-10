import os

# ============================================================
# CPU MEMORY SETTINGS
# ============================================================

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["TF_NUM_INTRAOP_THREADS"] = "2"
os.environ["TF_NUM_INTEROP_THREADS"] = "2"

from pathlib import Path
import json

import numpy as np
import tensorflow as tf


# ============================================================
# TENSORFLOW SETTINGS
# ============================================================

tf.config.threading.set_intra_op_parallelism_threads(2)
tf.config.threading.set_inter_op_parallelism_threads(2)

tf.random.set_seed(42)
np.random.seed(42)


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

SOURCE_IMAGE_DIR = (
    ROOT
    / "data"
    / "pest"
    / "ip102"
    / "ip102_v1.1"
    / "images"
)

SELECTED_DIR = (
    ROOT
    / "data"
    / "pest"
    / "selected"
)

TRAIN_FILE = SELECTED_DIR / "train.txt"
VAL_FILE = SELECTED_DIR / "val.txt"
TEST_FILE = SELECTED_DIR / "test.txt"
CLASSES_FILE = SELECTED_DIR / "classes.json"

MODEL_DIR = ROOT / "models" / "pest"
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = (
    MODEL_DIR
    / "crop_pest_model.keras"
)

MODEL_CLASSES_PATH = (
    MODEL_DIR
    / "crop_pest_classes.json"
)


# ============================================================
# TRAINING SETTINGS
# ============================================================

IMG_SIZE = (160, 160)
BATCH_SIZE = 4

HEAD_EPOCHS = 3
FINE_TUNE_EPOCHS = 2

AUTOTUNE = 1


# ============================================================
# LOAD CLASS NAMES
# ============================================================

def load_class_names():

    if not CLASSES_FILE.exists():
        raise FileNotFoundError(
            f"Classes file not found:\n{CLASSES_FILE}"
        )

    with open(
        CLASSES_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        class_names = json.load(f)

    if len(class_names) != 20:
        raise ValueError(
            f"Expected 20 classes, found {len(class_names)}"
        )

    # Safety check
    forbidden_words = (
        "chilli",
        "chili",
        "pepper"
    )

    for name in class_names:

        name_lower = name.lower()

        if any(
            word in name_lower
            for word in forbidden_words
        ):
            raise ValueError(
                f"Forbidden class found: {name}"
            )

    return class_names


# ============================================================
# LOAD SELECTED SPLIT
# ============================================================

def load_split(file_path):

    paths = []
    labels = []

    if not file_path.exists():
        raise FileNotFoundError(
            f"Split file not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            image_name = parts[0]
            label = int(parts[1])

            image_path = (
                SOURCE_IMAGE_DIR
                / image_name
            )

            if not image_path.exists():
                continue

            paths.append(
                str(image_path)
            )

            labels.append(
                label
            )

    return paths, labels


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(
    path,
    label
):

    image = tf.io.read_file(path)

    image = tf.image.decode_jpeg(
        image,
        channels=3
    )

    image = tf.image.resize(
        image,
        IMG_SIZE
    )

    image = tf.cast(
        image,
        tf.float32
    )

    return image, label


# ============================================================
# DATASET
# ============================================================

def create_dataset(
    paths,
    labels,
    training=False
):

    dataset = tf.data.Dataset.from_tensor_slices(
        (
            paths,
            labels
        )
    )

    if training:

        # Entire selected training set is only 4,000 images,
        # so we can shuffle the complete set.
        dataset = dataset.shuffle(
            buffer_size=len(paths),
            seed=42,
            reshuffle_each_iteration=True
        )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=1
    )

    dataset = dataset.batch(
        BATCH_SIZE
    )

    dataset = dataset.prefetch(
        1
    )

    return dataset


# ============================================================
# BUILD MODEL
# ============================================================

def build_model(
    num_classes
):

    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip(
                "horizontal"
            ),
            tf.keras.layers.RandomRotation(
                0.08
            ),
            tf.keras.layers.RandomZoom(
                0.10
            ),
            tf.keras.layers.RandomContrast(
                0.10
            )
        ],
        name="augmentation"
    )

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(
            IMG_SIZE[0],
            IMG_SIZE[1],
            3
        ),
        include_top=False,
        weights="imagenet"
    )

    base_model.trainable = False

    inputs = tf.keras.Input(
        shape=(
            IMG_SIZE[0],
            IMG_SIZE[1],
            3
        )
    )

    x = augmentation(inputs)

    x = tf.keras.applications.mobilenet_v2.preprocess_input(
        x
    )

    x = base_model(
        x,
        training=False
    )

    x = tf.keras.layers.GlobalAveragePooling2D()(x)

    x = tf.keras.layers.Dropout(
        0.40
    )(x)

    outputs = tf.keras.layers.Dense(
        num_classes,
        activation="softmax"
    )(x)

    model = tf.keras.Model(
        inputs,
        outputs
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.0005
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model, base_model


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SMART CROP INTELLIGENCE - 20 CLASS PEST MODEL")
    print("=" * 70)

    print(
        "\nTensorFlow:",
        tf.__version__
    )

    print(
        "GPU devices:",
        tf.config.list_physical_devices("GPU")
    )

    # --------------------------------------------------------
    # Classes
    # --------------------------------------------------------

    class_names = load_class_names()

    print(
        "\nNumber of classes:",
        len(class_names)
    )

    print("\nClasses:")

    for index, name in enumerate(class_names):
        print(
            f"{index:2} -> {name}"
        )

    # --------------------------------------------------------
    # Load splits
    # --------------------------------------------------------

    print(
        "\nLoading training data..."
    )

    train_paths, train_labels = load_split(
        TRAIN_FILE
    )

    print(
        "Training images:",
        len(train_paths)
    )

    print(
        "\nLoading validation data..."
    )

    val_paths, val_labels = load_split(
        VAL_FILE
    )

    print(
        "Validation images:",
        len(val_paths)
    )

    print(
        "\nLoading test data..."
    )

    test_paths, test_labels = load_split(
        TEST_FILE
    )

    print(
        "Testing images:",
        len(test_paths)
    )

    if len(train_paths) == 0:
        raise RuntimeError(
            "No training images found."
        )

    if len(val_paths) == 0:
        raise RuntimeError(
            "No validation images found."
        )

    if len(test_paths) == 0:
        raise RuntimeError(
            "No test images found."
        )

    # --------------------------------------------------------
    # Create datasets
    # --------------------------------------------------------

    print(
        "\nCreating TensorFlow datasets..."
    )

    train_ds = create_dataset(
        train_paths,
        train_labels,
        training=True
    )

    val_ds = create_dataset(
        val_paths,
        val_labels,
        training=False
    )

    test_ds = create_dataset(
        test_paths,
        test_labels,
        training=False
    )

    # --------------------------------------------------------
    # Build model
    # --------------------------------------------------------

    print(
        "\nBuilding MobileNetV2..."
    )

    model, base_model = build_model(
        len(class_names)
    )

    print(
        "\nTotal parameters:",
        model.count_params()
    )

    # --------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(MODEL_PATH),
        monitor="val_accuracy",
        save_best_only=True,
        mode="max",
        verbose=1
    )

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=2,
        restore_best_weights=True,
        mode="max",
        verbose=1
    )

    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.3,
        patience=1,
        min_lr=1e-7,
        verbose=1
    )

    callbacks = [
        checkpoint,
        early_stopping,
        reduce_lr
    ]

    # ========================================================
    # PHASE 1
    # ========================================================

    print("\n" + "=" * 70)
    print("PHASE 1 - TRANSFER LEARNING")
    print("=" * 70)

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=HEAD_EPOCHS,
        callbacks=callbacks,
        verbose=1
    )

    # ========================================================
    # PHASE 2
    # ========================================================

    print("\n" + "=" * 70)
    print("PHASE 2 - FINE TUNING")
    print("=" * 70)

    base_model.trainable = True

    # Freeze most MobileNetV2 layers.
    fine_tune_from = max(
        0,
        len(base_model.layers) - 20
    )

    for layer in base_model.layers[
        :fine_tune_from
    ]:

        layer.trainable = False

    # Keep BatchNorm frozen.
    for layer in base_model.layers:

        if isinstance(
            layer,
            tf.keras.layers.BatchNormalization
        ):

            layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-5
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=FINE_TUNE_EPOCHS,
        callbacks=callbacks,
        verbose=1
    )

    # ========================================================
    # TEST
    # ========================================================

    print("\n" + "=" * 70)
    print("FINAL TEST EVALUATION")
    print("=" * 70)

    test_loss, test_accuracy = model.evaluate(
        test_ds,
        verbose=1
    )

    print(
        f"\nTest Accuracy: "
        f"{test_accuracy * 100:.2f}%"
    )

    print(
        f"Test Loss: "
        f"{test_loss:.4f}"
    )

    # ========================================================
    # SAVE CLASS NAMES
    # ========================================================

    with open(
        MODEL_CLASSES_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            class_names,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        "\nModel saved to:"
    )

    print(
        MODEL_PATH
    )

    print(
        "\nClasses saved to:"
    )

    print(
        MODEL_CLASSES_PATH
    )

    print(
        "\nChilli/Mirchi included: FALSE"
    )

    print(
        "\nPest model training completed."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()