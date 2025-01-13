# api/dependencies.py
from backend.kiwoom import Kiwoom
from backend.services.stock_service import StockService
from backend.services.order_service import OrderService
from backend.services.account_service import AccountService
from backend.services.condition_service import ConditionService
from fastapi import Depends

# Kiwoom 인스턴스를 FastAPI 의존성으로 제공
def get_kiwoom() -> ConditionService:
    if not hasattr(get_kiwoom, "_kiwoom"):
        # Kiwoom 인스턴스를 처음 호출할 때 생성
        kiwoom_instance = Kiwoom()
        kiwoom_instance.comm_connect()  # 로그인
        kiwoom_instance.set_account()
        get_kiwoom._kiwoom = ConditionService(kiwoom_instance)
    return get_kiwoom._kiwoom

def get_order_service(kiwoom: ConditionService = Depends(get_kiwoom)) -> OrderService:
    return OrderService(kiwoom)