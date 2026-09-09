from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CurrencyStats(BaseModel):
    currency: str
    total_owed_to: float = Field(..., description="Ushbu valyutada berilgan jami qarz")
    total_owed_by: float = Field(..., description="Ushbu valyutada olingan jami qarz")
    net_balance: float = Field(..., description="Ushbu valyutadagi joriy balans (owed_to - owed_by)")
    active_debts_count: int
    paid_debts_count: int


class MonitoringDashboard(BaseModel):
    default_currency: str
    total_owed_to: float = Field(..., description="Umumiy qarz berilgan summa (foydalanuvchining asosiy valyutasida)")
    total_owed_by: float = Field(..., description="Umumiy qarz olingan summa (foydalanuvchining asosiy valyutasida)")
    current_balance: float = Field(..., description="Joriy balans (qarzlar farqi: total_owed_to - total_owed_by)")
    currency_breakdown: List[CurrencyStats] = Field(default=[], description="Har bir valyuta bo'yicha alohida hisobot")
    total_debts_count: int
    active_debts_count: int
    paid_debts_count: int
    overdue_debts_count: int
