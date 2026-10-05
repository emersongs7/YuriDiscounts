"""Carregamento centralizado de configuracoes da aplicacao (via .env)."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    mock_mode: bool = field(default_factory=lambda: os.getenv("MOCK_MODE", "true").lower() == "true")
    request_timeout: int = field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "10")))
    user_agent: str = field(
        default_factory=lambda: os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        )
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    min_match_score: float = field(default_factory=lambda: float(os.getenv("MIN_MATCH_SCORE", "55")))
    export_dir: Path = field(default_factory=lambda: Path(os.getenv("EXPORT_DIR", str(DATA_DIR))))
    products_file: Path = field(default_factory=lambda: DATA_DIR / "products.json")
    search_terms_file: Path = field(default_factory=lambda: DATA_DIR / "produtos_pesquisa.json")
    log_file: Path = field(default_factory=lambda: DATA_DIR / "search_log.txt")
    stores_file: Path = field(default_factory=lambda: CONFIG_DIR / "stores.json")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_stores_config() -> list[dict]:
    """Le a lista de lojas monitoradas a partir de config/stores.json."""
    settings = get_settings()
    if not settings.stores_file.exists():
        return []
    with open(settings.stores_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_search_terms() -> list[str]:
    """Le a lista de produtos a pesquisar a partir de data/produtos_pesquisa.json.

    O arquivo deve conter uma lista simples de strings, por exemplo:
        ["Dipirona 500mg", "Fralda Pampers Premium Care XXG"]
    """
    settings = get_settings()
    if not settings.search_terms_file.exists():
        return []
    with open(settings.search_terms_file, "r", encoding="utf-8") as f:
        conteudo = f.read().strip()
        if not conteudo:
            return []
        termos = json.loads(conteudo)
    return [t.strip() for t in termos if isinstance(t, str) and t.strip()]


def configure_logging() -> logging.Logger:
    """Configura logger raiz da aplicacao, gravando em data/search_log.txt."""
    settings = get_settings()
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("yuridiscounts")
    if logger.handlers:
        return logger

    logger.setLevel(settings.log_level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
