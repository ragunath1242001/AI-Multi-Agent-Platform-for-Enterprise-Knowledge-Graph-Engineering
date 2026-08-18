from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "SemanticOps"
    environment: str = "development"
    database_url: str = Field(
        default="postgresql+psycopg://semanticops:semanticops@localhost:5432/semanticops"
    )
    fuseki_url: AnyHttpUrl = "http://localhost:3030/semanticops"
    fuseki_user: str = "admin"
    fuseki_password: str = "semanticops"
    knowledge_assets_dir: str = "../kg"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
