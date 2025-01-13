# services/account_service.py
from typing import Dict, List
from backend.kiwoom import Kiwoom

class AccountService:
    def __init__(self, kiwoom: Kiwoom):
        self.kiwoom = kiwoom

    def get_account_balance(self) -> Dict[str, str]:
        """
        계좌평가잔고내역요청 (opw00018)
        - 계좌의 총평가금액, 보유 종목 정보 등을 반환합니다.
        """
        print("계좌평가잔고내역요청")
        account_no = self.kiwoom.get_login_info("ACCNO")
        account_no = account_no.split(";")[0]  # 첫 번째 계좌번호 사용
        self.kiwoom.set_input_value("계좌번호", account_no)
        self.kiwoom.set_input_value("비밀번호", "7540")  # 비밀번호 입력 필요
        self.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "0101")
        return self.kiwoom.opw00018_data

    def get_deposit(self) -> Dict[str, str]:
        """
        예수금상세현황요청 (opw00001)
        - 예수금과 출금가능금액을 반환합니다.
        """
        account_no = self.kiwoom.get_login_info("ACCNO").split(";")[0]  # 첫 번째 계좌번호 사용
        self.kiwoom.set_input_value("계좌번호", account_no)
        self.kiwoom.set_input_value("비밀번호", "7540")  # 비밀번호 입력 필요
        self.kiwoom.comm_rq_data("예수금상세현황요청", "opw00001", 0, "0101")
        return self.kiwoom.opw00001_data

    def get_holding_stocks(self) -> List[Dict[str, str]]:
        """
        계좌평가잔고내역요청 (opw00018)을 통해 보유 종목 정보만 반환합니다.
        """
        account_no = self.kiwoom.get_login_info("ACCNO").split(";")[0]  # 첫 번째 계좌번호 사용
        self.kiwoom.set_input_value("계좌번호", account_no)
        self.kiwoom.set_input_value("비밀번호", "7540")  # 비밀번호 입력 필요
        self.kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 0, "0101")
        return self.kiwoom.opw00018_data["stocks"]