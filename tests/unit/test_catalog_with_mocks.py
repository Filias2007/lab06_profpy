from unittest.mock import MagicMock, Mock, create_autospec

import pytest

from shop.exceptions import DuplicateProductError, ProductNotFoundError
from shop.protocols import ProductRepository
from shop.services import CatalogService


def test_add_product_calls_repository(laptop):
    repository = Mock(spec=ProductRepository)
    repository.get.return_value = None

    CatalogService(repository).add_product(laptop)

    repository.get.assert_called_once_with(1)
    repository.add.assert_called_once_with(laptop)


def test_duplicate_does_not_touch_storage(laptop):
    repository = Mock(spec=ProductRepository)
    repository.get.return_value = laptop

    with pytest.raises(DuplicateProductError):
        CatalogService(repository).add_product(laptop)

    repository.add.assert_not_called()


def test_get_product_not_found_from_mock():
    repository = Mock(spec=ProductRepository)
    repository.get.return_value = None

    with pytest.raises(ProductNotFoundError):
        CatalogService(repository).get_product(5)

    repository.get.assert_called_once_with(5)


def test_repository_failure_is_propagated(laptop):
    repository = Mock(spec=ProductRepository)
    repository.get.return_value = None
    repository.add.side_effect = OSError("disk is full")

    with pytest.raises(OSError, match="disk is full"):
        CatalogService(repository).add_product(laptop)


def test_most_expensive_with_magicmock(laptop, mouse):
    repository = MagicMock(spec=ProductRepository)
    repository.list_all.return_value = [mouse, laptop]

    result = CatalogService(repository).most_expensive()

    assert result == laptop
    repository.list_all.assert_called_once_with()


def test_autospec_checks_signature():
    repository = create_autospec(ProductRepository, instance=True)

    with pytest.raises(TypeError):
        repository.get(1, 2)


def test_state_testing_with_fake_repository(repository, laptop):
    """Fake: verify final state instead of interactions."""
    CatalogService(repository).add_product(laptop)

    assert repository.list_all() == [laptop]