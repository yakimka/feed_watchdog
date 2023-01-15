from datetime import datetime

from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from adapters.repositories.user import MongoUserRepository
from api.deps.mongo import get_db
from auth import InvalidTokenError, decode_token, oauth2_scheme
from domain.interfaces import IUserRepository
from domain.models import User


async def get_user_repo(
    db: AsyncIOMotorClient = Depends(get_db),
) -> IUserRepository:
    return MongoUserRepository(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> User:
    try:
        token_data = decode_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if datetime.fromtimestamp(token_data.exp) < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_user_by_id(token_data.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User.parse_obj(user.dict())
