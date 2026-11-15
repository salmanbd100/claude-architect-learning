"""Application settings, loaded from environment variables and the project's .env file."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration. Each field is read from the env var of the same name (case-insensitive)."""

    # extra="ignore" lets .env hold variables WorkPilot doesn't know about without failing validation.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: SecretStr
    workpilot_model: str = "claude-opus-5-5"


@lru_cache
def get_settings() -> Settings:
    """Return the settings, loading them once on first call."""
    return Settings()  # type: ignore[call-arg]  # values come from the environment, not arguments
