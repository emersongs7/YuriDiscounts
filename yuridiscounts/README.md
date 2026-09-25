# YuriDiscounts

Comparador de preços de produtos em redes de farmácias brasileiras (Drogarias
Pacheco, Drogaria São Paulo, Droga Raia, Panvel), com recomendação da melhor
oferta por menor preço final e maior percentual de desconto.

## Arquitetura

- **Strategy** (`yuridiscounts/scrapers/base.py` + implementações por loja): cada
  farmácia tem sua própria classe de extração, implementando `BaseScraper`.
- **Factory Method** (`yuridiscounts/scrapers/factory.py`): `ScraperFactory`
  resolve a estratégia correta a partir da URL ou do nome/domínio da loja.
- **Repository** (`yuridiscounts/repositories/`): `JsonProductRepository`
  persiste os termos de busca em `data/products.json`, desacoplado da
  interface `ProductRepository` (pode ser trocado por SQLite no futuro).
- **Service Layer** (`yuridiscounts/services/comparator.py`):
  `DiscountComparatorService` orquestra busca, fuzzy matching e ranking.
- **Modelos Pydantic** (`yuridiscounts/core/models.py`): `Produto`, `Oferta`,
  `Loja`, `ResultadoComparacao`, com `Decimal` para valores monetários e
  cálculo automático do percentual de desconto.

## Modo mock (sem rede real)

Os sites reais das farmácias ainda não foram fornecidos/validados, então os
scrapers concretos (`pacheco_scraper.py`, `drogaria_sp_scraper.py`,
`droga_raia_scraper.py`, `panvel_scraper.py`) são **esqueletos** com
seletores CSS provisórios (marcados com `# TODO`), a serem ajustados quando
as URLs reais de busca forem informadas.

Para validar o fluxo completo (CLI → repositório → factory → comparação →
relatório) sem depender de rede, existe um `MockScraper` que gera ofertas
simuladas determinísticas. Ative com `MOCK_MODE=true` no `.env` (padrão) ou
com a flag `--mock` no CLI.

## Setup

```sh
py -3.14 -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env
```

## Uso (CLI)

```sh
# Gerenciar produtos monitorados
python main.py produto add --termo "dipirona 500mg"
python main.py produto list
python main.py produto remove --termo "dipirona 500mg"

# Comparar preços
python main.py comparar --termo "dipirona 500mg" --mock
python main.py comparar --todos --mock --export json
```

## Testes

```sh
.venv/Scripts/python.exe -m pytest -v
```

## Próximos passos

- Fornecer as URLs reais de busca de cada farmácia e ajustar os seletores
  CSS marcados com `# TODO` nos scrapers concretos.
- Avaliar `robots.txt` e termos de uso de cada site antes de rodar scraping
  real em produção.
- Migrar `BaseScraper.buscar` para `async def` (httpx/aiohttp) caso seja
  necessário paralelizar buscas em muitas lojas/produtos.
- Adicionar rate limiting/backoff mais sofisticado nos scrapers reais.
