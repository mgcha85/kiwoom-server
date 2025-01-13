import pytest
from typing import Dict, List

import sys, os
# 프로젝트 루트 디렉토리를 시스템 경로에 추가
print(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.account_service import AccountService
from backend.kiwoom import Kiwoom

# Kiwoom API 모의 객체(Mock) 생성
class MockKiwoom:
    def __init__(self):
        self.stock_data = {}
        self.login_info = {"ACCNO": "123456789;0000"}

    def get_login_info(self, tag: str) -> str:
        return self.login_info.get(tag, "")

    def set_input_value(self, key: str, value: str):
        pass

    def comm_rq_data(self, request_name: str, tr_code: str, inquiry: int, screen_no: str):
        # 모의 데이터 반환
        if request_name == "계좌잔고조회":
            self.stock_data = {
                "계좌번호": "123456789",
                "총매입금액": "1000000",
                "총평가금액": "1200000",
                "총평가손익금액": "200000",
                "총수익률": "20.0",
            }
        elif request_name == "예수금상세현황요청":
            self.stock_data = {
                "예수금": "500000",
                "출금가능금액": "450000",
            }
        elif request_name == "보유종목조회":
            self.stock_data = [
                {"종목코드": "005930", "종목명": "삼성전자", "보유수량": "10", "평균단가": "70000", "현재가": "75000"},
                {"종목코드": "035720", "종목명": "카카오", "보유수량": "5", "평균단가": "120000", "현재가": "130000"},
            ]

# 테스트를 위한 AccountService 초기화
@pytest.fixture
def account_service():
    mock_kiwoom = MockKiwoom()
    return AccountService(mock_kiwoom)

# 계좌 잔고 조회 테스트
def test_get_account_balance(account_service):
    result = account_service.get_account_balance()
    assert isinstance(result, Dict)
    assert "계좌번호" in result
    assert "총매입금액" in result
    assert "총평가금액" in result
    assert "총평가손익금액" in result
    assert "총수익률" in result

# 예수금 조회 테스트
def test_get_deposit(account_service):
    result = account_service.get_deposit()
    assert isinstance(result, Dict)
    assert "예수금" in result
    assert "출금가능금액" in result

# 보유 종목 조회 테스트
def test_get_holding_stocks(account_service):
    result = account_service.get_holding_stocks()
    assert isinstance(result, List)
    assert len(result) > 0
    for item in result:
        assert "종목코드" in item
        assert "종목명" in item
        assert "보유수량" in item
        assert "평균단가" in item
        assert "현재가" in item