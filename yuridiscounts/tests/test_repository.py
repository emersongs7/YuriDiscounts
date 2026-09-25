import pytest

from yuridiscounts.core.exceptions import (
    ProductAlreadyExistsError,
    ProductNotRegisteredError,
)
from yuridiscounts.repositories.json_product_repository import JsonProductRepository


@pytest.fixture
def repo(tmp_path):
    return JsonProductRepository(tmp_path / "products.json")


def test_adicionar_e_listar(repo):
    repo.adicionar("dipirona 500mg")
    produtos = repo.listar()
    assert len(produtos) == 1
    assert produtos[0].termo_busca == "dipirona 500mg"


def test_adicionar_duplicado_lanca_erro(repo):
    repo.adicionar("dipirona 500mg")
    with pytest.raises(ProductAlreadyExistsError):
        repo.adicionar("dipirona 500mg")


def test_remover(repo):
    repo.adicionar("dipirona 500mg")
    repo.remover("dipirona 500mg")
    assert repo.listar() == []


def test_remover_inexistente_lanca_erro(repo):
    with pytest.raises(ProductNotRegisteredError):
        repo.remover("nao existe")


def test_atualizar(repo):
    repo.adicionar("dipirona 500mg")
    atualizado = repo.atualizar("dipirona 500mg", "dipirona 1g")
    assert atualizado.termo_busca == "dipirona 1g"
    assert repo.buscar_por_termo("dipirona 1g") is not None
