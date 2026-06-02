from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    openai_api_key: str = ""
    groq_api_key: str = ""
    tavily_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./research.db"
    chroma_persist_dir: str = "./chroma_db"
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    groq_model: str = "llama-3.3-70b-versatile"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
