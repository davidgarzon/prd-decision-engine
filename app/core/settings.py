from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "prd-decision-engine"
    debug: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
