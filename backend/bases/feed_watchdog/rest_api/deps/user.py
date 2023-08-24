from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from feed_watchdog.domain.interfaces import IRefreshTokenRepository, IUserRepository
from feed_watchdog.domain.models import User
from feed_watchdog.repositories.user import MongoRefreshTokenRepository
from feed_watchdog.rest_api.auth import InvalidTokenError, decode_token, oauth2_scheme
from feed_watchdog.rest_api.container import Container
from feed_watchdog.rest_api.deps.mongo import get_db

INVALID_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_refresh_token_repo(
    db: AsyncIOMotorClient = Depends(get_db),
) -> IRefreshTokenRepository:
    return MongoRefreshTokenRepository(db)


@inject
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(Provide[Container.user_repository]),
    secret: str = Depends(Provide[Container.config.auth.jwt_secret_key]),
) -> User:
    try:
        token_data = decode_token(token, secret=secret)
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
    secret: str = Depends(Provide[Container.config.auth.jwt_refresh_secret_key]),
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo),
) -> str:
    try:
        token_data = decode_token(token, secret=secret)
    except InvalidTokenError:
        raise INVALID_CREDENTIALS_EXC from None

    user_id = token_data.sub
    tokens = [item.token for item in await refresh_token_repo.get_by_user_id(user_id)]
    if token not in tokens:
        raise INVALID_CREDENTIALS_EXC

    return user_id
