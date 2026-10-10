from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routes import auth, recommendation, health, weather
from backend.app.routes import disease
from backend.app.routes import guidance
from backend.app.routes import pest
from backend.app.routes import pest_guidance
from backend.app.routes import research
from backend.app.routes import voice
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart Crop Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://smart-crop-intelligence-nine.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router); app.include_router(recommendation.router); app.include_router(health.router); app.include_router(weather.router)
app.include_router(
    disease.router
)
app.include_router(guidance.router)
app.include_router(pest.router)
app.include_router(pest_guidance.router)
app.include_router(research.router)
app.include_router(voice.router)

@app.get("/")
def root(): return {"message":"Smart Crop Intelligence API is running"}
