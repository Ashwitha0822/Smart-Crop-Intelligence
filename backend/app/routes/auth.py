import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "smart_crop_secret_2026_change_this"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


# ---------------------------------------------------------
# Password functions
# ---------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a password against its bcrypt hash.
    """

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------
# JWT token
# ---------------------------------------------------------

def create_access_token(user_id: int) -> str:
    """
    Create JWT access token.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new Smart Crop Intelligence user.
    """

    name = data.name.strip()
    email = data.email.strip().lower()
    password = data.password

    # Validate name
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty."
        )

    # Validate password
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 6 characters."
        )

    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Create password hash
    password_hash = hash_password(password)

    # Create user
    user = User(
        name=name,
        email=email,
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login using email and password.

    Swagger OAuth2 uses:
        username = user's email
        password = user's password
    """

    email = form_data.username.strip().lower()
    password = form_data.password

    # Find user
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Verify password
    if not verify_password(
        password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Create token
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }