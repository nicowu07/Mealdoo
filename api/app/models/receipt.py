from datetime import datetime, date
from uuid import UUID as PyUUID, uuid4
import enum

from sqlalchemy import DateTime, String, UUID, Numeric, ForeignKey, Integer, Enum, Text, Date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from decimal import Decimal
from app.models.item import ItemUnit

from app.db import Base

class InventorySource(str, enum.Enum):
    receipt_scan = "receipt_scan"
    photo_scan = "photo_scan"
    manual = "manual"


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[PyUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4
    )
    household_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE")
    )
    store_name: Mapped[str | None] = mapped_column(String(100))
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(precision=10, scale=2))
    receipt_date: Mapped[date | None] = mapped_column(Date)
    image_url: Mapped[str | None] = mapped_column(String(255))
    raw_ocr_text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    uploaded_by: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="SET NULL")
    )

class InventoryEntry(Base):
    __tablename__ = "inventory_entries"

    id: Mapped[PyUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4
    )
    item_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("items.id", ondelete="RESTRICT")
    )
    household_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE")
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    unit: Mapped[ItemUnit | None] = mapped_column(Enum(ItemUnit, name="item_unit", create_type=False))
    expiry_date: Mapped[date | None] = mapped_column(Date)
    purchased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[InventorySource] = mapped_column(Enum(InventorySource, name="inventory_source"))
    receipt_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("receipts.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )