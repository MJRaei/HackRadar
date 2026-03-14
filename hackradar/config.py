from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./hackradar.db"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # LLM (Google ADK)
    llm_model: str = "gemini-2.0-flash"
    google_api_key: str = ""

    # Embedding
    embedding_model: str = "allenai-specter"

    # Storage
    repos_base_dir: str = "./data/repos"


@lru_cache
def get_settings() -> Settings:
    return Settings()
