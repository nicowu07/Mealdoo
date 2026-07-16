from fastapi import APIRouter, status, HTTPException
from app.deps import SessionDep
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate, Token
from uuid import UUID
from app.security import hash_password, verify_password, create_access_token
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.deps import CurrentUserDep

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: SessionDep):
    user = User(display_name=user_in.display_name, email=user_in.email, hashed_password=hash_password(user_in.password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating user")
    session.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    users = session.execute(select(User).where(User.email == form_data.username)).scalars().all()
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not verify_password(form_data.password, users[0].hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(users[0].id)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user: CurrentUserDep):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: UUID, user_in: UserUpdate, session: SessionDep, current_user: CurrentUserDep):
    # Check if the current user is the same as the user being updated
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this user")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating user")
    #session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, session: SessionDep, current_user: CurrentUserDep):
    # Check if the current user is the same as the user being deleted
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to delete this user")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    session.delete(user)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting user")
    return None

