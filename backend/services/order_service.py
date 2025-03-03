# services/order_service.py
from typing import Dict
from datetime import datetime
from backend.kiwoom import Kiwoom

class OrderService:
    def __init__(self, kiwoom: Kiwoom):
        self.kiwoom = kiwoom

    def buy_order(self, code: str, quantity: int, price: int, due_date: datetime) -> Dict[str, str]:
        """매수 주문"""
        hogaType = "03" if price == 0 else "00"
        account_no = self.kiwoom.get_login_info("ACCNO").split(";")[0]

        self.kiwoom.send_order("매수주문", "0101", account_no, 1, code, quantity, price, hogaType, "", due_date)
        print("order_no: ", self.kiwoom.order_no)
        return self.kiwoom.order_data

    def sell_order(self, code: str, quantity: int, price: int) -> Dict[str, str]:
        """매도 주문"""
        hogaType = "03" if price == 0 else "00"
        account_no = self.kiwoom.get_login_info("ACCNO").split(";")[0]
        print(code, quantity, price)

        try:
            self.kiwoom.send_order("매도주문", "0101", account_no, 2, code, quantity, price, hogaType, "", None)
        except Exception as e:
            print(e)

        print("order_no: ", self.kiwoom.order_no)
        return self.kiwoom.order_data

    def cancel_order(self, order_no: str, code: str, quantity: int) -> Dict[str, str]:
        """주문 취소"""
        account_no = self.kiwoom.get_login_info("ACCNO").split(";")[0]
        self.kiwoom.send_order("주문취소", "0101", account_no, 3, code, quantity, 0, "03", order_no)
        return self.kiwoom.order_data
    