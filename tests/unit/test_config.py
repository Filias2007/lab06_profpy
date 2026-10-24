import json

import pytest

from shop.config import (
    DEFAULT_MIN_STOCK,
    ShopConfig,
    get_min_stock,
    load_config,
)
from shop.exceptions import ConfigError


def test_default_min_stock():
    assert get_min_stock() == DEFAULT_MIN_STOCK == 5


def test_min_stock_from_environment(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "12")

    assert get_min_stock() == 12


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("5", 5), ("100", 100)])
def test_min_stock_boundaries(monkeypatch, raw, expected):
    monkeypatch.setenv("SHOP_MIN_STOCK", raw)

    assert get_min_stock() == expected


def test_environment_not_integer(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "abc")

    with pytest.raises(ConfigError, match="integer") as exc_info:
        get_min_stock()

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_environment_negative(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "-1")

    with pytest.raises(ConfigError, match="negative"):
        get_min_stock()


def test_environment_removed_returns_default(monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "9")
    monkeypatch.delenv("SHOP_MIN_STOCK", raising=False)

    assert get_min_stock() == DEFAULT_MIN_STOCK


def test_shop_config_defaults():
    assert ShopConfig() == ShopConfig(min_stock=5, currency="UAH")


def test_load_config_from_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"min_stock": 7, "currency": "USD"}), encoding="utf-8")

    assert load_config(path) == ShopConfig(min_stock=7, currency="USD")


def test_load_config_uses_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{}", encoding="utf-8")

    assert load_config(path) == ShopConfig()


def test_missing_config_file(tmp_path):
    with pytest.raises(ConfigError, match="Cannot read"):
        load_config(tmp_path / "missing.json")


def test_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ConfigError, match="invalid JSON"):
        load_config(path)


def test_config_must_be_object(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[1, 2]", encoding="utf-8")

    with pytest.raises(ConfigError, match="object"):
        load_config(path)


@pytest.mark.parametrize("value", [-1, "5", 2.5, True])
def test_invalid_min_stock_in_file(tmp_path, value):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"min_stock": value}), encoding="utf-8")

    with pytest.raises(ConfigError, match="min_stock"):
        load_config(path)


@pytest.mark.parametrize("value", ["", "  ", 5])
def test_invalid_currency_in_file(tmp_path, value):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"currency": value}), encoding="utf-8")

    with pytest.raises(ConfigError, match="currency"):
        load_config(path)