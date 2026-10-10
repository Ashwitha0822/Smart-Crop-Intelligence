from pathlib import Path
import json

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    ROOT
    / "data"
    / "pest"
    / "selected"
)

IMAGE_DIR = (
    ROOT
    / "data"
    / "pest"
    / "ip102"
    / "ip102_v1.1"
    / "images"
)

TEST_FILE = DATA_DIR / "test.txt"

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


# ============================================================
# LOAD TEST DATA
# ============================================================

def load_test_data():

    paths = []
    labels = []

    with open(
        TEST_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            parts = line.split()

            image_name = parts[0]
            label = int(parts[1])

            image_path = IMAGE_DIR / image_name

            if image_path.exists():

                paths.append(
                    str(image_path)
                )

                labels.append(
                    label
                )

    return paths, labels


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(path):

    image = tf.io.read_file(
        str(path)
    )

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

    image = tf.expand_dims(
        image,
        axis=0
    )

    return image


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SMART CROP - PEST MODEL EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load classes
    # --------------------------------------------------------

    with open(
        CLASSES_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        class_names = json.load(f)

    print(
        "\nNumber of classes:",
        len(class_names)
    )

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print(
        "\nLoading model..."
    )

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    print(
        "Model loaded successfully."
    )

    # --------------------------------------------------------
    # Load test data
    # --------------------------------------------------------

    print(
        "\nLoading test dataset..."
    )

    image_paths, true_labels = load_test_data()

    print(
        "Test images:",
        len(image_paths)
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    predicted_labels = []

    print(
        "\nRunning predictions..."
    )

    for index, image_path in enumerate(
        image_paths,
        start=1
    ):

        image = load_image(
            image_path
        )

        probabilities = model.predict(
            image,
            verbose=0
        )[0]

        predicted_label = int(
            np.argmax(probabilities)
        )

        predicted_labels.append(
            predicted_label
        )

        if index % 100 == 0:

            print(
                f"Processed {index}/{len(image_paths)}"
            )

    # --------------------------------------------------------
    # Accuracy
    # --------------------------------------------------------

    accuracy = accuracy_score(
        true_labels,
        predicted_labels
    )

    print("\n" + "=" * 70)
    print("OVERALL RESULTS")
    print("=" * 70)

    print(
        f"\nAccuracy: {accuracy * 100:.2f}%"
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    report = classification_report(
        true_labels,
        predicted_labels,
        target_names=class_names,
        digits=4,
        zero_division=0
    )

    print("\n" + "=" * 70)
    print("CLASSIFICATION REPORT")
    print("=" * 70)

    print(report)

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        true_labels,
        predicted_labels
    )

    print("\n" + "=" * 70)
    print("CONFUSION MATRIX")
    print("=" * 70)

    print(
        "\nRows = Actual"
    )

    print(
        "Columns = Predicted"
    )

    print(
        cm
    )

    # --------------------------------------------------------
    # Most confused pairs
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("MOST CONFUSED CLASS PAIRS")
    print("=" * 70)

    confusion_pairs = []

    for actual in range(
        len(class_names)
    ):

        for predicted in range(
            len(class_names)
        ):

            if (
                actual != predicted
                and cm[actual][predicted] > 0
            ):

                confusion_pairs.append(
                    (
                        cm[actual][predicted],
                        actual,
                        predicted
                    )
                )

    confusion_pairs.sort(
        reverse=True
    )

    for count, actual, predicted in confusion_pairs[:15]:

        print(
            f"{class_names[actual]} "
            f"-> "
            f"{class_names[predicted]} "
            f": {count}"
        )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    report_file = (
        ROOT
        / "models"
        / "pest"
        / "pest_evaluation_report.txt"
    )

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "SMART CROP INTELLIGENCE - PEST MODEL EVALUATION\n"
        )

        f.write(
            "=" * 70
        )

        f.write(
            f"\n\nOverall Accuracy: "
            f"{accuracy * 100:.2f}%\n\n"
        )

        f.write(
            "Classification Report\n"
        )

        f.write(
            "=" * 70
            + "\n"
        )

        f.write(
            report
        )

        f.write(
            "\n\nMost Confused Class Pairs\n"
        )

        f.write(
            "=" * 70
            + "\n"
        )

        for count, actual, predicted in confusion_pairs[:15]:

            f.write(
                f"{class_names[actual]} "
                f"-> "
                f"{class_names[predicted]} "
                f": {count}\n"
            )

    print(
        "\nEvaluation report saved to:"
    )

    print(
        report_file
    )

    print("\nEvaluation completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()