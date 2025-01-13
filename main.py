from fastapi import FastAPI
from PyQt5.QtWidgets import QApplication
from threading import Thread
from queue import Queue
import sys
import uvicorn
from backend.kiwoom import Kiwoom
from backend.kiwoom.utils import open_yaml
from backend.services.account_service import AccountService
from backend.services.stock_service import StockService
from backend.services.order_service import OrderService
from datetime import datetime, timedelta
from typing import Optional

# PyQt5 애플리케이션 생성
app_qt = QApplication(sys.argv)

config = open_yaml('common/config.yaml')

# Kiwoom 인스턴스 생성
kiwoom = Kiwoom(config)
kiwoom.comm_connect()  # 로그인
kiwoom.set_account()

# 서비스 초기화
account_service = AccountService(kiwoom)
stock_service = StockService(kiwoom)
order_service = OrderService(kiwoom)

# Queue 생성
request_queue = Queue()
response_queue = Queue()

# FastAPI 애플리케이션 초기화
app = FastAPI(
    title="Kiwoom API",
    description="키움증권 API를 활용한 RESTful API 서비스",
    version="1.0.0",
)

@app.get("/account/balance")
def get_account_balance():
    """계좌 잔고 조회 API"""
    try:
        # 요청을 큐에 전달
        request_queue.put("get_account_balance")
        # 응답 대기
        response = response_queue.get(timeout=5)  # 5초 대기
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/account/deposit")
def get_deposit():
    """예수금 조회 API"""
    try:
        request_queue.put("get_deposit")
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/account/holdings")
def get_holding_stocks():
    """보유 종목 조회 API"""
    try:
        request_queue.put("get_holding_stocks")
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/stock/current/{code}")
def get_current_price(code: str):
    """현재가 조회 API"""
    try:
        request_queue.put(("get_current_price", code))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/stock/daily/{code}")
def get_daily_data(code: str, start_date: str, end_date: str):
    """일봉 데이터 조회 API"""
    try:
        request_queue.put(("get_daily_data", code, start_date, end_date))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/stock/minute/{code}")
def get_minute_data(code: str, period: int = 1):
    """분봉 데이터 조회 API"""
    try:
        request_queue.put(("get_minute_data", code, period))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/order/buy")
def buy_order(code: str, quantity: int, price: int, due_date: Optional[str] = None):
    """매수 주문 API"""
    try:
        if due_date is None:
            due_date = datetime.now() + timedelta(days=90)
        else:
            due_date = datetime.strptime(due_date, "%Y%m%d%H%M%S")

        request_queue.put(("buy_order", code, quantity, price, due_date))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/order/sell")
def sell_order(code: str, quantity: int, price: int):
    """매도 주문 API"""
    try:
        request_queue.put(("sell_order", code, quantity, price))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/order/cancel")
def cancel_order(order_no: str, code: str, quantity: int):
    """주문 취소 API"""
    try:
        request_queue.put(("cancel_order", order_no, code, quantity))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/conditions/list")
def get_conditions():
    """조건식 목록 조회 API"""
    try:
        request_queue.put("get_conditions")
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.get("/conditions/search")
def search_conditions(condition_name: str, condition_index: int, is_real_time: bool = False):
    """조건식으로 종목 검색 API"""
    try:
        request_queue.put(("search_conditions", condition_name, condition_index, is_real_time))
        response = response_queue.get(timeout=10)
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/conditions/stop")
def stop_conditions(condition_name: str, condition_index: int):
    """조건식 검색 중지 API"""
    try:
        request_queue.put(("stop_conditions", condition_name, condition_index))
        response = response_queue.get(timeout=5)
        return response
    except Exception as e:
        return {"error": str(e)}

def process_requests():
    """PyQt에서 FastAPI 요청 처리"""
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

            elif isinstance(task, tuple) and task[0] == "get_current_price":
                _, code = task
                response = stock_service.get_current_price(code)
                response_queue.put(response)

            elif isinstance(task, tuple) and task[0] == "get_daily_data":
                _, code, start_date, end_date = task
                response = stock_service.get_daily_data(code, start_date, end_date)
                response_queue.put(response)

            elif isinstance(task, tuple) and task[0] == "get_minute_data":
                _, code, period = task
                response = stock_service.get_minute_data(code, period)
                response_queue.put(response)

            elif isinstance(task, tuple) and task[0] == "buy_order":
                _, code, quantity, price, due_date = task
                response = order_service.buy_order(code, quantity, price, due_date)
                response_queue.put(response)

            elif isinstance(task, tuple) and task[0] == "sell_order":
                _, code, quantity, price = task
                response = order_service.sell_order(code, quantity, price)
                response_queue.put(response)

            elif isinstance(task, tuple) and task[0] == "cancel_order":
                _, order_no, code, quantity = task
                response = order_service.cancel_order(order_no, code, quantity)
                response_queue.put(response)

            elif task == "get_conditions":
                kiwoom.get_condition_load()
                response = kiwoom.get_condition_name_list()
                response_queue.put(response)

            elif isinstance(task, tuple) and task[0] == "search_conditions":
                _, condition_name, condition_index, is_real_time = task
                response = kiwoom.send_condition("0101", condition_name, condition_index, int(is_real_time))
                response_queue.put({"matched_codes": response})

            elif isinstance(task, tuple) and task[0] == "stop_conditions":
                _, condition_name, condition_index = task
                kiwoom.send_condition_stop("0101", condition_name, condition_index)
                response_queue.put({"message": "Condition search stopped successfully"})

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
