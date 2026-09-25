"""Abstracao de notificacao (stub). Ponto de extensao para e-mail/Telegram/etc."""
from __future__ import annotations

from abc import ABC, abstractmethod

from yuridiscounts.core.models import ResultadoComparacao


class Notifier(ABC):
    @abstractmethod
    def notificar(self, resultado: ResultadoComparacao) -> None: ...


class ConsoleNotifier(Notifier):
    """Implementacao minima: apenas informa no console quando ha uma boa oferta."""

    def notificar(self, resultado: ResultadoComparacao) -> None:
        if resultado.melhor_preco is None:
            return
        print(
            f"[notificacao] Melhor oferta para '{resultado.produto_termo}': "
            f"{resultado.melhor_preco.loja} por R$ {resultado.melhor_preco.preco_final:.2f}"
        )
