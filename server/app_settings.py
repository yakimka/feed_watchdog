from enum import Enum

from domain.models import BaseModel
from pydantic import BaseSettings


class AuthSettings(BaseSettings):
    auth_on: bool = True
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 31  # 31 days
    jwt_secret_key: str
    jwt_refresh_secret_key: str


class RedisSettings(BaseModel):
    PUB_SUB_URL: str = "redis://localhost:6379"


class MongoSettings(BaseModel):
    URL: str = "mongodb://mongo:27017/feed_watchdog"


class Interval(BaseModel):
    text: str
    value: str


class AppSettings(BaseModel):
    intervals: list[Interval] = [
        Interval(text="At 6 AM", value="0 6 * * *"),
        Interval(text="At 6 PM", value="0 18 * * *"),
        Interval(text="Every 10 minutes", value="*/10 * * * *"),
        Interval(text="Every 30 minutes", value="*/30 * * * *"),
    ]


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    redis: RedisSettings = RedisSettings()
    mongo: MongoSettings = MongoSettings()


class Topic(Enum):
    STREAMS = "streams"
