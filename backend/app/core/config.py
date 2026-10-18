from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "FRPEWS - Flood Risk Prediction & Early Warning System"
    secret_key: str = "dev-secret-change-in-production"
    database_url: str = "sqlite+aiosqlite:///./frpews.db"
    access_token_expire_minutes: int = 60 * 24

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Seed admin
    admin_email: str = "admin@frpews.local"
    admin_password: str = "Admin123!"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
