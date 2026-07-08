import enum
from datetime import datetime
from uuid import UUID as PyUUID, uuid4
from sqlalchemy import DateTime, Enum, String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base

class MemberRole(str, enum.Enum):
    owner = "owner"
    member = "member"

class Household(Base):
    __tablename__ = "households"
    id: Mapped[PyUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

class HouseholdMember(Base):
    __tablename__ = "household_members"
    user_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    household_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("households.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole, name="member_role"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
