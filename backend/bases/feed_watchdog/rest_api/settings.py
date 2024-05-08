from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from feed_watchdog.domain.models import BaseModel


class AuthSettings(BaseModel):
    algorithm: str = "HS256"
    decode_algorithms: list[str] = [algorithm]
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 31  # 31 days
    jwt_secret_key: str
    jwt_refresh_secret_key: str


class RedisSettings(BaseModel):
    pub_sub_url: str = "redis://localhost:6379/2"


class MongoSettings(BaseModel):
    url: str = "mongodb://mongo:27017/feed_watchdog"


class SentrySettings(BaseModel):
    dsn: str = ""


class Interval(BaseModel):
    text: str
    value: str


class MessageTemplate(BaseModel):
    text: str
    value: str


class AppSettings(BaseModel):
    handlers_conf_path: str = "/app/fw_handlers_conf.yaml"
    intervals: list[Interval] = [
        Interval(text="At 6 AM", value="0 6 * * *"),
        Interval(text="At 6 PM", value="0 18 * * *"),
        Interval(text="Every 10 minutes", value="*/10 * * * *"),
        Interval(text="Every 30 minutes", value="*/30 * * * *"),
    ]
    message_templates: list[MessageTemplate] = [
        MessageTemplate(
            text="Default Telegram",
            value=(
                '<a href="${url}">${title}</a>\n\n'
                "${source_hash_tags}\n${post_hash_tags}"
            ),
        ),
    ]


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    auth: AuthSettings
    redis: RedisSettings = RedisSettings()
    mongo: MongoSettings = MongoSettings()
    sentry: SentrySettings = SentrySettings()

    model_config = SettingsConfigDict(
        env_prefix="FW_API_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
