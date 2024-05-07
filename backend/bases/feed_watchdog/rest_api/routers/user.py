from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from picodi import Provide, inject
from pydantic import BaseModel

from feed_watchdog.domain.interfaces import IRefreshTokenRepository, IUserRepository
from feed_watchdog.domain.models import RefreshToken
from feed_watchdog.rest_api.auth import (
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
)
from feed_watchdog.rest_api.dependencies import (
    get_refresh_token_repository,
    get_user_repository,
)
from feed_watchdog.rest_api.deps.user import get_user_id_from_refresh_token
from feed_watchdog.utils.security import verify_password

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class LoginData(BaseModel):
    email: str
    password: str


@router.post("/user/login/", response_model=TokenResponse)
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: IUserRepository = Depends(Provide(get_user_repository)),
    refresh_token_repo: IRefreshTokenRepository = Depends(
        Provide(get_refresh_token_repository)
    ),
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

    refresh_token = create_refresh_token(user.id)
    await refresh_token_repo.create(RefreshToken(token=refresh_token, user_id=user.id))

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/user/refresh_token/", response_model=TokenResponse)
async def refresh(
    token: str = Depends(oauth2_scheme),
    user_id: str = Depends(Provide(get_user_id_from_refresh_token)),
):
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": token,
        "token_type": "bearer",
    }
