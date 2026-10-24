import json
from unittest.mock import AsyncMock

import pytest

from shop.async_provider import AsyncStockProvider
from shop.exceptions import ProviderError
from shop.exporters import export_products_json, export_report
from shop.importers import import_products
from shop.repositories import InMemoryProductRepository
from shop.services import CatalogService, build_report

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_import_refresh_export_flow(products_csv, output_dir):
    client = AsyncMock()
    client.fetch_stock.side_effect = [
        {"quantity": 10},
        {"quantity": 20},
        {"quantity": 0},
        {"quantity": 8},
    ]
    provider = AsyncStockProvider(client)

    refreshed = await provider.refresh_all(import_products(products_csv))

    catalog = CatalogService(InMemoryProductRepository())
    for product in refreshed:
        catalog.add_product(product)
    export_products_json(catalog.list_products(), output_dir / "products.json")
    export_report(build_report(catalog, 5), output_dir / "report.json")

    products = json.loads((output_dir / "products.json").read_text(encoding="utf-8"))
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert [item["quantity"] for item in products] == [10, 20, 0, 8]
    assert report["total_stock_value"] == pytest.approx(392_400)
    assert report["low_stock"] == ["Desk"]
    assert client.fetch_stock.await_count == 4


async def test_provider_failure_stops_the_flow(products_csv, output_dir):
    client = AsyncMock()
    client.fetch_stock.side_effect = [{"quantity": 10}, ConnectionError("down")]
    provider = AsyncStockProvider(client)
    target = output_dir / "products.json"

    with pytest.raises(ProviderError):
        refreshed = await provider.refresh_all(import_products(products_csv))
        export_products_json(refreshed, target)

    assert not target.exists()
    assert client.fetch_stock.await_count == 2