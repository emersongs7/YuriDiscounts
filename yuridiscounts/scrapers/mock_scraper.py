"""Scraper simulado (dados deterministicos) usado para validar o fluxo sem rede real."""
from __future__ import annotations

import hashlib
from decimal import Decimal

from yuridiscounts.core.exceptions import ProductNotFoundError
from yuridiscounts.core.models import Oferta
from yuridiscounts.scrapers.base import BaseScraper


class MockScraper(BaseScraper):
    """Gera ofertas simuladas para qualquer loja, com seed determinístico por termo+loja.

    Util para exercitar o fluxo completo (repositorio -> factory -> service ->
    relatorio) sem depender de acesso de rede aos sites reais das farmacias.
    """

    domain = "mock.local"

    def __init__(self, store_name: str = "Loja Simulada", **kwargs):
        super().__init__(**kwargs)
        self.store_name = store_name

    def _seed(self, termo: str) -> int:
        chave = f"{self.store_name}:{termo}".encode("utf-8")
        return int(hashlib.sha256(chave).hexdigest(), 16)

    def buscar(self, termo: str) -> list[Oferta]:
        seed = self._seed(termo)

        # ~1 em cada 11 combinacoes simula "produto nao encontrado" para
        # exercitar o tratamento de excecao no service layer.
        if seed % 11 == 0:
            raise ProductNotFoundError(f"'{termo}' nao encontrado em {self.store_name}")

        preco_base = Decimal(10 + (seed % 90)).quantize(Decimal("0.01"))
        tem_desconto = (seed % 3) != 0
        preco_promocional = None
        if tem_desconto:
            pct_desconto = Decimal(5 + (seed % 40))
            preco_promocional = (preco_base * (Decimal("100") - pct_desconto) / Decimal("100")).quantize(
                Decimal("0.01")
            )

        slug = termo.lower().replace(" ", "-")
        score = 90.0 + (seed % 10)

        oferta = Oferta(
            produto_termo=termo,
            loja=self.store_name,
            nome_encontrado=f"{termo} - {self.store_name}",
            preco_original=preco_base,
            preco_promocional=preco_promocional,
            url_produto=f"https://exemplo-mock.com.br/{slug}",
            score_match=min(score, 100.0),
        )
        return [oferta]
