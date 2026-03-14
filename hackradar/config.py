from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./hackradar.db"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # LLM provider selection
    # Options: gemini | openai | openai_compatible
    llm_provider: str = "gemini"

    # Model name — interpreted by the selected provider:
    #   gemini:            "gemini-2.0-flash", "gemini-2.5-pro", ...
    #   openai:            "gpt-4o", "gpt-4o-mini", ...
    #   openai_compatible: "gpt-oss-120b", or any model served by your endpoint
    llm_model: str = "gemini-2.0-flash"

    # Google credentials (required for llm_provider=gemini)
    google_api_key: str = ""

    # OpenAI credentials (required for llm_provider=openai or openai_compatible)
    openai_api_key: str = "test"

    # Custom base URL for OpenAI-compatible self-hosted endpoints.
    # Example (GPT-OSS hackathon server):
    #   https://vjioo4r1vyvcozuj.us-east-2.aws.endpoints.huggingface.cloud/v1
    # Leave empty when llm_provider=openai (uses OpenAI's default endpoint).
    openai_base_url: str = ""

    # Embedding
    embedding_model: str = "allenai-specter"

    # Storage
    repos_base_dir: str = "./data/repos"


@lru_cache
def get_settings() -> Settings:
    return Settings()
