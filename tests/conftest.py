import pytest

from shop.models import Product
from shop.repositories import InMemoryProductRepository
from shop.services import CatalogService
from shop.value_objects import Money

CSV_HEADER = "id,name,category,price,quantity\n"

STANDARD_ROWS = [
    "1,Laptop,electronics,35000,3",
    "2,Mouse,electronics,1200,20",
    "3,Desk,furniture,7500.5,5",
    "4,Chair,furniture,2300,2",
]


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Every test starts without SHOP_MIN_STOCK (deterministic tests)."""
    monkeypatch.delenv("SHOP_MIN_STOCK", raising=False)


@pytest.fixture(scope="session")
def csv_header() -> str:
    return CSV_HEADER


@pytest.fixture(params=["UAH", "USD", "EUR"])
def currency(request) -> str:
    """Parameterized fixture."""
    return request.param


@pytest.fixture
def product_factory():
    """Fixture factory."""

    def create(
        *,
        product_id: int = 1,
        name: str = "Product",
        price: float = 100.0,
        category: str = "general",
        quantity: int = 10,
        currency: str = "UAH",
    ) -> Product:
        return Product(
            product_id=product_id,
            name=name,
            price=Money(price, currency),
            category=category,
            quantity=quantity,
        )

    return create


@pytest.fixture
def laptop(product_factory) -> Product:
    return product_factory(
        product_id=1, name="Laptop", price=35_000, category="electronics", quantity=3
    )


@pytest.fixture
def mouse(product_factory) -> Product:
    return product_factory(
        product_id=2, name="Mouse", price=1_200, category="electronics", quantity=20
    )


@pytest.fixture
def desk(product_factory) -> Product:
    return product_factory(
        product_id=3, name="Desk", price=7_500.5, category="furniture", quantity=5
    )


@pytest.fixture
def products(laptop, mouse, desk) -> list[Product]:
    return [laptop, mouse, desk]


@pytest.fixture
def repository() -> InMemoryProductRepository:
    return InMemoryProductRepository()


@pytest.fixture
def empty_catalog(repository) -> CatalogService:
    return CatalogService(repository)


@pytest.fixture
def catalog(repository, products) -> CatalogService:
    service = CatalogService(repository)
    for product in products:
        service.add_product(product)
    return service


@pytest.fixture
def csv_factory(tmp_path, csv_header):
    """Creates a CSV file in an isolated temporary directory."""

    def create(rows, *, name="data.csv", header=None):
        path = tmp_path / name
        head = csv_header if header is None else header
        path.write_text(head + "".join(f"{row}\n" for row in rows), encoding="utf-8")
        return path

    return create


@pytest.fixture
def products_csv(csv_factory):
    return csv_factory(STANDARD_ROWS, name="products.csv")


@pytest.fixture
def output_dir(tmp_path):
    """Fixture with teardown: no temporary files may be left after a test."""
    directory = tmp_path / "out"
    directory.mkdir()
    yield directory
    leftovers = list(directory.glob("*.tmp"))
    assert not leftovers, f"Temporary files left behind: {leftovers}"