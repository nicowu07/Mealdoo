from fastapi import APIRouter, status, HTTPException
from app.deps import SessionDep, CurrentUserDep
from app.models import Household, HouseholdMember, MemberRole
from app.schemas import HouseholdCreate, HouseholdRead, HouseholdUpdate, HouseholdMemberCreate, HouseholdMemberRead
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select


router = APIRouter(prefix="/households", tags=["households"])

def require_household_member(session: SessionDep, household_id: UUID, user_id: UUID, owner_only: bool = False) -> HouseholdMember:
    membership = session.get(HouseholdMember, (user_id, household_id))
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this household")
    if owner_only and membership.role != MemberRole.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can perform this action")
    return membership

@router.post("", response_model=HouseholdRead, status_code=status.HTTP_201_CREATED)
def create_household(household_in: HouseholdCreate, session: SessionDep, current_user: CurrentUserDep):
    household = Household(name=household_in.name)
    session.add(household)
    session.flush()  # Flush to get the household ID before committing
    # Create a HouseholdMember for the owner
    owner_member = HouseholdMember(
        household_id=household.id,
        user_id=current_user.id,
        role=MemberRole.owner
    )
    session.add(owner_member)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating household member")
    
    return household

@router.get("/{household_id}", response_model=HouseholdRead)
def get_household(household_id: UUID, session: SessionDep, current_user: CurrentUserDep):
    household = session.get(Household, household_id)
    if not household:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found")
    require_household_member(session, household_id, current_user.id, owner_only=False)
    return household

@router.get("", response_model=list[HouseholdRead])
def get_households(session: SessionDep, current_user: CurrentUserDep):
    stmt = (
        select(Household)
        .join(HouseholdMember, HouseholdMember.household_id == Household.id)
        .where(HouseholdMember.user_id == current_user.id)
    )
    households = session.execute(stmt).scalars().all()
    return households

@router.patch("/{household_id}", response_model=HouseholdRead)
def update_household(household_id: UUID, household_in: HouseholdUpdate, session: SessionDep, current_user: CurrentUserDep):
    household = session.get(Household, household_id)
    if not household:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found")

    require_household_member(session, household_id, current_user.id, owner_only=True)
    for field, value in household_in.model_dump(exclude_unset=True).items():
        setattr(household, field, value)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating household")
    return household

@router.delete("/{household_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_household(household_id: UUID, session: SessionDep, current_user: CurrentUserDep):
    household = session.get(Household, household_id)
    if not household:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found")

    require_household_member(session, household_id, current_user.id, owner_only=True)
    session.delete(household)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting household")

@router.post("/{household_id}/members", status_code=status.HTTP_201_CREATED, response_model=HouseholdMemberRead)
def add_household_member(household_id: UUID, member_in: HouseholdMemberCreate, session: SessionDep, current_user: CurrentUserDep):
    household = session.get(Household, household_id)
    if not household:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found")

    require_household_member(session, household_id, current_user.id, owner_only=True)

    new_member = HouseholdMember(household_id=household_id, user_id=member_in.user_id, role=member_in.role)
    session.add(new_member)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error adding member to household")
    session.refresh(new_member)
    return new_member

@router.get("/{household_id}/members", response_model=list[HouseholdMemberRead])
def get_household_members(household_id: UUID, session: SessionDep, current_user: CurrentUserDep):
    household = session.get(Household, household_id)
    if not household:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Household not found")

    require_household_member(session, household_id, current_user.id, owner_only=False)  # Allow members to view the list of members

    stmt = select(HouseholdMember).where(HouseholdMember.household_id == household_id)
    members = session.execute(stmt).scalars().all()
    return members