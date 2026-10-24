import pytest

from shop.services import build_report


def test_report_for_catalog(catalog):
    report = build_report(catalog, min_stock=5)

    assert report["total_products"] == 3
    assert report["total_stock_value"] == pytest.approx(166_502.5)
    assert report["most_expensive"] == "Laptop"
    assert report["low_stock"] == ["Laptop"]


def test_report_for_empty_catalog(empty_catalog):
    report = build_report(empty_catalog, min_stock=5)

    assert report == {
        "total_products": 0,
        "total_stock_value": 0,
        "most_expensive": None,
        "low_stock": [],
    }