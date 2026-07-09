from datetime import datetime
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, UUID, Numeric, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from decimal import Decimal
from app.models.item import ItemUnit

from app.db import Base


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    household_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE")
    )
    item_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("items.id", ondelete="CASCADE")
    )
    quantity_needed: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=10, scale=2)
    )
    unit: Mapped[ItemUnit | None] = mapped_column(Enum(ItemUnit, name="item_unit", create_type=False))
    is_purchased: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    added_by: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
