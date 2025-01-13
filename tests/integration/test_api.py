import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_stock_current_price():
    response = client.get("/stock/current/005930")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "005930"
    assert data["price"] > 0

def test_get_stock_history():
    response = client.get("/stock/history/005930?start=20230101&end=20231231")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item["price"], float) for item in data)

def test_buy_order():
    response = client.post("/order/buy", json={"code": "005930", "quantity": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "005930"
    assert data["quantity"] == 10
    assert data["type"] == "buy"

def test_sell_order():
    response = client.post("/order/sell", json={"code": "005930", "quantity": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "005930"
    assert data["quantity"] == 5
    assert data["type"] == "sell"