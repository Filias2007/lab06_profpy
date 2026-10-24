from __future__ import annotations

import sqlite3
from pathlib import Path

from shop.models import Product
from shop.value_objects import Money


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


_COLUMNS = "id, name, category, price, currency, quantity"


def _row_to_product(row: tuple) -> Product:
    return Product(
        product_id=row[0],
        name=row[1],
        category=row[2],
        price=Money(row[3], row[4]),
        quantity=row[5],
    )


class SqliteProductRepository:
    """SQLite-backed repository; usable as a context manager."""

    def __init__(self, path: Path | str = ":memory:") -> None:
        self._connection = sqlite3.connect(str(path))
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS products ("
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, "
            "price REAL NOT NULL, currency TEXT NOT NULL, quantity INTEGER NOT NULL)"
        )
        self._connection.commit()

    def add(self, product: Product) -> None:
        self._connection.execute(
            f"INSERT OR REPLACE INTO products ({_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?)",
            (
                product.product_id,
                product.name,
                product.category,
                product.price.amount,
                product.price.currency,
                product.quantity,
            ),
        )
        self._connection.commit()

    def get(self, product_id: int) -> Product | None:
        row = self._connection.execute(
            f"SELECT {_COLUMNS} FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        return None if row is None else _row_to_product(row)

    def list_all(self) -> list[Product]:
        rows = self._connection.execute(
            f"SELECT {_COLUMNS} FROM products ORDER BY id"
        ).fetchall()
        return [_row_to_product(row) for row in rows]

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> SqliteProductRepository:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()