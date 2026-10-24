from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from shop.exceptions import ConfigError

DEFAULT_MIN_STOCK = 5
DEFAULT_CURRENCY = "UAH"
ENV_MIN_STOCK = "SHOP_MIN_STOCK"


@dataclass(frozen=True)
class ShopConfig:
    min_stock: int = DEFAULT_MIN_STOCK
    currency: str = DEFAULT_CURRENCY


def get_min_stock() -> int:
    """Read minimal stock threshold from the SHOP_MIN_STOCK environment variable."""
    raw = os.getenv(ENV_MIN_STOCK)
    if raw is None:
        return DEFAULT_MIN_STOCK
    try:
        value = int(raw)
    except ValueError as error:
        raise ConfigError(f"{ENV_MIN_STOCK} must be an integer, got {raw!r}") from error
    if value < 0:
        raise ConfigError(f"{ENV_MIN_STOCK} must not be negative")
    return value


def load_config(path: Path) -> ShopConfig:
    """Load configuration from a JSON file."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError(f"Cannot read config file: {path}") from error
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ConfigError("Config contains invalid JSON") from error
    if not isinstance(data, dict):
        raise ConfigError("Config must be a JSON object")

    min_stock = data.get("min_stock", DEFAULT_MIN_STOCK)
    if isinstance(min_stock, bool) or not isinstance(min_stock, int) or min_stock < 0:
        raise ConfigError("min_stock must be a non-negative integer")

    currency = data.get("currency", DEFAULT_CURRENCY)
    if not isinstance(currency, str) or not currency.strip():
        raise ConfigError("currency must be a non-empty string")

    return ShopConfig(min_stock=min_stock, currency=currency)