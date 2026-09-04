from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path




class Settings(BaseSettings):
    DATABASE_URL: str
   

    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str


    DARAJA_CONSUMER_KEY: str
    DARAJA_CONSUMER_SECRET: str
    DARAJA_SHORTCODE: str
    DARAJA_PASSKEY: str
    REGISTRATION_CALLBACK_URL: str
    PERMIT_CALLBACK_URL:str


    SMS_API_URL: str
    SMS_API_KEY: str
    SMS_SENDER_ID: str
    SMS_API_SECRET:str


    MPESA_ENVIRONMENT: str = "sandbox"


    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    ADMIN_FIRST_NAME: str = "System"
    ADMIN_LAST_NAME: str = "Administrator"
    ADMIN_EMAIL: str
    ADMIN_PHONE: str
    ADMIN_PASSWORD: str

    USSD_API_KEY: str
    AT_SHORTCODE:str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )




settings = Settings()
settings.JWT_PRIVATE_KEY = Path(settings.JWT_PRIVATE_KEY).read_text()
settings.JWT_PUBLIC_KEY = Path(settings.JWT_PUBLIC_KEY).read_text()


