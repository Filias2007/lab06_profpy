from unittest.mock import AsyncMock

import pytest

from shop.async_provider import AsyncStockProvider
from shop.exceptions import ProviderError, ValidationError

pytestmark = pytest.mark.asyncio


async def test_fetch_quantity():
    client = AsyncMock()
    client.fetch_stock.return_value = {"quantity": 9}

    result = await AsyncStockProvider(client).fetch_quantity(1)

    assert result == 9
    client.fetch_stock.assert_awaited_once_with(1)


async def test_connection_error_becomes_provider_error():
    client = AsyncMock()
    client.fetch_stock.side_effect = ConnectionError("Network error")

    with pytest.raises(ProviderError, match="unavailable") as exc_info:
        await AsyncStockProvider(client).fetch_quantity(1)

    assert isinstance(exc_info.value.__cause__, ConnectionError)


async def test_response_without_quantity():
    client = AsyncMock()
    client.fetch_stock.return_value = {"status": "ok"}

    with pytest.raises(ProviderError, match="quantity"):
        await AsyncStockProvider(client).fetch_quantity(1)


async def test_refresh_returns_updated_copy(laptop):
    client = AsyncMock()
    client.fetch_stock.return_value = {"quantity": 50}

    refreshed = await AsyncStockProvider(client).refresh(laptop)

    assert refreshed.quantity == 50
    assert refreshed.name == laptop.name
    assert laptop.quantity == 3  # original is unchanged
    client.fetch_stock.assert_awaited_once_with(laptop.product_id)


async def test_refresh_with_invalid_quantity(laptop):
    client = AsyncMock()
    client.fetch_stock.return_value = {"quantity": -5}

    with pytest.raises(ValidationError):
        await AsyncStockProvider(client).refresh(laptop)


async def test_refresh_all(products):
    client = AsyncMock()
    client.fetch_stock.side_effect = [{"quantity": 1}, {"quantity": 2}, {"quantity": 3}]

    refreshed = await AsyncStockProvider(client).refresh_all(products)

    assert [p.quantity for p in refreshed] == [1, 2, 3]
    assert client.fetch_stock.await_count == 3


async def test_refresh_all_empty_list():
    client = AsyncMock()

    assert await AsyncStockProvider(client).refresh_all([]) == []
    client.fetch_stock.assert_not_awaited()