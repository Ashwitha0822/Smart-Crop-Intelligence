from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    n = Column(Float, nullable=False); p = Column(Float, nullable=False); k = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False); humidity = Column(Float, nullable=False)
    ph = Column(Float, nullable=False); rainfall = Column(Float, nullable=False)
    recommended_crop = Column(String(100), nullable=False); confidence = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

class CropHealth(Base):
    __tablename__ = "crop_health"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ndvi = Column(Float, nullable=False)
    health_status = Column(String(30), nullable=False)
    note = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
