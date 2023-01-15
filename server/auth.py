from datetime import datetime, timedelta, timezone
from typing import Any, Union

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel, ValidationError

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 31  # 31 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "some-secret-key"
JWT_REFRESH_SECRET_KEY = "some-secret-key"


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/user/login", scheme_name="JWT"
)


def _create_token(subject: Union[str, Any], expires_minutes: int) -> str:
    expires_delta = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)


def create_access_token(
    subject: Union[str, Any], expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    return _create_token(subject, expires_minutes)


def create_refresh_token(
    subject: Union[str, Any],
    expires_minutes: int = REFRESH_TOKEN_EXPIRE_MINUTES,
) -> str:
    return _create_token(subject, expires_minutes)


class TokenPayload(BaseModel):
    sub: str
    exp: int


class InvalidTokenError(Exception):
    pass


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload.parse_obj(payload)
    except (jwt.JWTError, ValidationError) as e:
        raise InvalidTokenError from e
