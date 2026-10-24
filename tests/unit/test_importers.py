import pytest

from shop.exceptions import ImportDataError
from shop.importers import import_products


def test_import_valid_file(products_csv):
    products = import_products(products_csv)

    assert len(products) == 4
    assert products[0].name == "Laptop"
    assert products[0].price.amount == pytest.approx(35_000)
    assert products[2].price.amount == pytest.approx(7_500.5)
    assert products[3].quantity == 2


def test_import_header_only_returns_empty_list(csv_factory):
    assert import_products(csv_factory([])) == []


def test_import_with_custom_currency(products_csv):
    products = import_products(products_csv, currency="USD")

    assert {p.price.currency for p in products} == {"USD"}


def test_import_empty_file(csv_factory):
    path = csv_factory([], header="")

    with pytest.raises(ImportDataError, match="empty"):
        import_products(path)


def test_import_missing_columns(csv_factory):
    path = csv_factory([], header="id,name\n")

    with pytest.raises(ImportDataError, match="Missing columns"):
        import_products(path)


def test_import_missing_file(tmp_path):
    with pytest.raises(ImportDataError, match="Cannot read") as exc_info:
        import_products(tmp_path / "missing.csv")

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


@pytest.mark.parametrize(
    "row",
    [
        pytest.param("1,Laptop,electronics,abc,3", id="price-not-a-number"),
        pytest.param("x,Laptop,electronics,100,3", id="id-not-a-number"),
        pytest.param("1,Laptop,electronics,100,3.5", id="quantity-not-integer"),
        pytest.param("1,Laptop,electronics,-5,3", id="negative-price"),
        pytest.param("1,Laptop,electronics,0,3", id="zero-price"),
        pytest.param("1,,electronics,100,3", id="empty-name"),
        pytest.param("1,Laptop,electronics,100,-1", id="negative-quantity"),
        pytest.param("0,Laptop,electronics,100,3", id="zero-id"),
        pytest.param("1,Laptop,electronics", id="missing-fields"),
    ],
)
def test_malformed_record(csv_factory, row):
    path = csv_factory([row])

    with pytest.raises(ImportDataError, match="line 2") as exc_info:
        import_products(path)

    assert exc_info.value.line == 2
    assert exc_info.value.__cause__ is not None


def test_error_reports_correct_line(csv_factory):
    path = csv_factory(["1,Laptop,electronics,100,3", "2,Mouse,electronics,oops,3"])

    with pytest.raises(ImportDataError) as exc_info:
        import_products(path)

    assert exc_info.value.line == 3
    assert isinstance(exc_info.value.__cause__, ValueError)