from fastapi import APIRouter, status, HTTPException
from app.deps import SessionDep
from app.models import Household, HouseholdMember, MemberRole
from app.schemas import HouseholdCreate, HouseholdRead
from uuid import UUID
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/households", tags=["households"])

@router.post("", response_model=HouseholdRead, status_code=status.HTTP_201_CREATED)
def create_household(household_in: HouseholdCreate, session: SessionDep):
    household = Household(name=household_in.name)
    session.add(household)
    # Create a HouseholdMember for the owner
    owner_member = HouseholdMember(
        household_id=household.id,
        user_id=household_in.owner_id,
        role=MemberRole.owner
    )
    session.add(owner_member)
    print("household.id after add:", household.id)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating household member")
    
    return household