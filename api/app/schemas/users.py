from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    display_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    created_at: datetime
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    display_name: str | None = None