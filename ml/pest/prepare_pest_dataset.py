from pathlib import Path
from collections import defaultdict
import random
import json


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

SOURCE_DIR = ROOT / "data" / "pest" / "ip102" / "ip102_v1.1"
SELECTED_DIR = ROOT / "data" / "pest" / "selected"

SELECTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SELECTED PEST CLASSES
# ============================================================
# These are IP102 zero-based class IDs.
#
# Crop groups:
# Rice   -> 8 classes
# Maize  -> 2 classes
# Grape  -> 2 classes
# Orange -> 6 classes
# Mango  -> 2 classes
#
# Chilli/Mirchi is NOT included.
# ============================================================

SELECTED_CLASSES = {
    0: "rice leaf roller",
    3: "asiatic rice borer",
    4: "yellow rice borer",
    5: "rice gall midge",
    7: "brown plant hopper",
    8: "white backed plant hopper",
    9: "small brown plant hopper",
    10: "rice water weevil",

    22: "corn borer",
    23: "army worm",

    59: "Viteus vitifoliae",
    66: "Ampelophaga",

    76: "Icerya purchasi Maskell",
    77: "Unaspis yanonensis",
    82: "Aleurocanthus spiniferus",
    83: "Tetradacus c Bactrocera minax",
    88: "Phyllocnistis citrella Stainton",
    91: "Aphis citricola Vander Goot",

    99: "Rhytidodera bowrinii white",
    100: "Sternochetus frigidus",
}


# ============================================================
# NEW LABEL MAPPING
# ============================================================

OLD_TO_NEW = {
    old_id: new_id
    for new_id, old_id
    in enumerate(SELECTED_CLASSES.keys())
}


NEW_CLASS_NAMES = [
    name
    for name
    in SELECTED_CLASSES.values()
]


# ============================================================
# SETTINGS
# ============================================================

SEED = 42

# Make training balanced.
MAX_TRAIN_PER_CLASS = 200

# Keep validation and test reasonably balanced.
MAX_VAL_PER_CLASS = 80
MAX_TEST_PER_CLASS = 80


# ============================================================
# READ ORIGINAL SPLIT
# ============================================================

def read_split(
    filename,
    max_per_class
):

    source_file = SOURCE_DIR / filename

    grouped = defaultdict(list)

    with open(
        source_file,
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
            old_label = int(parts[1])

            if old_label not in SELECTED_CLASSES:
                continue

            grouped[old_label].append(
                image_name
            )

    rng = random.Random(SEED)

    selected_rows = []

    for old_label in SELECTED_CLASSES:

        images = grouped[old_label]

        rng.shuffle(images)

        images = images[:max_per_class]

        new_label = OLD_TO_NEW[old_label]

        for image_name in images:

            selected_rows.append(
                f"{image_name} {new_label}"
            )

    rng.shuffle(
        selected_rows
    )

    return selected_rows, grouped


# ============================================================
# SAVE SPLIT
# ============================================================

def save_split(
    filename,
    rows
):

    output_file = SELECTED_DIR / filename

    output_file.write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8"
    )

    return output_file


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SMART CROP - PREPARE SELECTED PEST DATASET")
    print("=" * 70)

    print(
        f"\nSelected classes: {len(SELECTED_CLASSES)}"
    )

    print("\nSelected pest classes:")

    for new_id, (old_id, name) in enumerate(
        SELECTED_CLASSES.items()
    ):
        print(
            f"{new_id:2} -> IP102 {old_id:3} -> {name}"
        )

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    train_rows, train_grouped = read_split(
        "train.txt",
        MAX_TRAIN_PER_CLASS
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    val_rows, val_grouped = read_split(
        "val.txt",
        MAX_VAL_PER_CLASS
    )

    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_rows, test_grouped = read_split(
        "test.txt",
        MAX_TEST_PER_CLASS
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    train_file = save_split(
        "train.txt",
        train_rows
    )

    val_file = save_split(
        "val.txt",
        val_rows
    )

    test_file = save_split(
        "test.txt",
        test_rows
    )

    classes_file = SELECTED_DIR / "classes.json"

    classes_file.write_text(
        json.dumps(
            NEW_CLASS_NAMES,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # PRINT COUNTS
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SELECTED DATASET COUNTS")
    print("=" * 70)

    print(
        f"\nTraining images:   {len(train_rows)}"
    )

    print(
        f"Validation images: {len(val_rows)}"
    )

    print(
        f"Testing images:    {len(test_rows)}"
    )

    print("\nTraining count by class:")

    train_counts = defaultdict(int)

    for row in train_rows:

        label = int(
            row.split()[1]
        )

        train_counts[label] += 1

    for label in range(
        len(NEW_CLASS_NAMES)
    ):

        print(
            f"{label:2} | "
            f"{train_counts[label]:3} | "
            f"{NEW_CLASS_NAMES[label]}"
        )

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    all_names = " ".join(
        NEW_CLASS_NAMES
    ).lower()

    forbidden = [
        "chilli",
        "chili",
        "pepper"
    ]

    for word in forbidden:

        if word in all_names:

            raise RuntimeError(
                f"Forbidden word found: {word}"
            )

    print("\nChilli/Mirchi safety check: PASSED")

    print("\nFiles created:")

    print(train_file)
    print(val_file)
    print(test_file)
    print(classes_file)

    print("\nDataset preparation completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()