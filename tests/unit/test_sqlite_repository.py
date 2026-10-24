import sqlite3

import pytest

from shop.repositories import InMemoryProductRepository, SqliteProductRepository


@pytest.fixture(params=["memory", "sqlite"])
def any_repository(request, tmp_path):
    """Both implementations must satisfy the same contract."""
    if request.param == "memory":
        yield InMemoryProductRepository()
    else:
        repository = SqliteProductRepository(tmp_path / "shop.db")
        yield repository
        repository.close()


def test_add_and_get(any_repository, laptop):
    any_repository.add(laptop)

    assert any_repository.get(1) == laptop


def test_get_unknown_returns_none(any_repository):
    assert any_repository.get(999) is None


def test_list_all_keeps_id_order(any_repository, products):
    for product in products:
        any_repository.add(product)

    assert [p.name for p in any_repository.list_all()] == ["Laptop", "Mouse", "Desk"]


def test_add_same_id_replaces(any_repository, laptop, product_factory):
    any_repository.add(laptop)
    any_repository.add(product_factory(product_id=1, name="Laptop Pro", price=40_000))

    assert [p.name for p in any_repository.list_all()] == ["Laptop Pro"]


def test_sqlite_data_survives_reopening(tmp_path, laptop):
    path = tmp_path / "shop.db"
    with SqliteProductRepository(path) as repository:
        repository.add(laptop)

    with SqliteProductRepository(path) as reopened:
        assert reopened.get(1) == laptop


def test_in_memory_sqlite_by_default(laptop):
    with SqliteProductRepository() as repository:
        repository.add(laptop)

        assert len(repository.list_all()) == 1


def test_context_manager_closes_connection(laptop):
    with SqliteProductRepository() as repository:
        repository.add(laptop)

    with pytest.raises(sqlite3.ProgrammingError):
        repository.get(1)


def test_context_manager_closes_after_exception():
    with pytest.raises(RuntimeError, match="boom"):
        with SqliteProductRepository() as repository:
            raise RuntimeError("boom")

    with pytest.raises(sqlite3.ProgrammingError):
        repository.list_all()