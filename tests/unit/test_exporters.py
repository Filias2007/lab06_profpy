import json

import pytest

import shop.exporters as exporters
from shop.exporters import (
    export_json,
    export_products_json,
    export_report,
    product_to_dict,
)


def test_product_to_dict(laptop):
    assert product_to_dict(laptop) == {
        "id": 1,
        "name": "Laptop",
        "category": "electronics",
        "price": 35_000,
        "currency": "UAH",
        "quantity": 3,
    }


def test_export_products(output_dir, products):
    target = output_dir / "products.json"

    count = export_products_json(products, target)

    data = json.loads(target.read_text(encoding="utf-8"))
    assert count == 3
    assert [item["name"] for item in data] == ["Laptop", "Mouse", "Desk"]
    assert data[2]["price"] == pytest.approx(7_500.5)


def test_export_keeps_unicode(output_dir, product_factory):
    target = output_dir / "products.json"

    export_products_json([product_factory(name="Ноутбук")], target)

    text = target.read_text(encoding="utf-8")
    assert "Ноутбук" in text
    assert "\\u" not in text


def test_export_empty_list(output_dir):
    target = output_dir / "empty.json"

    assert export_products_json([], target) == 0
    assert json.loads(target.read_text(encoding="utf-8")) == []


def test_export_report(output_dir):
    target = output_dir / "report.json"
    report = {"total_products": 2, "most_expensive": "Laptop"}

    export_report(report, target)

    assert json.loads(target.read_text(encoding="utf-8")) == report


def test_export_overwrites_existing_file(output_dir):
    target = output_dir / "data.json"
    target.write_text("old", encoding="utf-8")

    export_json({"new": True}, target)

    assert json.loads(target.read_text(encoding="utf-8")) == {"new": True}


def test_failed_replace_keeps_old_file(output_dir, products, monkeypatch):
    """Atomic output: old valid data survives, temporary file is removed."""
    target = output_dir / "products.json"
    target.write_text("old valid data", encoding="utf-8")

    def broken_replace(source, destination):
        raise OSError("disk error")

    monkeypatch.setattr(exporters.os, "replace", broken_replace)

    with pytest.raises(OSError, match="disk error"):
        export_products_json(products, target)

    assert target.read_text(encoding="utf-8") == "old valid data"
    assert not (output_dir / "products.json.tmp").exists()


def test_serialization_failure_keeps_old_file(output_dir):
    target = output_dir / "data.json"
    target.write_text("old valid data", encoding="utf-8")

    with pytest.raises(TypeError):
        export_json({"bad": object()}, target)

    assert target.read_text(encoding="utf-8") == "old valid data"


def test_export_to_missing_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        export_json({"a": 1}, tmp_path / "missing" / "data.json")