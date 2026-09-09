from typing import Optional
import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserSettingsBase(BaseModel):
    default_currency: str = Field(default="UZS", description="Asosiy valyuta (UZS, USD, EUR, etc.)")
    reminder_time: str = Field(default="09:00", description="Eslatma vaqti (HH:MM format)")
    reminder_days_before: int = Field(default=1, ge=0, description="Qarz to'lovidan necha kun oldin eslatish")
    notifications_enabled: bool = Field(default=True, description="Eslatmalar yoqilganligi")


class UserSettingsUpdate(BaseModel):
    default_currency: Optional[str] = None
    reminder_time: Optional[str] = None
    reminder_days_before: Optional[int] = Field(default=None, ge=0)
    notifications_enabled: Optional[bool] = None


class UserSettingsRead(UserSettingsBase):
    id: int
    user_id: int
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
