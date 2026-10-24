import json
from unittest.mock import Mock

import pytest

from shop.config import load_config
from shop.exporters import export_report
from shop.importers import import_products
from shop.protocols import Notifier
from shop.repositories import InMemoryProductRepository
from shop.services import CatalogService, StockAlertService, build_report

pytestmark = pytest.mark.integration


def build_catalog(products):
    catalog = CatalogService(InMemoryProductRepository())
    for product in products:
        catalog.add_product(product)
    return catalog


def test_config_file_import_report_export(tmp_path, products_csv, output_dir):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({"min_stock": 5, "currency": "UAH"}), encoding="utf-8"
    )
    config = load_config(config_file)

    catalog = build_catalog(import_products(products_csv, currency=config.currency))
    report = build_report(catalog, config.min_stock)
    export_report(report, output_dir / "report.json")

    saved = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
    assert saved["total_products"] == 4
    assert saved["total_stock_value"] == pytest.approx(171_102.5)
    assert saved["most_expensive"] == "Laptop"
    assert saved["low_stock"] == ["Laptop", "Chair"]


def test_environment_threshold_controls_notifications(products_csv, monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "3")
    catalog = build_catalog(import_products(products_csv))
    notifier = Mock(spec=Notifier)

    sent = StockAlertService(catalog, notifier).notify_low_stock("boss@shop.ua")

    assert sent == 1
    notifier.send.assert_called_once_with("boss@shop.ua", "Low stock: Chair (2 left)")