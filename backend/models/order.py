# models/order.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Order(BaseModel):
    """주문 정보"""
    order_no: str          # 주문번호
    code: str              # 종목코드
    name: str              # 종목명
    order_type: str        # 주문유형 (매수, 매도, 정정, 취소)
    quantity: int          # 주문수량
    price: int             # 주문가격
    status: str            # 주문상태 (접수, 체결, 취소)
    order_time: datetime   # 주문시간
    remain_quantity: int   # 미체결수량
    cum_price: int         # 체결누계금액