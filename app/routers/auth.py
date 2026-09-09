from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings
from app.schemas.auth import UserRegister, UserLogin, UserRead, Token
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Foydalanuvchi ro'yxatdan o'tishi")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Username mavjudligini tekshirish
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu foydalanuvchi nomi (username) allaqachon band.",
        )
    # Email mavjudligini tekshirish
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu email allaqachon ro'yxatdan o'tgan.",
        )

    # Foydalanuvchini yaratish
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Birlamchi sozlamalarni yaratish
    user_settings = UserSettings(
        user_id=new_user.id,
        default_currency="UZS",
        reminder_time="09:00",
        reminder_days_before=1,
        notifications_enabled=True,
    )
    db.add(user_settings)
    db.commit()

    return new_user


@router.post("/login", response_model=Token, summary="Tizimga kirish va JWT token olish (JSON body)")
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri foydalanuvchi nomi yoki parol.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token, summary="OAuth2 standart login form (Swagger UI uchun)")
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri foydalanuvchi nomi yoki parol.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead, summary="Joriy foydalanuvchi ma'lumotlari")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
