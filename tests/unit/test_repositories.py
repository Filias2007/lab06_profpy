from shop.repositories import InMemoryProductRepository


def test_repository_is_empty_initially():
    repository = InMemoryProductRepository()

    assert len(repository) == 0
    assert repository.list_all() == []


def test_add_and_get(laptop):
    repository = InMemoryProductRepository()

    repository.add(laptop)

    assert repository.get(1) == laptop
    assert len(repository) == 1


def test_get_unknown_returns_none():
    assert InMemoryProductRepository().get(999) is None


def test_list_all_returns_copy(laptop):
    repository = InMemoryProductRepository()
    repository.add(laptop)

    result = repository.list_all()
    result.clear()

    assert len(repository) == 1


def test_add_same_id_replaces(laptop, product_factory):
    repository = InMemoryProductRepository()
    repository.add(laptop)
    updated = product_factory(product_id=1, name="Laptop Pro", price=40_000)

    repository.add(updated)

    assert repository.get(1).name == "Laptop Pro"
    assert len(repository) == 1