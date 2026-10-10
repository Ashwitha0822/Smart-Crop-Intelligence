# Smart Crop Intelligence System using AI and Data Analytics

A full-stack academic project using React + FastAPI + MySQL + Scikit-learn.

## Kaggle dataset
Primary ML dataset: **Crop Recommendation Dataset** by Siddharth Sharma / commonly distributed as `Crop_recommendation.csv` and the `atharvaingle/crop-recommendation-dataset` Kaggle dataset. It contains 7 input features: N, P, K, temperature, humidity, pH and rainfall, with crop label as target. The Kaggle dataset has 2,200 rows / 22 crop classes in commonly used versions. See `data/DATASET_SOURCE.md`.

The project does **not** silently substitute a synthetic dataset. Run `python data/download_kaggle_dataset.py` after configuring your Kaggle API credentials.

## Features
- User registration/login with JWT
- Soil + weather based crop recommendation
- Top-3 crop probabilities
- Recommendation history stored in MySQL
- Weather endpoint (OpenWeather optional; demo fallback)
- Crop-health/NDVI input module
- Admin-style dataset statistics endpoint
- ML training and evaluation script
- React dashboard

## Folder structure
```
Smart-Crop-Intelligence-Kaggle/
├── frontend/                 # React + Vite
├── backend/                  # FastAPI + SQLAlchemy
├── ml/                       # Training and evaluation
├── data/                     # Kaggle downloader and dataset location
├── database/                 # MySQL schema
├── models/                   # trained model generated here
└── README.md
```

## 1. Requirements
- Python 3.10+
- Node.js 18+
- MySQL 8+
- Kaggle account/API token

## 2. Download the Kaggle dataset
Install Kaggle CLI:
```
pip install kaggle
```
Create the Kaggle API token from Kaggle Account Settings and place `kaggle.json` in `%USERPROFILE%\\.kaggle\\kaggle.json` on Windows or `~/.kaggle/kaggle.json` on Linux/macOS.

Then from the project root:
```
python data/download_kaggle_dataset.py
```
It downloads the dataset and copies the CSV to `data/Crop_recommendation.csv`.

## 3. Train the ML model
```
cd ml
pip install -r requirements.txt
python train_model.py
```
The script creates `models/crop_model.joblib` and `models/metrics.json`.

## 4. Create MySQL database
Open MySQL and run:
```
source database/schema.sql;
```
Or paste the file into MySQL Workbench.

## 5. Backend
```
cd backend
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS/Linux
# source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```
Edit `.env` with your MySQL username/password.

Backend docs: http://localhost:8000/docs

## 6. Frontend
```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Important academic note
The Kaggle crop recommendation dataset is widely used for ML demonstrations, but it is not a substitute for local agronomic validation. The app should be presented as a decision-support prototype, not as guaranteed agricultural advice.
