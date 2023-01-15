from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from api.deps.user import get_current_user, get_user_repo
from auth import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    oauth2_scheme,
)
from domain.interfaces import IUserRepository
from domain.models import User
from utils.security import verify_password

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginData(BaseModel):
    email: str
    password: str


@router.post("/user/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: IUserRepository = Depends(get_user_repo),
):
    user = await user_repo.get_user_by_email(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }


@router.post("/user/refresh_token/", response_model=TokenResponse)
async def refresh(
    token: str = Depends(oauth2_scheme), user: User = Depends(get_current_user)
):
    # TODO store refresh token in DB and check if it's valid
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": token,
        "token_type": "bearer",
    }
