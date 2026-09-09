import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings
from app.schemas.settings import UserSettingsRead, UserSettingsUpdate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings & Profile"])


@router.get("/", response_model=UserSettingsRead, summary="Foydalanuvchi sozlamalarini olish (GET)")
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings:
        # Agar qandaydir sabab bilan mavjud bo'lmasa, avtomatik yaratish
        user_settings = UserSettings(
            user_id=current_user.id,
            default_currency="UZS",
            reminder_time="09:00",
            reminder_days_before=1,
            notifications_enabled=True,
        )
        db.add(user_settings)
        db.commit()
        db.refresh(user_settings)
    return user_settings


@router.put("/", response_model=UserSettingsRead, summary="Foydalanuvchi sozlamalarini yangilash (UPDATE via PUT)")
def update_user_settings_put(
    settings_in: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _apply_settings_update(settings_in, current_user, db)


@router.patch("/", response_model=UserSettingsRead, summary="Foydalanuvchi sozlamalarini qisman yangilash (UPDATE via PATCH)")
def update_user_settings_patch(
    settings_in: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _apply_settings_update(settings_in, current_user, db)


def _apply_settings_update(settings_in: UserSettingsUpdate, current_user: User, db: Session):
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.add(user_settings)

    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user_settings, field, value)

    user_settings.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(user_settings)
    return user_settings
