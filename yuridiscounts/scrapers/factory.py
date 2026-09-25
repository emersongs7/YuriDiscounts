"""Factory Method: escolhe a estrategia de scraper correta por URL/dominio/nome."""
from __future__ import annotations

from urllib.parse import urlparse

from yuridiscounts.core.exceptions import UnsupportedStoreError
from yuridiscounts.scrapers.base import BaseScraper
from yuridiscounts.scrapers.droga_raia_scraper import DrogaRaiaScraper
from yuridiscounts.scrapers.drogaria_sp_scraper import DrogariaSaoPauloScraper
from yuridiscounts.scrapers.mock_scraper import MockScraper
from yuridiscounts.scrapers.pacheco_scraper import PachecoScraper
from yuridiscounts.scrapers.panvel_scraper import PanvelScraper


class ScraperFactory:
    """Factory Method que resolve a estrategia (BaseScraper) correta.

    Quando `mock_mode=True`, sempre devolve um `MockScraper`, permitindo
    validar o fluxo completo sem depender de acesso de rede aos sites reais.
    """

    _registry: dict[str, type[BaseScraper]] = {
        PachecoScraper.domain: PachecoScraper,
        DrogariaSaoPauloScraper.domain: DrogariaSaoPauloScraper,
        DrogaRaiaScraper.domain: DrogaRaiaScraper,
        PanvelScraper.domain: PanvelScraper,
    }

    def __init__(self, mock_mode: bool = False, timeout: int = 10, user_agent: str | None = None):
        self.mock_mode = mock_mode
        self.timeout = timeout
        self.user_agent = user_agent

    def criar_por_url(self, url: str) -> BaseScraper:
        dominio = urlparse(url).netloc.replace("www.", "") or url.replace("www.", "")
        return self._criar(dominio)

    def criar_por_nome_loja(self, nome_loja: str, dominio: str) -> BaseScraper:
        if self.mock_mode:
            return MockScraper(store_name=nome_loja, timeout=self.timeout, user_agent=self.user_agent)
        return self._criar(dominio)

    def _criar(self, dominio: str) -> BaseScraper:
        if self.mock_mode:
            return MockScraper(timeout=self.timeout, user_agent=self.user_agent)

        classe = self._registry.get(dominio)
        if classe is None:
            raise UnsupportedStoreError(f"Nenhum scraper registrado para o dominio '{dominio}'")
        return classe(timeout=self.timeout, user_agent=self.user_agent)

    @classmethod
    def listar_lojas_suportadas(cls) -> list[str]:
        return [scraper_cls.store_name for scraper_cls in cls._registry.values()]
