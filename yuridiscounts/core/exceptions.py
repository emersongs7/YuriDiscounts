"""Hierarquia de excecoes customizadas do YuriDiscounts."""


class YuriDiscountsError(Exception):
    """Excecao base de toda a aplicacao."""


class ScraperError(YuriDiscountsError):
    """Erro generico ocorrido durante a coleta de dados em uma loja."""


class ScraperTimeoutError(ScraperError):
    """A requisicao ao site da loja excedeu o tempo limite."""


class ScraperBlockedError(ScraperError):
    """A loja bloqueou a requisicao (403, captcha, anti-bot, etc.)."""


class ProductNotFoundError(ScraperError):
    """Nenhum produto correspondente foi encontrado na loja."""


class DomParsingError(ScraperError):
    """A estrutura HTML da pagina mudou e o parsing falhou."""


class ScraperFactoryError(YuriDiscountsError):
    """Erro ao resolver/instanciar uma estrategia de scraper."""


class UnsupportedStoreError(ScraperFactoryError):
    """A loja/dominio informado nao possui scraper registrado."""


class RepositoryError(YuriDiscountsError):
    """Erro generico de acesso ao repositorio de produtos."""


class ProductAlreadyExistsError(RepositoryError):
    """O termo de busca ja esta cadastrado."""


class ProductNotRegisteredError(RepositoryError):
    """O termo de busca informado nao esta cadastrado."""
