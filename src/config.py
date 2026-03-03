import os
from enum import StrEnum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    project_name: str = "Medical Study Metadata API"
    app_env: str = "local"
    debug: bool = True
    testing: bool = False
    api_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/medical_db"
    pool_size: int = 10
    max_overflow: int = 20

    # RabbitMQ
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    rabbit_pool_size: int = 2
    rabbit_channel_pool_size: int = 10

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_cache_ttl: int = 3600

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/{self.rabbitmq_vhost}"
        )

    @property
    def redis_url(self) -> str:
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


class LocalSettings(Settings):
    debug: bool = True
    app_env: str = "local"


class ProductionSettings(Settings):
    debug: bool = False
    app_env: str = "production"


class TestSettings(Settings):
    debug: bool = False
    testing: bool = True
    app_env: str = "testing"
    database_url: str = "sqlite+aiosqlite:///test.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "local")
    config_map: dict[str, type[Settings]] = {
        "local": LocalSettings,
        "production": ProductionSettings,
        "testing": TestSettings,
    }
    return config_map.get(env, LocalSettings)()


settings = get_settings()
