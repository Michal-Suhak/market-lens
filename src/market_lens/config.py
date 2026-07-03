from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProvider = Literal["gemini", "groq", "openai"]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config.yaml"


class Paths(BaseModel):
    data_dir: Path
    prices_dir: Path
    documents_dir: Path


class Secrets(BaseSettings):
    database_url: str = "sqlite:///data/market_lens.db"
    qdrant_url: str = "http://localhost:6333"
    fred_api_key: str = ""
    groq_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Config(BaseModel):
    pairs: list[str]
    windows_hours: list[int]
    paths: Paths
    llm_provider: LLMProvider
    llm_temperature: float = 0.0  # deterministic output for reproducible predictions
    secrets: Secrets = Field(default_factory=Secrets)


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    data = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    return Config(**data)
