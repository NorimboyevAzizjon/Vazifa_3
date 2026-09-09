from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.monitoring import MonitoringDashboard
from app.services.auth_service import get_current_user
from app.services.debt_service import get_monitoring_dashboard

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Dashboard"])


@router.get("/", response_model=MonitoringDashboard, summary="Asosiy sahifa statistikasi va monitoring ma'lumotlarini olish (GET)")
def get_monitoring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Asosiy sahifa (Homepage / Dashboard) ma'lumotlari:
    - total_owed_to: Umumiy qarz berilgan summa
    - total_owed_by: Umumiy qarz olingan summa
    - current_balance: Joriy balans (qarzlar farqi: total_owed_to - total_owed_by)
    - currency_breakdown: Har bir valyuta bo'yicha alohida tahlil
    - active_debts_count, paid_debts_count, overdue_debts_count
    """
    return get_monitoring_dashboard(db=db, user_id=current_user.id)
