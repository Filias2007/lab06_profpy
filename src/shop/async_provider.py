from __future__ import annotations

from dataclasses import replace

from shop.exceptions import ProviderError
from shop.models import Product
from shop.protocols import AsyncStockClient


class AsyncStockProvider:
    """Refreshes product quantities from an external async system."""

    def __init__(self, client: AsyncStockClient) -> None:
        self._client = client

    async def fetch_quantity(self, product_id: int) -> int:
        try:
            data = await self._client.fetch_stock(product_id)
        except ConnectionError as error:
            raise ProviderError(f"Stock provider unavailable for {product_id}") from error
        if "quantity" not in data:
            raise ProviderError("Provider response has no 'quantity' field")
        return data["quantity"]

    async def refresh(self, product: Product) -> Product:
        quantity = await self.fetch_quantity(product.product_id)
        return replace(product, quantity=quantity)

    async def refresh_all(self, products: list[Product]) -> list[Product]:
        return [await self.refresh(product) for product in products]