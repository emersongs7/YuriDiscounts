"""Interface do Repository de produtos (Repository Pattern)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from yuridiscounts.core.models import Produto


class ProductRepository(ABC):
    """Contrato de acesso a dados dos termos de busca (produtos)."""

    @abstractmethod
    def adicionar(self, termo_busca: str, categoria: str | None = None) -> Produto: ...

    @abstractmethod
    def remover(self, termo_busca: str) -> None: ...

    @abstractmethod
    def atualizar(self, termo_busca_atual: str, novo_termo: str) -> Produto: ...

    @abstractmethod
    def listar(self) -> list[Produto]: ...

    @abstractmethod
    def buscar_por_termo(self, termo_busca: str) -> Produto | None: ...
