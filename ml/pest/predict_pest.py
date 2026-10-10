from pathlib import Path
import json
import sys

import numpy as np
import tensorflow as tf


ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT / "models" / "pest" / "crop_pest_model.keras"
CLASSES_PATH = ROOT / "models" / "pest" / "crop_pest_classes.json"

IMG_SIZE = (160, 160)


def predict(image_path):

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    with open(
        CLASSES_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        class_names = json.load(f)

    image = tf.io.read_file(
        str(image_path)
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

    predictions = model.predict(
        image,
        verbose=0
    )[0]

    top_indices = np.argsort(
        predictions
    )[::-1][:5]

    print("\n" + "=" * 60)
    print("PEST PREDICTION")
    print("=" * 60)

    print(
        f"\nImage: {image_path}"
    )

    for rank, index in enumerate(
        top_indices,
        start=1
    ):

        print(
            f"{rank}. "
            f"{class_names[index]} "
            f"-> "
            f"{predictions[index] * 100:.2f}%"
        )

    print("=" * 60)


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            'py -3.14 ml\\pest\\predict_pest.py "IMAGE_PATH"'
        )

        sys.exit(1)

    image_path = Path(
        sys.argv[1]
    )

    if not image_path.exists():

        print(
            f"Image not found:\n{image_path}"
        )

        sys.exit(1)

    predict(
        image_path
    )