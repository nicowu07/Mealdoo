from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from app.models.household import MemberRole

class HouseholdBase(BaseModel):
    name: str

class HouseholdCreate(HouseholdBase):
    owner_id: UUID

class HouseholdRead(HouseholdBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)