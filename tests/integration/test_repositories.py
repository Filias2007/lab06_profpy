import pytest
from shop.models import Product
from shop.repositories import CategoryRepository, ProductRepository
from shop.services import ShopService


@pytest.mark.integration
def test_crud_and_aggregates(db_session):
    cat_repo = CategoryRepository(db_session)
    prod_repo = ProductRepository(db_session)
    service = ShopService(db_session)

    # 1. Create
    electronics = cat_repo.add("Electronics")
    laptop = prod_repo.add(
        Product(name="Laptop", price=30000.0, quantity=5, category_id=electronics.id)
    )
    mouse = prod_repo.add(
        Product(name="Mouse", price=1000.0, quantity=10, category_id=electronics.id)
    )

    # 2. Read
    assert laptop.id is not None
    assert prod_repo.get_by_id(laptop.id).name == "Laptop"

    # 3. Aggregates
    total_val = service.get_total_stock_value()
    assert total_val == pytest.approx(160000.0)

    most_expensive = service.get_most_expensive_product()
    assert most_expensive.name == "Laptop"

    # 4. Update
    updated = prod_repo.update_price_and_quantity(mouse.id, 1200.0, 8)
    assert updated.price == 1200.0
    assert updated.quantity == 8

    # 5. Delete
    deleted = prod_repo.delete(laptop.id)
    assert deleted is True
    assert prod_repo.get_by_id(laptop.id) is None