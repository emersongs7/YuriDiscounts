"""Fuzzy matching basico entre o termo buscado e o titulo retornado pela loja."""
from __future__ import annotations

try:
    from rapidfuzz import fuzz

    def score_similaridade(termo_busca: str, titulo_encontrado: str) -> float:
        return float(fuzz.token_set_ratio(termo_busca.lower(), titulo_encontrado.lower()))

except ImportError:  # fallback sem dependencia externa
    from difflib import SequenceMatcher

    def score_similaridade(termo_busca: str, titulo_encontrado: str) -> float:
        return SequenceMatcher(None, termo_busca.lower(), titulo_encontrado.lower()).ratio() * 100
