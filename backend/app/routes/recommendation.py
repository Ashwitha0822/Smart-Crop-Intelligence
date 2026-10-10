from pathlib import Path
import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Recommendation
from ..schemas import SoilIn
from ..auth import current_user

router = APIRouter(prefix="/api/recommendation", tags=["Crop Recommendation"])
MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "crop_model.joblib"
_bundle = None

def get_model():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise HTTPException(500, "ML model not found. Run ml/train_model.py first.")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle

@router.post("")
def recommend(data: SoilIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    bundle = get_model(); model=bundle["model"]; features=bundle["features"]
    X = pd.DataFrame([[data.N,data.P,data.K,data.temperature,data.humidity,data.ph,data.rainfall]], columns=features)
    pred = str(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    classes = model.classes_
    top = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)[:3]
    conf = float(top[0][1])
    rec = Recommendation(user_id=user.id, n=data.N,p=data.P,k=data.K,temperature=data.temperature,humidity=data.humidity,ph=data.ph,rainfall=data.rainfall,recommended_crop=pred,confidence=conf)
    db.add(rec); db.commit(); db.refresh(rec)
    return {"recommended_crop": pred, "confidence": conf, "top3":[{"crop":str(c),"probability":float(p)} for c,p in top]}

@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Recommendation).filter(Recommendation.user_id==user.id).order_by(Recommendation.id.desc()).limit(50).all()
    return [{"id":r.id,"crop":r.recommended_crop,"confidence":r.confidence,"created_at":r.created_at} for r in rows]
