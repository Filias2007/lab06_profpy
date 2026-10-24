from __future__ import annotations

from shop.config import get_min_stock
from shop.exceptions import (
    DiscountProviderError,
    DuplicateProductError,
    EmptyCatalogError,
    PricingError,
    ProductNotFoundError,
    ValidationError,
)
from shop.models import Product
from shop.protocols import DiscountProvider, Notifier, ProductRepository
from shop.value_objects import Money
from shop.validators import validate_email, validate_percent


class CatalogService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def add_product(self, product: Product) -> None:
        if self._repository.get(product.product_id) is not None:
            raise DuplicateProductError(f"Product {product.product_id} already exists")
        self._repository.add(product)

    def get_product(self, product_id: int) -> Product:
        product = self._repository.get(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found")
        return product

    def list_products(self) -> list[Product]:
        return list(self._repository.list_all())

    def search(self, text: str) -> list[Product]:
        needle = text.strip().lower()
        return [p for p in self._repository.list_all() if needle in p.name.lower()]

    def filter_by_category(self, category: str) -> list[Product]:
        wanted = category.strip().lower()
        return [
            p
            for p in self._repository.list_all()
            if p.category.strip().lower() == wanted
        ]

    def total_stock_value(self, currency: str = "UAH") -> Money:
        total = Money(0, currency)
        for product in self._repository.list_all():
            total = total + product.stock_value
        return total

    def most_expensive(self) -> Product:
        products = self.list_products()
        if not products:
            raise EmptyCatalogError("Catalog is empty")
        return max(products, key=lambda product: product.price.amount)

    def low_stock(self, min_stock: int) -> list[Product]:
        if min_stock < 0:
            raise ValidationError("min_stock must not be negative")
        return [p for p in self._repository.list_all() if p.quantity < min_stock]


class PricingService:
    def __init__(self, provider: DiscountProvider) -> None:
        self._provider = provider

    def discounted_price(self, product: Product) -> Money:
        try:
            percent = self._provider.get_discount(product.category)
        except DiscountProviderError as error:
            raise PricingError("Discount provider is unavailable") from error
        try:
            validate_percent(percent)
        except ValidationError as error:
            raise PricingError(f"Invalid discount: {percent}") from error
        return product.price * (1 - percent / 100)

class StockAlertService:
    def __init__(
        self,
        catalog: CatalogService,
        notifier: Notifier,
        min_stock: int | None = None,
    ) -> None:
        self._catalog = catalog
        self._notifier = notifier
        self._min_stock = get_min_stock() if min_stock is None else min_stock

    def notify_low_stock(self, recipient: str) -> int:
        address = validate_email(recipient)
        low = self._catalog.low_stock(self._min_stock)
        for product in low:
            self._notifier.send(
                address, f"Low stock: {product.name} ({product.quantity} left)"
            )
        return len(low)

def build_report(catalog: CatalogService, min_stock: int) -> dict:
    products = catalog.list_products()
    most_expensive = catalog.most_expensive().name if products else None
    return {
        "total_products": len(products),
        "total_stock_value": catalog.total_stock_value().amount,
        "most_expensive": most_expensive,
        "low_stock": [p.name for p in catalog.low_stock(min_stock)],
    }