from decimal import Decimal

import pytest
from pydantic import ValidationError

from yuridiscounts.core.models import Oferta


def test_desconto_calculado_automaticamente():
    oferta = Oferta(
        produto_termo="dipirona",
        loja="Loja X",
        nome_encontrado="Dipirona 500mg",
        preco_original=Decimal("20.00"),
        preco_promocional=Decimal("15.00"),
        url_produto="https://exemplo.com/produto",
    )
    assert oferta.desconto_pct == Decimal("25.00")
    assert oferta.preco_final == Decimal("15.00")


def test_sem_promocao_desconto_zero():
    oferta = Oferta(
        produto_termo="dipirona",
        loja="Loja X",
        nome_encontrado="Dipirona 500mg",
        preco_original=Decimal("20.00"),
        url_produto="https://exemplo.com/produto",
    )
    assert oferta.desconto_pct == Decimal("0.00")
    assert oferta.preco_final == Decimal("20.00")


def test_preco_negativo_invalido():
    with pytest.raises(ValidationError):
        Oferta(
            produto_termo="x",
            loja="Loja X",
            nome_encontrado="X",
            preco_original=Decimal("-1"),
            url_produto="https://exemplo.com/produto",
        )
