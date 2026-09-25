"""Implementacao do ProductRepository persistindo em um arquivo JSON."""
from __future__ import annotations

import json
import os
from pathlib import Path

from yuridiscounts.core.exceptions import (
    ProductAlreadyExistsError,
    ProductNotRegisteredError,
)
from yuridiscounts.core.models import Produto
from yuridiscounts.repositories.base_repository import ProductRepository


class JsonProductRepository(ProductRepository):
    """Armazena a lista de produtos/termos de busca em um arquivo JSON local."""

    def __init__(self, arquivo: Path | str):
        self._arquivo = Path(arquivo)
        self._arquivo.parent.mkdir(parents=True, exist_ok=True)
        if not self._arquivo.exists():
            self._escrever([])

    def _ler(self) -> list[dict]:
        if not self._arquivo.exists():
            return []
        with open(self._arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            return json.loads(conteudo) if conteudo else []

    def _escrever(self, dados: list[dict]) -> None:
        tmp = self._arquivo.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
        os.replace(tmp, self._arquivo)

    def adicionar(self, termo_busca: str, categoria: str | None = None) -> Produto:
        if self.buscar_por_termo(termo_busca) is not None:
            raise ProductAlreadyExistsError(f"Produto '{termo_busca}' ja cadastrado")
        produto = Produto(termo_busca=termo_busca, categoria=categoria)
        dados = self._ler()
        dados.append(json.loads(produto.model_dump_json()))
        self._escrever(dados)
        return produto

    def remover(self, termo_busca: str) -> None:
        dados = self._ler()
        novos = [d for d in dados if d["termo_busca"].lower() != termo_busca.lower()]
        if len(novos) == len(dados):
            raise ProductNotRegisteredError(f"Produto '{termo_busca}' nao encontrado")
        self._escrever(novos)

    def atualizar(self, termo_busca_atual: str, novo_termo: str) -> Produto:
        dados = self._ler()
        for d in dados:
            if d["termo_busca"].lower() == termo_busca_atual.lower():
                d["termo_busca"] = novo_termo
                self._escrever(dados)
                return Produto(**d)
        raise ProductNotRegisteredError(f"Produto '{termo_busca_atual}' nao encontrado")

    def listar(self) -> list[Produto]:
        return [Produto(**d) for d in self._ler()]

    def buscar_por_termo(self, termo_busca: str) -> Produto | None:
        for d in self._ler():
            if d["termo_busca"].lower() == termo_busca.lower():
                return Produto(**d)
        return None
