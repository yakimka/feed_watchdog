from datetime import datetime, timedelta, timezone
from typing import Any, Union

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from picodi import Provide, inject
from pydantic import BaseModel, ValidationError

from feed_watchdog.rest_api.dependencies import get_option

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", scheme_name="JWT")


def _create_token(
    subject: Union[str, Any],
    expires_minutes: int,
    secret: str,
    algorithm: str,
) -> str:
    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    return jwt.encode(to_encode, secret, algorithm)


@inject
def create_access_token(
    subject: Union[str, Any],
    expires_minutes: int = Provide(get_option("auth.access_token_expire_minutes")),
    secret: str = Provide(get_option("auth.jwt_secret_key")),
    algorithm: str = Provide(get_option("auth.algorithm")),
) -> str:
    return _create_token(
        subject,
        expires_minutes=expires_minutes,
        secret=secret,
        algorithm=algorithm,
    )


@inject
def create_refresh_token(
    subject: Union[str, Any],
    expires_minutes: int = Provide(get_option("auth.refresh_token_expire_minutes")),
    secret: str = Provide(get_option("auth.jwt_refresh_secret_key")),
    algorithm: str = Provide(get_option("auth.algorithm")),
) -> str:
    return _create_token(
        subject,
        expires_minutes=expires_minutes,
        secret=secret,
        algorithm=algorithm,
    )


class TokenPayload(BaseModel):
    sub: str
    exp: int


class InvalidTokenError(Exception):
    pass


@inject
def decode_token(
    token: str,
    *,
    secret: str,
    algorithms: list[str] = Provide(get_option("auth.decode_algorithms")),
) -> TokenPayload:
    try:
        payload = jwt.decode(token, secret, algorithms=algorithms)
        return TokenPayload.parse_obj(payload)
    except (jwt.JWTError, ValidationError) as e:
        raise InvalidTokenError from e
