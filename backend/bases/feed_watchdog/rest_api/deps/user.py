from datetime import datetime

from fastapi import Depends, HTTPException, status
from picodi import inject
from picodi.integrations.fastapi import Provide

from feed_watchdog.domain.interfaces import IRefreshTokenRepository, IUserRepository
from feed_watchdog.domain.models import User
from feed_watchdog.rest_api.auth import InvalidTokenError, decode_token, oauth2_scheme
from feed_watchdog.rest_api.dependencies import (
    get_refresh_token_repository,
    get_user_repository,
)
from feed_watchdog.rest_api.settings import Settings, get_settings

INVALID_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Provide(get_user_repository, wrap=True),
    settings: Settings = Provide(get_settings, wrap=True),
) -> User:
    try:
        token_data = decode_token(token, secret=settings.auth.jwt_secret_key)
    except InvalidTokenError:
        raise INVALID_CREDENTIALS_EXC from None

    if datetime.fromtimestamp(token_data.exp) < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_user_by_id(token_data.sub)

    if user is None:
        raise INVALID_CREDENTIALS_EXC

    return User.parse_obj(user.dict())


@inject
async def get_user_id_from_refresh_token(
    token: str = Depends(oauth2_scheme),
    refresh_token_repo: IRefreshTokenRepository = Depends(
        Provide(get_refresh_token_repository)
    ),
    settings: Settings = Provide(get_settings, wrap=True),
) -> str:
    try:
        token_data = decode_token(token, secret=settings.auth.jwt_refresh_secret_key)
    except InvalidTokenError:
        raise INVALID_CREDENTIALS_EXC from None

    user_id = token_data.sub
    tokens = [item.token for item in await refresh_token_repo.get_by_user_id(user_id)]
    if token not in tokens:
        raise INVALID_CREDENTIALS_EXC

    return user_id
