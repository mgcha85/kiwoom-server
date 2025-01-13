import pytest
from backend.services.stock_service import StockService
from backend.services.order_service import OrderService
from backend.services.account_service import AccountService

def test_stock_service_integration():
    stock_service = StockService()
    current_price = stock_service.get_current_price("005930")
    assert current_price.price > 0

    history = stock_service.get_history("005930", "20230101", "20231231")
    assert len(history) > 0

def test_order_service_integration():
    order_service = OrderService()
    buy_order = order_service.buy("005930", 10)
    assert buy_order.quantity == 10

    sell_order = order_service.sell("005930", 5)
    assert sell_order.quantity == 5

def test_account_service_integration():
    account_service = AccountService()
    account = account_service.get_account_info("123456789")
    assert account.balance > 0