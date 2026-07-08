from datetime import datetime
from uuid import UUID as PyUUID, uuid4
from sqlalchemy import DateTime, Enum, String, UUID, ForeignKey, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.item import ItemCategory, ItemUnit
from decimal import Decimal

from app.db import Base

class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[PyUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cook_time_minutes: Mapped[int | None] = mapped_column(Integer)
    servings: Mapped[int | None] = mapped_column(Integer)
    household_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL")
    )

class RecipeItem(Base):
    __tablename__ = "recipe_items"
    recipe_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True
    )
    item_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("items.id", ondelete="RESTRICT"), primary_key=True
    )
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(precision=10, scale=2))
    unit: Mapped[ItemUnit | None] = mapped_column(Enum(ItemUnit, name="item_unit"))
    notes: Mapped[str | None] = mapped_column(Text)