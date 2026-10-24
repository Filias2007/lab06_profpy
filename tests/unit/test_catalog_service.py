import pytest

from shop.exceptions import (
    DuplicateProductError,
    EmptyCatalogError,
    ProductNotFoundError,
    ValidationError,
)


def names(products):
    return [product.name for product in products]


def test_add_product_stores_it(empty_catalog, laptop):
    empty_catalog.add_product(laptop)

    assert empty_catalog.get_product(1) == laptop


def test_duplicate_product_rejected(catalog, laptop):
    with pytest.raises(DuplicateProductError, match="already exists"):
        catalog.add_product(laptop)


def test_get_unknown_product(catalog):
    with pytest.raises(ProductNotFoundError, match="999"):
        catalog.get_product(999)


def test_list_products(catalog):
    assert names(catalog.list_products()) == ["Laptop", "Mouse", "Desk"]


def test_search_by_name(catalog):
    assert names(catalog.search("lap")) == ["Laptop"]


def test_search_is_case_insensitive(catalog):
    assert names(catalog.search("MOUSE")) == ["Mouse"]


def test_search_without_match(catalog):
    assert catalog.search("tablet") == []


def test_filter_by_category(catalog):
    assert names(catalog.filter_by_category("electronics")) == ["Laptop", "Mouse"]


def test_filter_by_category_is_case_insensitive(catalog):
    assert names(catalog.filter_by_category("  FURNITURE ")) == ["Desk"]


def test_filter_unknown_category(catalog):
    assert catalog.filter_by_category("toys") == []


def test_total_stock_value(catalog):
    assert catalog.total_stock_value().amount == pytest.approx(166_502.5)


def test_total_stock_value_of_empty_catalog(empty_catalog):
    assert empty_catalog.total_stock_value().amount == 0


def test_total_stock_value_with_mixed_currencies(empty_catalog, product_factory):
    empty_catalog.add_product(product_factory(product_id=9, currency="USD"))

    with pytest.raises(ValidationError, match="Currency mismatch"):
        empty_catalog.total_stock_value()


def test_most_expensive(catalog):
    assert catalog.most_expensive().name == "Laptop"


def test_most_expensive_of_empty_catalog(empty_catalog):
    with pytest.raises(EmptyCatalogError, match="empty"):
        empty_catalog.most_expensive()


@pytest.mark.parametrize(
    ("min_stock", "expected"),
    [
        pytest.param(0, [], id="zero-threshold"),
        pytest.param(3, [], id="equal-to-lowest-is-not-low"),
        pytest.param(4, ["Laptop"], id="just-above-lowest"),
        pytest.param(5, ["Laptop"], id="equal-to-desk-is-not-low"),
        pytest.param(6, ["Laptop", "Desk"], id="two-low"),
    ],
)
def test_low_stock_boundaries(catalog, min_stock, expected):
    assert names(catalog.low_stock(min_stock)) == expected


def test_low_stock_negative_threshold(catalog):
    with pytest.raises(ValidationError, match="negative"):
        catalog.low_stock(-1)