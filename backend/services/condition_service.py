# backend/services/condition_service.py
from backend.kiwoom import Kiwoom

class ConditionService:
    def __init__(self, kiwoom: Kiwoom):
        self.kiwoom = kiwoom

    def get_condition_list(self):
        """조건식 목록 조회"""
        self.kiwoom.get_condition_load()
        return self.kiwoom.get_condition_name_list()

    def search_by_condition(self, condition_name: str, condition_index: int, is_real_time: bool = False):
        """조건식으로 종목 검색"""
        return self.kiwoom.send_condition("0101", condition_name, condition_index, int(is_real_time))

    def stop_condition_search(self, condition_name: str, condition_index: int):
        """조건식 검색 중지"""
        self.kiwoom.send_condition_stop("0101", condition_name, condition_index)
