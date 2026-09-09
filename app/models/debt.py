import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class DebtTypeEnum(str, enum.Enum):
    owed_to = "owed_to"   # Berilgan qarz (Owed To Me)
    owed_by = "owed_by"   # Olingan qarz (Owed By Me)


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    person_name = Column(String(255), nullable=False, index=True)
    debt_type = Column(String(20), nullable=False, index=True)  # "owed_to" or "owed_by"
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="UZS", nullable=False)
    description = Column(Text, nullable=True)

    is_paid = Column(Boolean, default=False, nullable=False, index=True)  # Fully paid status
    date_incurred = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    date_due = Column(DateTime, nullable=True)
    reminder_enabled = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="debts")
