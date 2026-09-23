from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4.1-mini"
    github_token: str = ""
    database_path: str = "./agent_runs.sqlite3"
    sandbox_image: str = "python:3.12-slim"
    sandbox_timeout_seconds: int = 180
    max_repo_files: int = 80
    max_file_bytes: int = 50_000


@lru_cache
def get_settings() -> Settings:
    return Settings()
