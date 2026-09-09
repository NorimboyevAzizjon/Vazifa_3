import datetime
from typing import Optional, List, Union, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.database import get_db
from app.models.user import User
from app.models.debt import Debt, DebtTypeEnum
from app.schemas.debt import DebtCreate, DebtUpdate, DebtRead, IndividualPersonSummary
from app.services.auth_service import get_current_user
from app.services.debt_service import get_individual_debts_summary

router = APIRouter(prefix="/debts", tags=["Debts Management"])


@router.post("/", response_model=DebtRead, status_code=status.HTTP_201_CREATED, summary="Yangi qarz qo'shish (POST)")
def create_debt(
    debt_in: DebtCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yangi qarz yozish:
    - debt_type: owed_to (berilgan) yoki owed_by (olingan)
    - person_name: to'liq ism
    - amount: qarz qiymati (> 0)
    - currency: valyuta kodi (UZS, USD, etc.)
    - description: qisqacha tavsif
    - date_incurred: qarz olingan/berilgan sana va vaqt
    - date_due: qaytarish sanasi va vaqti
    - reminder_enabled: eslatma
    """
    debt_data = debt_in.model_dump()
    if not debt_data.get("date_incurred"):
        debt_data["date_incurred"] = datetime.datetime.now(datetime.timezone.utc)

    new_debt = Debt(
        user_id=current_user.id,
        **debt_data
    )
    db.add(new_debt)
    db.commit()
    db.refresh(new_debt)
    return new_debt


@router.get(
    "/",
    response_model=Union[List[IndividualPersonSummary], List[DebtRead]],
    summary="Qarzlar ro'yxatini olish (3 ta filtr bo'yicha)"
)
def list_debts(
    debt_type: Optional[Literal["owed_to", "owed_by", "individual"]] = Query(
        None,
        description="Filtr turi: owed_to (berilgan), owed_by (olingan), individual (shaxs kesimida jamlangan)"
    ),
    is_paid: Optional[bool] = Query(None, description="To'langan yoki to'lanmagan qarzlar filtri"),
    sort_by: Optional[Literal["date_incurred", "date_due", "amount", "name"]] = Query(
        "date_incurred",
        description="Saralash maydoni"
    ),
    order: Optional[Literal["asc", "desc"]] = Query("desc", description="Saralash tartibi"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Qarzlar ro'yxatini olish:
    - debt_type=owed_to: Berilgan qarzlar ro'yxati
    - debt_type=owed_by: Olingan qarzlar ro'yxati
    - debt_type=individual: Har bir inson bo'yicha alohida jamlangan hisob-kitob (To Me, By Me, Net Balance)
    - Agar debt_type ko'rsatilsa bo'lmasa: barcha qarzlar ro'yxati qaytadi
    """
    # 1. Individual ko'rinish
    if debt_type == "individual":
        include_paid = (is_paid is True) if is_paid is not None else False
        return get_individual_debts_summary(
            db=db,
            user_id=current_user.id,
            include_paid=include_paid,
            sort_by=sort_by if sort_by else "name",
            order=order if order else "asc"
        )

    # 2. Oddiy ro'yxat (owed_to, owed_by yoki barchasi)
    query = db.query(Debt).filter(Debt.user_id == current_user.id)

    if debt_type in ["owed_to", "owed_by"]:
        query = query.filter(Debt.debt_type == debt_type)

    if is_paid is not None:
        query = query.filter(Debt.is_paid == is_paid)

    # Saralash
    sort_column = Debt.date_incurred
    if sort_by == "date_due":
        sort_column = Debt.date_due
    elif sort_by == "amount":
        sort_column = Debt.amount
    elif sort_by == "name":
        sort_column = Debt.person_name

    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    return query.all()


@router.get("/{debt_id}", response_model=DebtRead, summary="Bitta qarz ma'lumotlarini olish")
def get_debt(
    debt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == current_user.id).first()
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Qarz topilmadi yoki sizga tegishli emas."
        )
    return debt


@router.put("/{debt_id}", response_model=DebtRead, summary="Qarzni to'liq o'zgartirish (UPDATE via PUT)")
def update_debt_put(
    debt_id: int,
    debt_in: DebtUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _apply_debt_update(debt_id, debt_in, current_user, db)


@router.patch("/{debt_id}", response_model=DebtRead, summary="Qarzni qisman o'zgartirish (UPDATE via PATCH)")
def update_debt_patch(
    debt_id: int,
    debt_in: DebtUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _apply_debt_update(debt_id, debt_in, current_user, db)


@router.delete("/{debt_id}", status_code=status.HTTP_200_OK, summary="Qarzni o'chirish (DELETE)")
def delete_debt(
    debt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == current_user.id).first()
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Qarz topilmadi yoki sizga tegishli emas."
        )

    db.delete(debt)
    db.commit()
    return {"status": "success", "message": f"Qarz #{debt_id} muvaffaqiyatli o'chirildi."}


def _apply_debt_update(debt_id: int, debt_in: DebtUpdate, current_user: User, db: Session) -> Debt:
    debt = db.query(Debt).filter(Debt.id == debt_id, Debt.user_id == current_user.id).first()
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Qarz topilmadi yoki sizga tegishli emas."
        )

    update_data = debt_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(debt, field, value)

    debt.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(debt)
    return debt
