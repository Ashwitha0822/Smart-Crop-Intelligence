from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class SoilIn(BaseModel):
    N: float = Field(ge=0, le=300)
    P: float = Field(ge=0, le=300)
    K: float = Field(ge=0, le=400)
    temperature: float = Field(ge=-20, le=60)
    humidity: float = Field(ge=0, le=100)
    ph: float = Field(ge=0, le=14)
    rainfall: float = Field(ge=0, le=2000)

class HealthIn(BaseModel):
    ndvi: float = Field(ge=-1, le=1)
    note: str | None = None
