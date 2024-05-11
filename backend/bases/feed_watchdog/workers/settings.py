from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from feed_watchdog.domain.models import BaseModel


class AppSettings(BaseModel):
    api_base_url: str = "http://feed_watchdog_api:8000/api"
    api_token: str
    api_timeout: int = 30
    handlers_conf_path: str = "/app/fw_handlers_conf.yaml"
    streams_topic: str = "feed_watchdog:streams"
    messages_topic: str = "feed_watchdog:messages"


class RedisSettings(BaseModel):
    storage_url: str = "redis://redis:6379/1"
    pub_sub_url: str = "redis://redis:6379/2"


class SentrySettings(BaseModel):
    dsn: str = ""


class Settings(BaseSettings):
    app: AppSettings
    redis: RedisSettings = RedisSettings()
    sentry: SentrySettings = SentrySettings()

    model_config = SettingsConfigDict(
        env_prefix="FW_WRK_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
