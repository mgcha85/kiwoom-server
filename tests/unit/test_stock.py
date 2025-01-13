import pytest
from backend.services.stock_service import StockService
from backend.models.stock import Stock

def test_get_current_price():
    stock_service = StockService()
    stock = stock_service.get_current_price("005930")  # 삼성전자 종목 코드
    assert isinstance(stock, Stock)
    assert stock.code == "005930"
    assert stock.price > 0

def test_get_history():
    stock_service = StockService()
    history = stock_service.get_history("005930", "20230101", "20231231")
    assert isinstance(history, list)
    assert len(history) > 0
    assert all(isinstance(item, Stock) for item in history)