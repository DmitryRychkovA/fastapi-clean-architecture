from src.config import (
    LocalSettings,
    ProductionSettings,
    Settings,
)
from src.config import TestSettings as AppTestSettings


class TestSettingsFactory:
    def test_local_settings_defaults(self, monkeypatch):
        for k in ("APP_ENV", "DATABASE_URL"):
            monkeypatch.delenv(k, raising=False)
        s = LocalSettings(_env_file=None)
        assert s.debug is True
        assert s.app_env == "local"

    def test_production_settings(self, monkeypatch):
        for k in ("APP_ENV", "DATABASE_URL"):
            monkeypatch.delenv(k, raising=False)
        s = ProductionSettings(_env_file=None)
        assert s.debug is False
        assert s.app_env == "production"

    def test_test_settings(self, monkeypatch):
        for k in ("APP_ENV", "DATABASE_URL"):
            monkeypatch.delenv(k, raising=False)
        s = AppTestSettings(_env_file=None)
        assert s.debug is False
        assert s.testing is True
        assert "sqlite" in s.database_url

    def test_rabbitmq_url_property(self):
        s = Settings(
            rabbitmq_user="user", rabbitmq_password="pass",
            rabbitmq_host="rabbit", rabbitmq_port=5672, rabbitmq_vhost="/",
        )
        assert s.rabbitmq_url == "amqp://user:pass@rabbit:5672//"

    def test_redis_url_property(self):
        s = Settings(redis_host="redis-host", redis_port=6379, redis_db=0, redis_password="")
        assert s.redis_url == "redis://redis-host:6379/0"

    def test_redis_url_with_password(self):
        s = Settings(
            redis_password="secret123", redis_host="localhost",
            redis_port=6379, redis_db=0,
        )
        assert ":secret123@" in s.redis_url
