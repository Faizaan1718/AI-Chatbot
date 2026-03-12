from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))


@dataclass
class AppConfig:
    model_path: str = os.getenv("MODEL_PATH", str(ROOT_DIR / "models" / "checkpoints" / "ecommerce-support"))
    base_model_name: str = os.getenv("BASE_MODEL_NAME", "microsoft/DialoGPT-small")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    max_history_turns: int = int(os.getenv("MAX_HISTORY_TURNS", "8"))


def get_config() -> AppConfig:
    return AppConfig()

