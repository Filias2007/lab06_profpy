import json
from unittest.mock import Mock, call

import pytest

from shop.config import load_config
from shop.exceptions import DuplicateProductError
from shop.exporters import export_products_json, export_report
from shop.importers import import_products
from shop.protocols import Notifier
from shop.repositories import SqliteProductRepository
from shop.services import CatalogService, StockAlertService, build_report

pytestmark = pytest.mark.integration

MANAGER = "manager@shop.ua"


def test_full_application_flow_with_sqlite(tmp_path, products_csv, output_dir):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"min_stock": 5, "currency": "UAH"}), encoding="utf-8"
    )
    config = load_config(config_file)
    notifier = Mock(spec=Notifier)

    with SqliteProductRepository(tmp_path / "shop.db") as repository:
        catalog = CatalogService(repository)
        for product in import_products(products_csv, currency=config.currency):
            catalog.add_product(product)

        sent = StockAlertService(catalog, notifier, config.min_stock).notify_low_stock(
            MANAGER
        )
        export_products_json(catalog.list_products(), output_dir / "products.json")
        export_report(build_report(catalog, config.min_stock), output_dir / "report.json")

    products = json.loads((output_dir / "products.json").read_text(encoding="utf-8"))
    report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert sent == 2
    assert notifier.send.call_args_list == [
        call(MANAGER, "Low stock: Laptop (3 left)"),
        call(MANAGER, "Low stock: Chair (2 left)"),
    ]
    assert [item["name"] for item in products] == ["Laptop", "Mouse", "Desk", "Chair"]
    assert report["total_stock_value"] == pytest.approx(171_102.5)
    assert report["most_expensive"] == "Laptop"


def test_sqlite_catalog_survives_restart(tmp_path, products_csv):
    path = tmp_path / "shop.db"
    with SqliteProductRepository(path) as repository:
        catalog = CatalogService(repository)
        for product in import_products(products_csv):
            catalog.add_product(product)

    with SqliteProductRepository(path) as reopened:
        catalog = CatalogService(reopened)

        assert catalog.most_expensive().name == "Laptop"
        assert catalog.total_stock_value().amount == pytest.approx(171_102.5)


def test_sqlite_catalog_rejects_duplicate(tmp_path, products_csv):
    with SqliteProductRepository(tmp_path / "shop.db") as repository:
        catalog = CatalogService(repository)
        products = import_products(products_csv)
        catalog.add_product(products[0])

        with pytest.raises(DuplicateProductError):
            catalog.add_product(products[0])