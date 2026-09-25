"""Service Layer: orquestra busca, matching e comparacao de ofertas."""
from __future__ import annotations

import logging

from yuridiscounts.core.exceptions import ScraperError
from yuridiscounts.core.models import Oferta, ResultadoComparacao
from yuridiscounts.scrapers.factory import ScraperFactory
from yuridiscounts.services.matcher import score_similaridade


class DiscountComparatorService:
    """Orquestra a busca em todas as lojas ativas e determina a melhor oferta."""

    def __init__(
        self,
        factory: ScraperFactory,
        lojas: list[dict],
        min_match_score: float = 55.0,
        logger: logging.Logger | None = None,
    ):
        self.factory = factory
        self.lojas = [loja for loja in lojas if loja.get("ativo", True)]
        self.min_match_score = min_match_score
        self.logger = logger or logging.getLogger("yuridiscounts")

    def comparar(self, termo_busca: str) -> ResultadoComparacao:
        ofertas: list[Oferta] = []

        for loja in self.lojas:
            try:
                scraper = self.factory.criar_por_nome_loja(loja["nome"], loja["dominio"])
                encontradas = scraper.buscar(termo_busca)
            except ScraperError as exc:
                self.logger.warning("Falha ao buscar '%s' em %s: %s", termo_busca, loja["nome"], exc)
                continue
            except Exception as exc:  # nunca deixa uma loja derrubar as demais
                self.logger.error("Erro inesperado em %s: %s", loja["nome"], exc)
                continue

            for oferta in encontradas:
                oferta.score_match = oferta.score_match or score_similaridade(
                    termo_busca, oferta.nome_encontrado
                )
                if oferta.score_match >= self.min_match_score:
                    ofertas.append(oferta)
                else:
                    self.logger.info(
                        "Oferta descartada por baixo score de match (%.1f): %s",
                        oferta.score_match,
                        oferta.nome_encontrado,
                    )

        if not ofertas:
            self.logger.warning("Nenhuma oferta valida encontrada para '%s'", termo_busca)
            return ResultadoComparacao(produto_termo=termo_busca)

        melhor_preco = min(ofertas, key=lambda o: o.preco_final)
        maior_desconto = max(ofertas, key=lambda o: o.desconto_pct)

        return ResultadoComparacao(
            produto_termo=termo_busca,
            melhor_preco=melhor_preco,
            maior_desconto=maior_desconto,
            todas_ofertas=sorted(ofertas, key=lambda o: o.preco_final),
        )

    def comparar_varios(self, termos_busca: list[str]) -> list[ResultadoComparacao]:
        return [self.comparar(termo) for termo in termos_busca]
