from __future__ import annotations


class ShopError(Exception):
    """Base class for all shop errors."""


class ValidationError(ShopError, ValueError):
    """Invalid value passed to a model or value object."""


class DuplicateProductError(ShopError):
    """Product with the same id already exists."""


class ProductNotFoundError(ShopError):
    """Product was not found."""


class EmptyCatalogError(ShopError):
    """Operation is impossible for an empty catalog."""


class ImportDataError(ShopError):
    """CSV import failed (missing file, bad header, malformed record)."""

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


class ConfigError(ShopError):
    """Invalid or unreadable configuration."""


class DiscountProviderError(ShopError):
    """External discount provider failed."""


class PricingError(ShopError):
    """Price could not be calculated."""


class NotificationError(ShopError):
    """Notification could not be delivered."""


class ProviderError(ShopError):
    """External (async) stock provider failed."""