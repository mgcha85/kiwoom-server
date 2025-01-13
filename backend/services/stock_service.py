# services/stock_service.py
from typing import Dict, List, Union
from backend.kiwoom import Kiwoom

class StockService:
    def __init__(self, kiwoom: Kiwoom):
        self.kiwoom = kiwoom

    def get_current_price(self, code: str) -> Dict[str, Union[str, int]]:
        """현재가 정보 조회"""
        try:
            self.kiwoom.set_input_value("종목코드", code)
            self.kiwoom.comm_rq_data("주식현재가요청", "opt10001", 0, "0101")
            
            stock_data = self.kiwoom.stock_data
            return {
                "code": stock_data['code'],
                "name": stock_data['name'],
                "price": int(stock_data['price'].replace('+', '')),
                "volume": int(stock_data['volume']),
                "change": 0  # Add default change value or get from Kiwoom API
            }
        except Exception as e:
            return {"error": str(e)}
        
    def get_daily_data(self, code: str, start_date: str, end_date: str) -> List[Dict[str, str]]:
        """일봉 데이터 조회"""
        self.kiwoom.repeat = 60
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", end_date)
        self.kiwoom.set_input_value("수정주가구분", "1")
        self.kiwoom.comm_rq_data("주식일봉차트요청", "opt10081", 0, "0101")
        
        return self.kiwoom.stock_data

    def get_minute_data(self, code: str, period: int = 1) -> List[Dict[str, str]]:
        """분봉 데이터 조회"""
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("틱범위", str(period))
        self.kiwoom.set_input_value("수정주가구분", "0")
        self.kiwoom.comm_rq_data("주식분봉차트조회", "opt10080", 0, "0101")
        print(self.kiwoom.stock_data)
        return self.kiwoom.stock_data
