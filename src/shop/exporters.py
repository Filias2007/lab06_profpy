from __future__ import annotations

import json
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from shop.models import Product


def product_to_dict(product: Product) -> dict:
    return {
        "id": product.product_id,
        "name": product.name,
        "category": product.category,
        "price": product.price.amount,
        "currency": product.price.currency,
        "quantity": product.quantity,
    }


def export_json(data: Any, path: Path) -> None:
    """Serialize data to JSON and write it atomically."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    _atomic_write(path, text)


def export_products_json(products: Iterable[Product], path: Path) -> int:
    data = [product_to_dict(product) for product in products]
    export_json(data, path)
    return len(data)


def export_report(report: dict, path: Path) -> None:
    export_json(report, path)


def _atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise