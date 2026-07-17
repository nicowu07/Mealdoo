from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models.household import MemberRole

class HouseholdBase(BaseModel):
    name: str

class HouseholdCreate(HouseholdBase):
    pass

class HouseholdRead(HouseholdBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HouseholdUpdate(HouseholdBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class HouseholdMemberCreate(BaseModel):
    user_id: UUID
    role: MemberRole
class HouseholdMemberRead(HouseholdMemberCreate):
    household_id: UUID
    user_id: UUID
    role: MemberRole

    model_config = ConfigDict(from_attributes=True)