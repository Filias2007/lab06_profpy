from __future__ import annotations

from dataclasses import dataclass

from shop.exceptions import ValidationError
from shop.value_objects import Money

MAX_PRICE = 1_000_000
MAX_QUANTITY = 1_000_000


@dataclass(frozen=True)
class Product:
    product_id: int
    name: str
    price: Money
    category: str
    quantity: int = 0

    def __post_init__(self) -> None:
        if (
            isinstance(self.product_id, bool)
            or not isinstance(self.product_id, int)
            or self.product_id <= 0
        ):
            raise ValidationError("Product id must be a positive integer")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("Name must not be empty")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValidationError("Category must not be empty")
        if not isinstance(self.price, Money):
            raise ValidationError("Price must be a Money instance")
        if self.price.amount <= 0:
            raise ValidationError("Price must be positive")
        if self.price.amount > MAX_PRICE:
            raise ValidationError(f"Price must not exceed {MAX_PRICE}")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ValidationError("Quantity must be an integer")
        if not 0 <= self.quantity <= MAX_QUANTITY:
            raise ValidationError(f"Quantity must be between 0 and {MAX_QUANTITY}")

    @property
    def stock_value(self) -> Money:
        return self.price * self.quantity