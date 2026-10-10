from pathlib import Path
import subprocess, zipfile, shutil

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Crop_recommendation.csv"
TMP = ROOT / "kaggle_download"
TMP.mkdir(exist_ok=True)

DATASET = "atharvaingle/crop-recommendation-dataset"
print(f"Downloading {DATASET} from Kaggle...")
subprocess.run([
    "kaggle", "datasets", "download", "-d", DATASET,
    "-p", str(TMP), "--force"
], check=True)

zips = list(TMP.glob("*.zip"))
if not zips:
    raise FileNotFoundError("Kaggle download completed but no ZIP was found.")

with zipfile.ZipFile(zips[0]) as z:
    z.extractall(TMP / "unzipped")

candidates = list((TMP / "unzipped").rglob("*.csv"))
if not candidates:
    raise FileNotFoundError("No CSV file found in the Kaggle dataset archive.")

# Prefer the canonical file name if present.
chosen = next((p for p in candidates if p.name.lower() == "crop_recommendation.csv"), candidates[0])
shutil.copy2(chosen, OUT)
print(f"Dataset ready: {OUT}")
print(f"Rows/columns will be checked by the training script.")
