from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    app_name: str = "Optimize My Oura API"
    environment: str = "development"

    # Oura
    oura_personal_access_token: Optional[str] = None
    oura_client_id: Optional[str] = None
    oura_client_secret: Optional[str] = None
    oura_redirect_uri: Optional[str] = None
    oura_scopes: str = (
        "daily"
    )

    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


