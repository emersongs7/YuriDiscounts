from yuridiscounts.scrapers.factory import ScraperFactory
from yuridiscounts.services.comparator import DiscountComparatorService

LOJAS = [
    {"nome": "Drogarias Pacheco", "dominio": "drogariaspacheco.com.br", "ativo": True},
    {"nome": "Drogaria São Paulo", "dominio": "drogariasaopaulo.com.br", "ativo": True},
    {"nome": "Droga Raia", "dominio": "drogaraia.com.br", "ativo": True},
    {"nome": "Panvel", "dominio": "panvel.com", "ativo": True},
]


def test_comparar_com_mock_retorna_resultado_coerente():
    factory = ScraperFactory(mock_mode=True)
    service = DiscountComparatorService(factory, LOJAS, min_match_score=0)

    resultado = service.comparar("dipirona 500mg")

    assert resultado.produto_termo == "dipirona 500mg"
    assert len(resultado.todas_ofertas) > 0
    assert resultado.melhor_preco is not None
    assert resultado.maior_desconto is not None

    precos = [o.preco_final for o in resultado.todas_ofertas]
    assert resultado.melhor_preco.preco_final == min(precos)

    descontos = [o.desconto_pct for o in resultado.todas_ofertas]
    assert resultado.maior_desconto.desconto_pct == max(descontos)


def test_comparar_varios_termos():
    factory = ScraperFactory(mock_mode=True)
    service = DiscountComparatorService(factory, LOJAS, min_match_score=0)

    resultados = service.comparar_varios(["dipirona 500mg", "fralda pampers xg"])

    assert len(resultados) == 2
    assert {r.produto_termo for r in resultados} == {"dipirona 500mg", "fralda pampers xg"}
