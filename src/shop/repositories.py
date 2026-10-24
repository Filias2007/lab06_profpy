from __future__ import annotations

from shop.models import Product


class InMemoryProductRepository:
    """Simple fake/real repository that keeps products in a dict."""

    def __init__(self) -> None:
        self._items: dict[int, Product] = {}

    def add(self, product: Product) -> None:
        self._items[product.product_id] = product

    def get(self, product_id: int) -> Product | None:
        return self._items.get(product_id)

    def list_all(self) -> list[Product]:
        return list(self._items.values())

    def __len__(self) -> int:
        return len(self._items)