import json
from unittest.mock import Mock

import pytest

from shop.exceptions import DuplicateProductError, ImportDataError
from shop.exporters import export_json, export_products_json
from shop.importers import import_products
from shop.protocols import DiscountProvider
from shop.repositories import InMemoryProductRepository
from shop.services import CatalogService, PricingService

pytestmark = pytest.mark.integration


def run_pipeline(csv_path, output_path):
    catalog = CatalogService(InMemoryProductRepository())
    for product in import_products(csv_path):
        catalog.add_product(product)
    export_products_json(catalog.list_products(), output_path)
    return catalog


def test_csv_to_json_pipeline(products_csv, output_dir):
    target = output_dir / "products.json"

    catalog = run_pipeline(products_csv, target)

    data = json.loads(target.read_text(encoding="utf-8"))
    assert len(catalog.list_products()) == 4
    assert [item["name"] for item in data] == ["Laptop", "Mouse", "Desk", "Chair"]
    assert data[2]["price"] == pytest.approx(7_500.5)


def test_pipeline_stops_on_malformed_record(csv_factory, output_dir):
    csv_path = csv_factory(
        ["1,Laptop,electronics,35000,3", "2,Mouse,electronics,oops,20"]
    )
    target = output_dir / "products.json"

    with pytest.raises(ImportDataError) as exc_info:
        run_pipeline(csv_path, target)

    assert exc_info.value.line == 3
    assert not target.exists()


def test_pipeline_detects_duplicate_ids(csv_factory, output_dir):
    csv_path = csv_factory(
        ["1,Laptop,electronics,35000,3", "1,Phone,electronics,20000,4"]
    )

    with pytest.raises(DuplicateProductError):
        run_pipeline(csv_path, output_dir / "products.json")


def test_import_discount_export_pipeline(products_csv, output_dir):
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.side_effect = lambda category: {
        "electronics": 10,
        "furniture": 20,
    }[category]
    pricing = PricingService(provider)
    target = output_dir / "prices.json"

    products = import_products(products_csv)
    export_json(
        [
            {
                "id": p.product_id,
                "original": p.price.amount,
                "discounted": pricing.discounted_price(p).amount,
            }
            for p in products
        ],
        target,
    )

    data = json.loads(target.read_text(encoding="utf-8"))
    assert data[0]["discounted"] == pytest.approx(31_500)
    assert data[2]["discounted"] == pytest.approx(6_000.4)
    assert data[3]["discounted"] == pytest.approx(1_840)
    assert provider.get_discount.call_count == 4