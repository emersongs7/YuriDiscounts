"""Scraper (esqueleto) para Droga Raia.

Seletores CSS provisorios - ajustar quando a URL real de busca for fornecida.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup

from yuridiscounts.core.exceptions import DomParsingError, ProductNotFoundError
from yuridiscounts.core.models import Oferta
from yuridiscounts.scrapers.base import BaseScraper


class DrogaRaiaScraper(BaseScraper):
    store_name = "Droga Raia"
    domain = "drogaraia.com.br"

    BASE_URL = "https://www.drogaraia.com.br"
    SEARCH_PATH = "/busca"

    def buscar(self, termo: str) -> list[Oferta]:
        url = f"{self.BASE_URL}{self.SEARCH_PATH}"
        resposta = self._fazer_request_com_retry(url, params={"q": termo})

        try:
            soup = BeautifulSoup(resposta.text, "lxml")
            # TODO: validar seletor real quando a URL de busca for confirmada.
            item = soup.select_one("div.product-summary, li.shelf-item")
            if item is None:
                raise ProductNotFoundError(f"'{termo}' nao encontrado em {self.store_name}")

            nome_el = item.select_one(".product-name, .shelf-item__title")
            preco_original_el = item.select_one(".old-price, .shelf-item__old-price")
            preco_promocional_el = item.select_one(".best-price, .shelf-item__price")
            link_el = item.select_one("a")

            if nome_el is None or preco_promocional_el is None or link_el is None:
                raise DomParsingError(f"Estrutura HTML inesperada em {self.store_name}")

            preco_promocional = self._parse_preco(preco_promocional_el.get_text())
            preco_original = (
                self._parse_preco(preco_original_el.get_text()) if preco_original_el else preco_promocional
            )
            link = link_el.get("href", "")
            if link and not link.startswith("http"):
                link = f"{self.BASE_URL}{link}"

            oferta = Oferta(
                produto_termo=termo,
                loja=self.store_name,
                nome_encontrado=nome_el.get_text(strip=True),
                preco_original=preco_original,
                preco_promocional=preco_promocional,
                url_produto=link or self.BASE_URL,
            )
            return [oferta]
        except (ProductNotFoundError, DomParsingError):
            raise
        except Exception as exc:
            raise DomParsingError(f"Falha ao interpretar pagina de {self.store_name}: {exc}") from exc

    @staticmethod
    def _parse_preco(texto: str) -> Decimal:
        limpo = texto.strip().replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return Decimal(limpo)
        except InvalidOperation as exc:
            raise DomParsingError(f"Preco invalido: '{texto}'") from exc
