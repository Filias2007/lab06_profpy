import random
from unittest.mock import Mock

import pytest

from shop.exceptions import DiscountProviderError, PricingError
from shop.protocols import DiscountProvider
from shop.services import PricingService


def test_seeded_random_is_deterministic():
    """Experiment 5: a seeded generator makes a random-based test repeatable."""
    first = random.Random(42)
    second = random.Random(42)

    assert [first.randint(1, 100) for _ in range(5)] == [
        second.randint(1, 100) for _ in range(5)
    ]


def test_monkeypatch_makes_random_deterministic(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.75)

    assert random.random() > 0.5


@pytest.mark.parametrize("run", [1, 2, 3])
def test_tmp_path_is_isolated_between_runs(tmp_path, run):
    """Experiment 6: every run gets a fresh temporary directory."""
    target = tmp_path / "result.txt"
    assert not target.exists()

    target.write_text(f"run {run}", encoding="utf-8")

    assert target.read_text(encoding="utf-8") == f"run {run}"


def test_dependency_success_path(laptop):
    """Experiment 7, success: the provider is called and the price changes."""
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.return_value = 10

    result = PricingService(provider).discounted_price(laptop)

    assert result.amount == pytest.approx(31_500)
    provider.get_discount.assert_called_once_with("electronics")


def test_dependency_failure_path(laptop):
    """Experiment 7, failure: error is translated and no price is produced."""
    provider = Mock(spec=DiscountProvider)
    provider.get_discount.side_effect = DiscountProviderError("down")
    service = PricingService(provider)

    with pytest.raises(PricingError):
        service.discounted_price(laptop)

    provider.get_discount.assert_called_once_with("electronics")