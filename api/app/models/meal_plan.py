from datetime import datetime, date
from uuid import UUID as PyUUID, uuid4
import enum
from sqlalchemy import DateTime, UUID, Numeric, ForeignKey, Enum, Text, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    plan_date: Mapped[date | None] = mapped_column(Date)
    meal_type: Mapped[MealType | None] = mapped_column(Enum(MealType, name="meal_type"))
    household_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE")
    )
    recipe_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("recipes.id", ondelete="SET NULL")
    )
    servings_planned: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
