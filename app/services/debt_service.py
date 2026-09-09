import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.debt import Debt, DebtTypeEnum
from app.models.settings import UserSettings
from app.schemas.debt import IndividualPersonSummary, DebtRead
from app.schemas.monitoring import MonitoringDashboard, CurrencyStats


def get_individual_debts_summary(
    db: Session,
    user_id: int,
    include_paid: bool = False,
    sort_by: str = "name",
    order: str = "asc"
) -> List[IndividualPersonSummary]:
    """
    Guruhlangan individual qarzlar hisoboti (har bir inson bo'yicha).
    To Me (berilgan), By Me (olingan) va Net Balance (farq) hisoblanadi.
    """
    query = db.query(Debt).filter(Debt.user_id == user_id)
    if not include_paid:
        query = query.filter(Debt.is_paid == False)

    debts = query.all()

    # Guruhlash: (person_name, currency) -> ma'lumotlar
    grouped = defaultdict(lambda: {
        "person_name": "",
        "currency": "",
        "total_owed_to": 0.0,
        "total_owed_by": 0.0,
        "debts": []
    })

    for debt in debts:
        key = (debt.person_name.strip(), debt.currency.upper())
        item = grouped[key]
        item["person_name"] = debt.person_name.strip()
        item["currency"] = debt.currency.upper()
        if debt.debt_type == DebtTypeEnum.owed_to.value:
            item["total_owed_to"] += debt.amount
        elif debt.debt_type == DebtTypeEnum.owed_by.value:
            item["total_owed_by"] += debt.amount
        item["debts"].append(DebtRead.model_validate(debt))

    results = []
    for key, data in grouped.items():
        net = data["total_owed_to"] - data["total_owed_by"]
        results.append(
            IndividualPersonSummary(
                person_name=data["person_name"],
                currency=data["currency"],
                total_owed_to=round(data["total_owed_to"], 2),
                total_owed_by=round(data["total_owed_by"], 2),
                net_balance=round(net, 2),
                debts_count=len(data["debts"]),
                debts=data["debts"],
            )
        )

    # Saralash (sorting)
    reverse = (order.lower() == "desc")
    if sort_by == "name":
        results.sort(key=lambda x: x.person_name.lower(), reverse=reverse)
    elif sort_by == "net_balance":
        results.sort(key=lambda x: x.net_balance, reverse=reverse)
    elif sort_by == "amount":
        results.sort(key=lambda x: (x.total_owed_to + x.total_owed_by), reverse=reverse)

    return results


def get_monitoring_dashboard(db: Session, user_id: int) -> MonitoringDashboard:
    """
    Asosiy sahifa (Dashboard / Monitoring) uchun hisob-kitoblar:
    - Umumiy berilgan qarz (owed_to)
    - Umumiy olingan qarz (owed_by)
    - Joriy balans (owed_to - owed_by)
    - Har bir valyuta bo'yicha alohida statistika
    """
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    default_currency = user_settings.default_currency if user_settings else "UZS"

    all_debts = db.query(Debt).filter(Debt.user_id == user_id).all()

    total_debts_count = len(all_debts)
    active_debts = [d for d in all_debts if not d.is_paid]
    paid_debts = [d for d in all_debts if d.is_paid]

    now = datetime.datetime.now(datetime.timezone.utc)
    overdue_debts = [
        d for d in active_debts
        if d.date_due and (d.date_due.replace(tzinfo=datetime.timezone.utc) if d.date_due.tzinfo is None else d.date_due) < now
    ]

    # Valyutalar bo'yicha guruhlash
    currency_data = defaultdict(lambda: {
        "owed_to": 0.0,
        "owed_by": 0.0,
        "active_count": 0,
        "paid_count": 0
    })

    for debt in all_debts:
        curr = debt.currency.upper()
        if debt.is_paid:
            currency_data[curr]["paid_count"] += 1
        else:
            currency_data[curr]["active_count"] += 1
            if debt.debt_type == DebtTypeEnum.owed_to.value:
                currency_data[curr]["owed_to"] += debt.amount
            elif debt.debt_type == DebtTypeEnum.owed_by.value:
                currency_data[curr]["owed_by"] += debt.amount

    breakdown: List[CurrencyStats] = []
    for curr, vals in sorted(currency_data.items()):
        breakdown.append(
            CurrencyStats(
                currency=curr,
                total_owed_to=round(vals["owed_to"], 2),
                total_owed_by=round(vals["owed_by"], 2),
                net_balance=round(vals["owed_to"] - vals["owed_by"], 2),
                active_debts_count=vals["active_count"],
                paid_debts_count=vals["paid_count"],
            )
        )

    # Foydalanuvchining asosiy valyutasidagi (yoki barcha) umumiy summasi
    # Agar asosiy valyutada qarzlar bo'lsa, o'shani olamiz; bo'lmasa mavjud birinchi valyuta yoki 0
    default_stats = next((b for b in breakdown if b.currency == default_currency.upper()), None)
    if default_stats:
        total_owed_to = default_stats.total_owed_to
        total_owed_by = default_stats.total_owed_by
        current_balance = default_stats.net_balance
    else:
        # Barcha faol qarzlar yig'indisi (agar barchasi bitta valyutada bo'lsa yoki default bo'lsa)
        total_owed_to = sum(b.total_owed_to for b in breakdown)
        total_owed_by = sum(b.total_owed_by for b in breakdown)
        current_balance = round(total_owed_to - total_owed_by, 2)

    return MonitoringDashboard(
        default_currency=default_currency,
        total_owed_to=round(total_owed_to, 2),
        total_owed_by=round(total_owed_by, 2),
        current_balance=round(current_balance, 2),
        currency_breakdown=breakdown,
        total_debts_count=total_debts_count,
        active_debts_count=len(active_debts),
        paid_debts_count=len(paid_debts),
        overdue_debts_count=len(overdue_debts),
    )
