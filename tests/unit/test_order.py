import pytest
from backend.services.order_service import OrderService
from backend.models.order import Order

def test_buy_order():
    order_service = OrderService()
    order = order_service.buy("005930", 10)  # 삼성전자 10주 매수
    assert isinstance(order, Order)
    assert order.code == "005930"
    assert order.quantity == 10
    assert order.type == "buy"

def test_sell_order():
    order_service = OrderService()
    order = order_service.sell("005930", 5)  # 삼성전자 5주 매도
    assert isinstance(order, Order)
    assert order.code == "005930"
    assert order.quantity == 5
    assert order.type == "sell"