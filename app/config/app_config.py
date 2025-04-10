from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, EmailStr, field_validator, ValidationInfo
from enum import Enum
import secrets
import os
from collections.abc import Sequence

class Environment(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

class Settings(BaseSettings):
    # API
    PROJECT_NAME: str
    VERSION: str
    
    # Environment
    ENVIRONMENT: Environment
    DEBUG: bool
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    # SESSION_MAX_AGE: int
    
    # Rate Limiting
    RATE_LIMIT_TIMES: int
    RATE_LIMIT_SECONDS: int
    SESSION_MAX_AGE: int = 60

    # Server
    HOST: str = "0.0.0.0"
    PORT: int
    ALLOWED_HOSTS: List[str]

    # CORS
    CORS_ORIGINS: Sequence[str]
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | list) -> list:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid value for CORS_ORIGINS: {v}")

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    SQLALCHEMY_DATABASE_URI: str | None = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        values = info.data
        return (
            f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    # Redis
    REDIS_URL: str
    
    # Email
    # SMTP_TLS: bool = True
    # SMTP_PORT: int | None = None
    # SMTP_HOST: str | None = None
    # SMTP_USER: str | None = None
    # SMTP_PASSWORD: str | None = None
    # EMAILS_FROM_EMAIL: EmailStr | None = None
    # EMAILS_FROM_NAME: str | None = None
    
    # Monitoring
    # SENTRY_DSN: str | None = None
    
    # First Superuser
    FIRST_SUPERUSER_EMAIL: EmailStr | None = None
    FIRST_SUPERUSER_PASSWORD: str | None = None
    
    # Read from .env file
    _env_file: str = f"{os.path.dirname(os.path.abspath(__file__))}/../../envs/.{os.getenv("APP_ENV", "dev")}.env"
    print(f"Loading env file: {_env_file}")
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=_env_file,
        env_file_encoding="utf-8",
    )

    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEV

    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PROD
    
class RoutesName():
    API_V1: str = "/api/v1"

settings = Settings()
routes_name = RoutesName()