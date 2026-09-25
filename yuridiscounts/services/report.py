"""Geracao do relatorio consolidado: tabela no terminal + exportacao JSON/CSV."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from tabulate import tabulate

from yuridiscounts.core.models import ResultadoComparacao


def imprimir_relatorio(resultados: list[ResultadoComparacao]) -> None:
    for resultado in resultados:
        print(f"\n=== {resultado.produto_termo} ===")
        if not resultado.todas_ofertas:
            print("Nenhuma oferta valida encontrada.")
            continue

        linhas = [
            [
                oferta.loja,
                oferta.nome_encontrado,
                f"R$ {oferta.preco_final:.2f}",
                f"{oferta.desconto_pct:.2f}%",
                oferta.url_produto,
            ]
            for oferta in resultado.todas_ofertas
        ]
        print(tabulate(linhas, headers=["Loja", "Produto", "Preço final", "Desconto", "Link"]))

        if resultado.melhor_preco:
            print(
                f"\n>> Melhor preço: {resultado.melhor_preco.loja} - "
                f"R$ {resultado.melhor_preco.preco_final:.2f}"
            )
        if resultado.maior_desconto:
            print(
                f">> Maior desconto: {resultado.maior_desconto.loja} - "
                f"{resultado.maior_desconto.desconto_pct:.2f}%"
            )


def exportar(resultados: list[ResultadoComparacao], formato: str, export_dir: Path) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    destino = export_dir / f"relatorio_{timestamp}.{formato}"

    if formato == "json":
        payload = [json.loads(r.model_dump_json()) for r in resultados]
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    elif formato == "csv":
        with open(destino, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["produto_termo", "loja", "nome_encontrado", "preco_final", "desconto_pct", "url"])
            for resultado in resultados:
                for oferta in resultado.todas_ofertas:
                    writer.writerow(
                        [
                            resultado.produto_termo,
                            oferta.loja,
                            oferta.nome_encontrado,
                            f"{oferta.preco_final:.2f}",
                            f"{oferta.desconto_pct:.2f}",
                            str(oferta.url_produto),
                        ]
                    )
    else:
        raise ValueError(f"Formato de exportacao nao suportado: {formato}")

    return destino
