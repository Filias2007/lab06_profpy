import pytest

from shop.exceptions import ValidationError
from shop.value_objects import Money


def test_money_creation():
    money = Money(100, "UAH")

    assert money.amount == 100
    assert money.currency == "UAH"


def test_default_currency_is_uah():
    assert Money(10).currency == "UAH"


def test_money_keeps_any_currency(currency):
    assert Money(5, currency).currency == currency


def test_negative_money_rejected():
    with pytest.raises(ValidationError, match="negative"):
        Money(-1, "UAH")


def test_validation_error_is_value_error():
    with pytest.raises(ValueError):
        Money(-0.01)


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        pytest.param(0, 0, id="zero"),
        pytest.param(0.01, 0.01, id="minimum-positive"),
        pytest.param(100, 100, id="integer"),
        pytest.param(9999.99, 9999.99, id="large"),
    ],
)
def test_valid_money_amounts(amount, expected):
    assert Money(amount).amount == pytest.approx(expected)


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param("10", id="string"),
        pytest.param(None, id="none"),
        pytest.param(True, id="bool"),
    ],
)
def test_invalid_amount_type_or_value(amount):
    with pytest.raises(ValidationError, match="finite number"):
        Money(amount)


@pytest.mark.parametrize("currency_value", ["", "   ", None])
def test_empty_currency_rejected(currency_value):
    with pytest.raises(ValidationError, match="Currency"):
        Money(10, currency_value)


def test_money_addition():
    assert Money(100) + Money(50) == Money(150)


def test_currency_mismatch():
    with pytest.raises(ValidationError, match="Currency mismatch"):
        Money(100, "UAH") + Money(10, "USD")


def test_adding_non_money_is_type_error():
    with pytest.raises(TypeError):
        Money(1) + 5


def test_multiplication():
    result = Money(100) * 3

    assert result.amount == pytest.approx(300)
    assert result.currency == "UAH"


def test_negative_factor_rejected():
    with pytest.raises(ValidationError, match="negative"):
        Money(100) * -1