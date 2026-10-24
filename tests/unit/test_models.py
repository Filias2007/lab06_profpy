from dataclasses import FrozenInstanceError

import pytest

from shop.exceptions import ValidationError
from shop.models import MAX_PRICE, MAX_QUANTITY, Product
from shop.value_objects import Money


def test_product_creation(laptop):
    assert laptop.product_id == 1
    assert laptop.name == "Laptop"
    assert laptop.category == "electronics"
    assert laptop.price == Money(35_000)
    assert laptop.quantity == 3


def test_default_quantity_is_zero():
    product = Product(1, "Pen", Money(10), "office")

    assert product.quantity == 0


@pytest.mark.parametrize(
    "product_id",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("1", id="string"),
        pytest.param(True, id="bool"),
        pytest.param(None, id="none"),
    ],
)
def test_invalid_product_id(product_factory, product_id):
    with pytest.raises(ValidationError, match="Product id"):
        product_factory(product_id=product_id)


@pytest.mark.parametrize("name", ["", "   ", None, 5])
def test_invalid_name(product_factory, name):
    with pytest.raises(ValidationError, match="Name"):
        product_factory(name=name)


@pytest.mark.parametrize("category", ["", "   ", None])
def test_invalid_category(product_factory, category):
    with pytest.raises(ValidationError, match="Category"):
        product_factory(category=category)


@pytest.mark.parametrize(
    "price",
    [
        pytest.param(0.01, id="minimum-valid"),
        pytest.param(1, id="one"),
        pytest.param(MAX_PRICE, id="maximum-valid"),
    ],
)
def test_price_boundaries_valid(product_factory, price):
    product = product_factory(price=price)

    assert product.price.amount == pytest.approx(price)


@pytest.mark.parametrize(
    ("price", "message"),
    [
        pytest.param(0, "positive", id="zero"),
        pytest.param(MAX_PRICE + 0.01, "exceed", id="above-maximum"),
    ],
)
def test_price_boundaries_invalid(product_factory, price, message):
    with pytest.raises(ValidationError, match=message):
        product_factory(price=price)


def test_price_must_be_money():
    with pytest.raises(ValidationError, match="Money"):
        Product(1, "Pen", 100, "office")


@pytest.mark.parametrize("quantity", [0, 1, MAX_QUANTITY])
def test_quantity_boundaries_valid(product_factory, quantity):
    assert product_factory(quantity=quantity).quantity == quantity


@pytest.mark.parametrize("quantity", [-1, MAX_QUANTITY + 1])
def test_quantity_out_of_range(product_factory, quantity):
    with pytest.raises(ValidationError, match="between"):
        product_factory(quantity=quantity)


@pytest.mark.parametrize("quantity", [2.5, "3", True, None])
def test_quantity_wrong_type(product_factory, quantity):
    with pytest.raises(ValidationError, match="integer"):
        product_factory(quantity=quantity)


def test_stock_value(laptop):
    assert laptop.stock_value.amount == pytest.approx(105_000)


def test_stock_value_of_empty_stock(product_factory):
    assert product_factory(quantity=0).stock_value.amount == 0


def test_product_is_immutable(laptop):
    with pytest.raises(FrozenInstanceError):
        laptop.quantity = 100