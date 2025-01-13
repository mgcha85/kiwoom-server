# models/account.py
from pydantic import BaseModel
from typing import List, Optional

class AccountBalance(BaseModel):
    """계좌 잔고 정보"""
    total_balance: int          # 총평가금액
    deposit: int                # 예수금
    total_profit: int           # 총평가손익금액
    total_profit_rate: float    # 총수익률(%)

class HoldingStock(BaseModel):
    """보유 종목 정보"""
    code: str                   # 종목코드
    name: str                   # 종목명
    quantity: int               # 보유수량
    purchase_price: int         # 매입가
    current_price: int          # 현재가
    profit: int                 # 평가손익
    profit_rate: float          # 수익률(%)

class AccountInfo(BaseModel):
    """계좌 정보"""
    account_no: str             # 계좌번호
    balance: AccountBalance     # 잔고 정보
    holding_stocks: List[HoldingStock]  # 보유 종목 리스트