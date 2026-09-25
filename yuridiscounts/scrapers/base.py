"""Interface Strategy para os extratores (scrapers) de cada farmacia."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod

import requests

from yuridiscounts.core.exceptions import ScraperBlockedError, ScraperTimeoutError
from yuridiscounts.core.models import Oferta


class BaseScraper(ABC):
    """Estrategia comum a todos os scrapers de farmacias (Strategy Pattern).

    A assinatura de `buscar` foi desenhada para poder ser trocada por uma
    variante `async def buscar` (com httpx/aiohttp) sem alterar o restante
    do fluxo, caso seja necessario paralelizar as buscas no futuro.
    """

    store_name: str
    domain: str

    def __init__(self, timeout: int = 10, user_agent: str | None = None, max_retries: int = 2):
        self.timeout = timeout
        self.user_agent = user_agent or "YuriDiscounts/1.0"
        self.max_retries = max_retries

    @abstractmethod
    def buscar(self, termo: str) -> list[Oferta]:
        """Busca o termo na loja e retorna as ofertas encontradas.

        Deve lancar `ProductNotFoundError` quando nada relevante for
        encontrado, e `DomParsingError` quando o HTML nao puder ser
        interpretado como esperado.
        """
        raise NotImplementedError

    def _fazer_request_com_retry(self, url: str, params: dict | None = None) -> requests.Response:
        """Hook de infraestrutura com headers realistas, timeout e retry/backoff."""
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }
        ultimo_erro: Exception | None = None
        for tentativa in range(1, self.max_retries + 1):
            try:
                resposta = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                if resposta.status_code in (403, 429):
                    raise ScraperBlockedError(
                        f"{self.store_name} bloqueou a requisicao (status {resposta.status_code})"
                    )
                resposta.raise_for_status()
                return resposta
            except requests.Timeout as exc:
                ultimo_erro = ScraperTimeoutError(f"Timeout ao acessar {self.store_name}: {exc}")
            except ScraperBlockedError as exc:
                ultimo_erro = exc
                break
            except requests.RequestException as exc:
                ultimo_erro = ScraperBlockedError(f"Erro de rede ao acessar {self.store_name}: {exc}")
            time.sleep(0.5 * tentativa)
        assert ultimo_erro is not None
        raise ultimo_erro
