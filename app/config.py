"""Configurações centralizadas via pydantic-settings — lê de .env e variáveis de ambiente."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centralizadas da aplicação — carregadas via pydantic-settings de .env e variáveis de ambiente."""

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
    allowed_origins: str = "http://localhost:3000"
    observability_stack: str = "floci"
    floci_endpoint: str = "http://floci:4566"
    aws_region: str = "us-east-1"
    xray_daemon_address: str = "floci:2000"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
