from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_name: str = Field(default="Bankroll Risk API")
    app_version: str = Field(default="0.1.0")
    api_v1_prefix: str = Field(default="/v1")


@lru_cache
def get_settings() -> Settings:
    return Settings()
