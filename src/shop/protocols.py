from __future__ import annotations

from typing import Protocol

from shop.models import Product


class ProductRepository(Protocol):
    def add(self, product: Product) -> None:
        """Store (or replace) a product."""

    def get(self, product_id: int) -> Product | None:
        """Return product by id or None."""

    def list_all(self) -> list[Product]:
        """Return all stored products."""


class DiscountProvider(Protocol):
    def get_discount(self, category: str) -> float:
        """Return discount percent (0..100) for a category."""


class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None:
        """Send a notification."""


class AsyncStockClient(Protocol):
    async def fetch_stock(self, product_id: int) -> dict:
        """Fetch stock information from an external system."""