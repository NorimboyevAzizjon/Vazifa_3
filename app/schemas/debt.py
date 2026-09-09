from typing import Optional, List, Literal
import datetime
from pydantic import BaseModel, Field, ConfigDict


def get_current_utc_time():
    return datetime.datetime.now(datetime.timezone.utc)


class DebtBase(BaseModel):
    person_name: str = Field(..., min_length=1, max_length=255, description="Qarz berayotgan yoki olayotgan shaxsning to'liq ismi")
    debt_type: Literal["owed_to", "owed_by"] = Field(..., description="Qarz turi: owed_to (berilgan qarz) yoki owed_by (olingan qarz)")
    amount: float = Field(..., gt=0, description="Qarz summasi (0 dan katta bo'lishi kerak)")
    currency: str = Field(default="UZS", description="Valyuta (UZS, USD, EUR, etc.)")
    description: Optional[str] = Field(default=None, description="Qisqacha ma'lumot")
    is_paid: bool = Field(default=False, description="To'langanlik holati (Fully Paid)")
    date_incurred: Optional[datetime.datetime] = Field(default_factory=get_current_utc_time, description="Qarz olingan/berilgan sana va vaqt")
    date_due: Optional[datetime.datetime] = Field(default=None, description="Qaytarish muddati")
    reminder_enabled: bool = Field(default=False, description="Eslatma yoqilganligi")


class DebtCreate(DebtBase):
    pass


class DebtUpdate(BaseModel):
    person_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    debt_type: Optional[Literal["owed_to", "owed_by"]] = None
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None
    is_paid: Optional[bool] = None
    date_incurred: Optional[datetime.datetime] = None
    date_due: Optional[datetime.datetime] = None
    reminder_enabled: Optional[bool] = None


class DebtRead(DebtBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class IndividualPersonSummary(BaseModel):
    person_name: str
    currency: str
    total_owed_to: float = Field(..., description="Berilgan jami summa (To Me)")
    total_owed_by: float = Field(..., description="Olingan jami summa (By Me)")
    net_balance: float = Field(..., description="Sof balans (To Me - By Me). Musbat bo'lsa odam sizdan qarzdor, manfiy bo'lsa siz qarzdorsiz")
    debts_count: int
    debts: List[DebtRead] = []
