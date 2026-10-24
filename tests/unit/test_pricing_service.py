from unittest.mock import Mock

import pytest

from shop.exceptions import DiscountProviderError, PricingError
from shop.protocols import DiscountProvider
from shop.services import PricingService


def make_provider():
    return Mock(spec=DiscountProvider)


def test_discount_applied(laptop):
    provider = make_provider()
    provider.get_discount.return_value = 10

    result = PricingService(provider).discounted_price(laptop)

    assert result.amount == pytest.approx(31_500)
    assert result.currency == "UAH"
    provider.get_discount.assert_called_once_with("electronics")


@pytest.mark.parametrize(
    ("percent", "expected"),
    [
        pytest.param(0, 100, id="no-discount"),
        pytest.param(10, 90, id="ten"),
        pytest.param(25, 75, id="quarter"),
        pytest.param(100, 0, id="full"),
    ],
)
def test_discount_values(product_factory, percent, expected):
    provider = make_provider()
    provider.get_discount.return_value = percent

    result = PricingService(provider).discounted_price(product_factory(price=100))

    assert result.amount == pytest.approx(expected)


def test_provider_returns_different_values(laptop):
    provider = make_provider()
    provider.get_discount.side_effect = [10, 20]
    service = PricingService(provider)

    first = service.discounted_price(laptop)
    second = service.discounted_price(laptop)

    assert first.amount == pytest.approx(31_500)
    assert second.amount == pytest.approx(28_000)
    assert provider.get_discount.call_count == 2


def test_provider_failure_raises_pricing_error(laptop):
    provider = make_provider()
    provider.get_discount.side_effect = DiscountProviderError("timeout")

    with pytest.raises(PricingError, match="unavailable") as exc_info:
        PricingService(provider).discounted_price(laptop)

    assert isinstance(exc_info.value.__cause__, DiscountProviderError)


@pytest.mark.parametrize("percent", [-1, 100.01, 150])
def test_invalid_discount_from_provider(laptop, percent):
    provider = make_provider()
    provider.get_discount.return_value = percent

    with pytest.raises(PricingError, match="Invalid discount"):
        PricingService(provider).discounted_price(laptop)