from __future__ import annotations

import csv
from pathlib import Path

from shop.exceptions import ImportDataError
from shop.models import Product
from shop.value_objects import Money

REQUIRED_COLUMNS = ("id", "name", "category", "price", "quantity")


def import_products(path: Path, currency: str = "UAH") -> list[Product]:
    """Read products from a CSV file (header: id,name,category,price,quantity)."""
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ImportDataError("CSV file is empty")
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ImportDataError(f"Missing columns: {', '.join(missing)}")
            return [
                _parse_row(row, line, currency)
                for line, row in enumerate(reader, start=2)
            ]
    except OSError as error:
        raise ImportDataError(f"Cannot read file: {path}") from error


def _parse_row(row: dict, line: int, currency: str) -> Product:
    try:
        return Product(
            product_id=int(row["id"]),
            name=row["name"],
            category=row["category"],
            price=Money(float(row["price"]), currency),
            quantity=int(row["quantity"]),
        )
    except (ValueError, TypeError) as error:
        raise ImportDataError(
            f"Malformed record on line {line}: {error}", line=line
        ) from error