"""Configurações centralizadas via pydantic-settings — lê de .env e variáveis de ambiente."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://user:password@localhost:5432/safehire_auth"
    )
    database_url_sync: str = (
        "postgresql+psycopg2://user:password@localhost:5432/safehire_auth"
    )
    secret_key: str = "change-me-to-a-long-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    app_name: str = "SafeHire Auth Service"
    debug: bool = True
    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8001

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
