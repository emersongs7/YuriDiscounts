"""YuriDiscounts - CLI de comparacao de precos em farmacias."""
from __future__ import annotations

import argparse
import sys

if __package__ in (None, ""):
    # Permite executar este arquivo diretamente (ex.: "Debug Python File" do
    # VSCode), adicionando a raiz do projeto ao sys.path para que o pacote
    # "yuridiscounts" seja encontrado.
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from yuridiscounts.config.settings import (
    configure_logging,
    get_settings,
    load_search_terms,
    load_stores_config,
)
from yuridiscounts.core.exceptions import RepositoryError, YuriDiscountsError
from yuridiscounts.repositories.json_product_repository import JsonProductRepository
from yuridiscounts.scrapers.factory import ScraperFactory
from yuridiscounts.services.comparator import DiscountComparatorService
from yuridiscounts.services.report import exportar, imprimir_relatorio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yuridiscounts", description="Comparador de precos")
    sub = parser.add_subparsers(dest="comando", required=True)

    produto = sub.add_parser("produto", help="Gerenciar produtos monitorados")
    produto_sub = produto.add_subparsers(dest="acao", required=True)

    p_add = produto_sub.add_parser("add", help="Produtos....")
    p_add.add_argument("--termo", required=True)
    p_add.add_argument("--categoria", default=None)

    p_remove = produto_sub.add_parser("remove", help="Remover um termo de busca")
    p_remove.add_argument("--termo", required=True)

    produto_sub.add_parser("list", help="Listar produtos cadastrados")

    comparar = sub.add_parser("comparar", help="Comparar precos entre lojas")
    comparar.add_argument("--termo", help="Termo especifico a comparar")
    comparar.add_argument("--todos", action="store_true", help="Comparar todos os produtos cadastrados")
    comparar.add_argument(
        "--lista",
        action="store_true",
        help="Comparar todos os produtos definidos em data/produtos_pesquisa.json",
    )
    comparar.add_argument("--mock", action="store_true", help="Forcar uso de dados simulados")
    comparar.add_argument("--export", choices=["json", "csv"], default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = get_settings()
    logger = configure_logging()
    repo = JsonProductRepository(settings.products_file)

    try:
        if args.comando == "produto":
            if args.acao == "add":
                produto = repo.adicionar(args.termo, args.categoria)
                print(f"Produto adicionado: {produto.termo_busca}")
            elif args.acao == "remove":
                repo.remover(args.termo)
                print(f"Produto removido: {args.termo}")
            elif args.acao == "list":
                produtos = repo.listar()
                if not produtos:
                    print("Nenhum produto cadastrado.")
                for p in produtos:
                    print(f"- {p.termo_busca} (categoria: {p.categoria or 'N/A'})")

        elif args.comando == "comparar":
            mock_mode = args.mock or settings.mock_mode
            factory = ScraperFactory(mock_mode=mock_mode, timeout=settings.request_timeout, user_agent=settings.user_agent)
            lojas = load_stores_config()
            service = DiscountComparatorService(factory, lojas, min_match_score=settings.min_match_score, logger=logger)

            if args.todos:
                termos = [p.termo_busca for p in repo.listar()]
                if not termos:
                    print("Nenhum produto cadastrado para comparar.")
                    return 0
            elif args.lista:
                termos = load_search_terms()
                if not termos:
                    print(f"Nenhum produto encontrado em {settings.search_terms_file}.")
                    return 0
            elif args.termo:
                termos = [args.termo]
            else:
                parser.error("Informe --termo, --todos ou --lista")
                return 1

            resultados = service.comparar_varios(termos)
            imprimir_relatorio(resultados)

            if args.export:
                destino = exportar(resultados, args.export, settings.export_dir)
                print(f"\nRelatorio exportado para: {destino}")

        return 0
    except (RepositoryError, YuriDiscountsError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
