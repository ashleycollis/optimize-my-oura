from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    app_name: str = "Optimize My Oura API"
    environment: str = "development"
    database_url: str = "sqlite:///./oura.db"

    # Oura
    oura_personal_access_token: Optional[str] = None
    oura_client_id: Optional[str] = None
    oura_client_secret: Optional[str] = None
    oura_redirect_uri: Optional[str] = None
    oura_scopes: str = (
        "daily"
    )

    # Frontend removed; open CORS configured in app.main during rebuild

    # LLM (Ollama) optional
    ollama_enabled: bool = False
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"


@lru_cache
def get_settings() -> Settings:
    return Settings()


