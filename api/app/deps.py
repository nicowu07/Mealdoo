from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.security import decode_access_token
from app.models import User
from sqlalchemy.orm import Session
from jwt import InvalidTokenError

from app.db import engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,) -> User:
    try: 
        user_id = decode_access_token(token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]