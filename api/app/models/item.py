import enum
from datetime import datetime
from uuid import UUID as PyUUID, uuid4
from sqlalchemy import DateTime, Enum, String, UUID, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base

class ItemCategory(str, enum.Enum):
    vegetable = "vegetable"
    fruit = "fruit"
    meat = "meat"
    seasoning = "seasoning"
    staple = "staple"
    dairy = "dairy"
    other = "other"

class ItemUnit(str, enum.Enum):
    grams = "grams"
    bottle = "bottle"
    box = "box"
    ml = "ml"
    pcs = "pcs"

class Item(Base):
    __tablename__ = "items"
    id: Mapped[PyUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[ItemCategory | None] = mapped_column(Enum(ItemCategory, name="item_category"))
    default_unit: Mapped[ItemUnit | None] = mapped_column(Enum(ItemUnit, name="item_unit"))
    default_shelf_life_days: Mapped[int | None] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(255))
    household_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL")
    )
