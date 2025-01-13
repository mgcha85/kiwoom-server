from fastapi import FastAPI
from PyQt5.QtWidgets import QApplication
from threading import Thread
from queue import Queue
import sys
import uvicorn
from backend.kiwoom import Kiwoom
from api.routes.account import router as account_router
from api.routes.order import router as order_router
from api.routes.stock import router as stock_router

# PyQt5 애플리케이션 생성
app_qt = QApplication(sys.argv)

# Kiwoom 인스턴스 생성
kiwoom = Kiwoom()
kiwoom.comm_connect()  # 로그인
kiwoom.set_account()

# Queue 생성
request_queue = Queue()
response_queue = Queue()

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="Kiwoom API",
    description="키움증권 API를 활용한 RESTful API 서비스",
    version="1.0.0",
)

# 라우트 등록
app.include_router(account_router, prefix="/account", tags=["account"])
app.include_router(order_router, prefix="/order", tags=["order"])
app.include_router(stock_router, prefix="/stock", tags=["stock"])

def process_requests():
    """PyQt에서 FastAPI 요청 처리"""
    from backend.services.account_service import AccountService
    from backend.services.order_service import OrderService
    from backend.services.stock_service import StockService

    account_service = AccountService(kiwoom)
    order_service = OrderService(kiwoom)
    stock_service = StockService(kiwoom)

    while True:
        if not request_queue.empty():
            task = request_queue.get()

            if task == "get_account_balance":
                response = account_service.get_account_balance()
                response_queue.put(response)

            elif task == "get_deposit":
                response = account_service.get_deposit()
                response_queue.put(response)

            elif task == "get_holding_stocks":
                response = account_service.get_holding_stocks()
                response_queue.put(response)

            elif task == "buy_order":
                response = order_service.buy_order()
                response_queue.put(response)

            elif task == "sell_order":
                response = order_service.sell_order()
                response_queue.put(response)

            elif task == "cancel_order":
                response = order_service.cancel_order()
                response_queue.put(response)

            elif task == "get_current_price":
                response = stock_service.get_current_price()
                response_queue.put(response)

            elif task == "get_daily_data":
                response = stock_service.get_daily_data()
                response_queue.put(response)

            elif task == "get_minute_data":
                response = stock_service.get_minute_data()
                response_queue.put(response)

def run_fastapi():
    """FastAPI 애플리케이션 실행"""
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    # 요청 처리 스레드 시작
    request_thread = Thread(target=process_requests, daemon=True)
    request_thread.start()

    # FastAPI 실행 스레드 시작
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # PyQt5 애플리케이션 실행 (메인 스레드)
    sys.exit(app_qt.exec_())
