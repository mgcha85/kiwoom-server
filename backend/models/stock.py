# models/stock.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StockCurrentPrice(BaseModel):
    """현재가 정보"""
    code: str          # 종목코드
    name: str          # 종목명
    price: int         # 현재가
    volume: int        # 거래량
    change: float      # 등락율

class StockDailyData(BaseModel):
    """일봉 데이터"""
    date: str     # 일자
    open: int          # 시가
    high: int          # 고가
    low: int           # 저가
    close: int         # 종가
    volume: int        # 거래량

class StockMinuteData(BaseModel):
    """분봉 데이터"""
    time: str     # 체결시간
    open: int          # 시가
    high: int          # 고가
    low: int           # 저가
    close: int         # 종가
    volume: int        # 거래량