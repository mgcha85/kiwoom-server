# api/routes/order.py
from fastapi import APIRouter, Depends, HTTPException
from backend.models.order import Order
from backend.services.order_service import OrderService
from api.dependencies import get_order_service
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

class BuyOrderRequest(BaseModel):
    code: str
    quantity: int
    price: int
    due_date: Optional[datetime] = None  # 선택적 필드

    def set_default_due_date(self):
        """
        due_date가 제공되지 않았을 경우 기본값 설정 (오늘 + 10년)
        """
        if self.due_date is None:
            self.due_date = datetime.now() + timedelta(days=3650)  # 오늘 + 10년

# 매수 주문
@router.post("/buy", response_model=Order)
def buy_order(
    request: BuyOrderRequest,
    order_service: OrderService = Depends(get_order_service),
):
    try:
        # 기본값 설정
        request.set_default_due_date()
        return order_service.buy_order(request.code, request.quantity, request.price, request.due_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 매도 주문
@router.post("/sell", response_model=Order)
def sell_order(
    request: BuyOrderRequest,
    order_service: OrderService = Depends(get_order_service),
):
    try:
        return order_service.sell_order(request.code, request.quantity, request.price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 주문 취소
@router.post("/cancel", response_model=Order)
def cancel_order(
    order_no: str,
    code: str,
    quantity: int,
    order_service: OrderService = Depends(get_order_service),
):
    try:
        return order_service.cancel_order(order_no, code, quantity)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))