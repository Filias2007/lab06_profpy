import sqlite3
import pytest
from shop.services import find_products_by_category_db_api


@pytest.mark.integration
def test_db_api_parameterized_query(tmp_path):
    db_file = tmp_path / "test_shop.db"

    # Створюємо тестову таблицю та додаємо дані через сирий DB-API
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
        )
        cursor.execute(
            "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, quantity INTEGER, category_id INTEGER);"
        )
        cursor.execute("INSERT INTO categories VALUES (1, 'Audio');")
        cursor.execute(
            "INSERT INTO products VALUES (101, 'Headphones', 1500.0, 5, 1);"
        )
        conn.commit()

    # Перевіряємо параметризований виклик DB-API
    results = find_products_by_category_db_api(str(db_file), "Audio")

    assert len(results) == 1
    assert results[0][1] == "Headphones"
    assert results[0][2] == 1500.0