from pathlib import Path
from typing import Dict, Optional, Any

from pydantic import AnyUrl, BaseSettings, EmailStr, validator

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # DEBUG
    DEBUG: bool

    # TOKENS
    EMAIL_OTP_EXPIRE_SECONDS: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    # SECURITY
    SECRET_KEY: str

    # PROJECT DETAILS
    PROJECT_NAME: str
    FRONTEND_URL: str
    CORS_ALLOWED_ORIGINS: Any

    # POSTGRESQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URL: Optional[str] = None

    # FIRST SUPERUSER
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # FIRST AUCTIONEER
    FIRST_AUCTIONEER_EMAIL: EmailStr
    FIRST_AUCTIONEER_PASSWORD: str

    # FIRST REVIEWER
    FIRST_REVIEWER_EMAIL: EmailStr
    FIRST_REVIEWER_PASSWORD: str

    # EMAIL CONFIG
    MAIL_SENDER_EMAIL: str
    MAIL_SENDER_PASSWORD: str
    MAIL_SENDER_HOST: str
    MAIL_SENDER_PORT: int

    # CLOUDINARY CONFIG
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    @validator("SQLALCHEMY_DATABASE_URL", pre=True)
    def assemble_postgres_connection(
        cls, v: Optional[str], values: Dict[str, str]
    ) -> str:

        # Assemble postgres url
        if isinstance(v, str):
            return v
        if values.get("DEBUG"):
            postgres_server = "localhost"
        else:
            postgres_server = values.get("POSTGRES_SERVER")

        return AnyUrl.build(
            scheme="postgresql+psycopg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=postgres_server or "localhost",
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB')}",
        )

    @validator("CORS_ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        return v.split()

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings: Settings = Settings()
