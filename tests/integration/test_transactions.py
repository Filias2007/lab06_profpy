import pytest
from shop.models import Product
from shop.repositories import CategoryRepository, ProductRepository
from shop.services import ShopService
from shop.exceptions import InsufficientStockError


@pytest.mark.integration
def test_purchase_transaction_success_and_rollback(db_session):
    cat_repo = CategoryRepository(db_session)
    prod_repo = ProductRepository(db_session)
    service = ShopService(db_session)

    cat = cat_repo.add("Gadgets")
    prod = prod_repo.add(
        Product(name="Phone", price=15000.0, quantity=3, category_id=cat.id)
    )

    # Успішна транзакція
    service.purchase_product(prod.id, 2)
    db_session.refresh(prod)
    assert prod.quantity == 1

    # Помилка транзакції та гарантований Rollback
    with pytest.raises(InsufficientStockError):
        service.purchase_product(prod.id, 5)

    db_session.refresh(prod)
    assert prod.quantity == 1  # Стан у БД не змінився