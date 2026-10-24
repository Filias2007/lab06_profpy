from unittest.mock import Mock, call, patch
from shop.exceptions import ValidationError
import pytest

from shop.exceptions import ConfigError, NotificationError
from shop.protocols import Notifier
from shop.services import StockAlertService

MANAGER = "manager@shop.ua"


def test_notification_for_low_stock_product(catalog):
    notifier = Mock(spec=Notifier)

    sent = StockAlertService(catalog, notifier, min_stock=5).notify_low_stock(MANAGER)

    assert sent == 1
    notifier.send.assert_called_once_with(MANAGER, "Low stock: Laptop (3 left)")


def test_no_notification_when_stock_is_enough(catalog):
    notifier = Mock(spec=Notifier)

    sent = StockAlertService(catalog, notifier, min_stock=0).notify_low_stock(MANAGER)

    assert sent == 0
    notifier.send.assert_not_called()


def test_threshold_is_read_from_environment(catalog, monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "6")
    notifier = Mock(spec=Notifier)

    sent = StockAlertService(catalog, notifier).notify_low_stock(MANAGER)

    assert sent == 2
    assert notifier.send.call_args_list == [
        call(MANAGER, "Low stock: Laptop (3 left)"),
        call(MANAGER, "Low stock: Desk (5 left)"),
    ]


def test_default_threshold_without_environment(catalog):
    notifier = Mock(spec=Notifier)

    sent = StockAlertService(catalog, notifier).notify_low_stock(MANAGER)

    assert sent == 1  # default threshold is 5


def test_invalid_environment_value(catalog, monkeypatch):
    monkeypatch.setenv("SHOP_MIN_STOCK", "abc")

    with pytest.raises(ConfigError):
        StockAlertService(catalog, Mock(spec=Notifier))


def test_patch_where_name_is_looked_up(catalog):
    notifier = Mock(spec=Notifier)

    with patch("shop.services.get_min_stock", return_value=4) as mocked:
        sent = StockAlertService(catalog, notifier).notify_low_stock(MANAGER)

    mocked.assert_called_once_with()
    assert sent == 1


def test_notifier_failure_is_propagated(catalog):
    notifier = Mock(spec=Notifier)
    notifier.send.side_effect = NotificationError("SMTP is down")
    service = StockAlertService(catalog, notifier, min_stock=6)

    with pytest.raises(NotificationError, match="SMTP"):
        service.notify_low_stock(MANAGER)

    assert notifier.send.call_count == 1

def test_invalid_recipient_email_rejected(catalog):
    notifier = Mock(spec=Notifier)
    service = StockAlertService(catalog, notifier, min_stock=5)

    with pytest.raises(ValidationError, match="Invalid email"):
        service.notify_low_stock("not-an-email")

    notifier.send.assert_not_called()


def test_send_called_exactly_once(catalog):
    notifier = Mock(spec=Notifier)

    StockAlertService(catalog, notifier, min_stock=5).notify_low_stock(MANAGER)

    notifier.send.assert_called_once()


@patch("shop.services.get_min_stock", return_value=6)
def test_patch_as_decorator(mocked_min_stock, catalog):
    notifier = Mock(spec=Notifier)

    sent = StockAlertService(catalog, notifier).notify_low_stock(MANAGER)

    mocked_min_stock.assert_called_once_with()
    assert sent == 2