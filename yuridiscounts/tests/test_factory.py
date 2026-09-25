import pytest

from yuridiscounts.core.exceptions import UnsupportedStoreError
from yuridiscounts.scrapers.factory import ScraperFactory
from yuridiscounts.scrapers.mock_scraper import MockScraper
from yuridiscounts.scrapers.pacheco_scraper import PachecoScraper


def test_factory_resolve_por_url():
    factory = ScraperFactory(mock_mode=False)
    scraper = factory.criar_por_url("https://www.drogariaspacheco.com.br/busca?q=x")
    assert isinstance(scraper, PachecoScraper)


def test_factory_dominio_desconhecido():
    factory = ScraperFactory(mock_mode=False)
    with pytest.raises(UnsupportedStoreError):
        factory.criar_por_url("https://www.loja-inexistente.com.br")


def test_factory_mock_mode_sempre_devolve_mock():
    factory = ScraperFactory(mock_mode=True)
    scraper = factory.criar_por_url("https://www.drogariaspacheco.com.br")
    assert isinstance(scraper, MockScraper)


def test_listar_lojas_suportadas():
    lojas = ScraperFactory.listar_lojas_suportadas()
    assert "Drogarias Pacheco" in lojas
    assert "Panvel" in lojas
