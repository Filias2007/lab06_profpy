import pytest

from shop.exceptions import ValidationError
from shop.validators import validate_email, validate_percent


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        pytest.param("anna@example.com", "anna@example.com", id="normal"),
        pytest.param("a@b.co", "a@b.co", id="shortest"),
        pytest.param("  manager@shop.ua ", "manager@shop.ua", id="trimmed"),
    ],
)
def test_valid_email(email, expected):
    assert validate_email(email) == expected


@pytest.mark.parametrize(
    "email",
    [
        pytest.param("", id="empty"),
        pytest.param("plain", id="no-at"),
        pytest.param("a@b", id="no-domain-dot"),
        pytest.param("@shop.ua", id="no-local-part"),
        pytest.param("a b@c.com", id="space-inside"),
        pytest.param(None, id="none"),
        pytest.param(5, id="number"),
    ],
)
def test_invalid_email(email):
    with pytest.raises(ValidationError, match="Invalid email"):
        validate_email(email)


@pytest.mark.parametrize("percent", [0, 0.01, 50, 99.99, 100])
def test_valid_percent(percent):
    assert validate_percent(percent) == pytest.approx(percent)


@pytest.mark.parametrize(
    "percent",
    [
        pytest.param(-0.01, id="below-minimum"),
        pytest.param(100.01, id="above-maximum"),
        pytest.param("10", id="string"),
        pytest.param(None, id="none"),
        pytest.param(True, id="bool"),
        pytest.param(float("nan"), id="nan"),
    ],
)
def test_invalid_percent(percent):
    with pytest.raises(ValidationError, match="between 0 and 100"):
        validate_percent(percent)