"""Modelos de dominio (Pydantic): Produto, Loja, Oferta, ResultadoComparacao."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class Loja(BaseModel):
    nome: str
    dominio: str
    base_url: HttpUrl
    ativo: bool = True


class Produto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    termo_busca: str
    categoria: str | None = None
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("termo_busca")
    @classmethod
    def termo_nao_vazio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("termo_busca nao pode ser vazio")
        return v


class Oferta(BaseModel):
    produto_termo: str
    loja: str
    nome_encontrado: str
    preco_original: Decimal
    preco_promocional: Decimal | None = None
    desconto_pct: Decimal = Decimal("0")
    url_produto: HttpUrl
    coletado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    score_match: float = 0.0

    @field_validator("preco_original")
    @classmethod
    def preco_original_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("preco_original deve ser maior que zero")
        return v

    @field_validator("preco_promocional")
    @classmethod
    def preco_promocional_valido(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError("preco_promocional nao pode ser negativo")
        return v

    @model_validator(mode="after")
    def calcular_desconto(self) -> "Oferta":
        if self.preco_promocional is not None and self.preco_promocional < self.preco_original:
            desconto = (
                (self.preco_original - self.preco_promocional) / self.preco_original * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            object.__setattr__(self, "desconto_pct", desconto)
        else:
            object.__setattr__(self, "desconto_pct", Decimal("0.00"))
        return self

    @property
    def preco_final(self) -> Decimal:
        return self.preco_promocional if self.preco_promocional is not None else self.preco_original


class ResultadoComparacao(BaseModel):
    produto_termo: str
    melhor_preco: Oferta | None = None
    maior_desconto: Oferta | None = None
    todas_ofertas: list[Oferta] = Field(default_factory=list)
