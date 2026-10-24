from __future__ import annotations

import math
from dataclasses import dataclass

from shop.exceptions import ValidationError


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "UAH"

    def __post_init__(self) -> None:
        if (
            isinstance(self.amount, bool)
            or not isinstance(self.amount, (int, float))
            or not math.isfinite(self.amount)
        ):
            raise ValidationError("Amount must be a finite number")
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")
        if not isinstance(self.currency, str) or not self.currency.strip():
            raise ValidationError("Currency must not be empty")

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValidationError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: float) -> Money:
        if factor < 0:
            raise ValidationError("Factor cannot be negative")
        return Money(self.amount * factor, self.currency)