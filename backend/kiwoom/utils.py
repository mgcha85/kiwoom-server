# kiwoom/utils.py
import os
import yaml
from dotenv import load_dotenv

# .env 파일 로딩
load_dotenv()


def format_stock_data(data):
    """주식 데이터 포맷팅"""
    formatted_data = {
        "code": data.get("code", ""),
        "name": data.get("name", ""),
        "price": int(data.get("price", 0)),
        "volume": int(data.get("volume", 0)),
    }
    return formatted_data


def format_order_data(data):
    """주문 데이터 포맷팅"""
    formatted_data = {
        "order_no": data.get("9203", ""),
        "code": data.get("9001", "")[1:],
        "quantity": int(data.get("900", 0)),
        "price": int(data.get("901", 0)),
    }
    return formatted_data


def open_yaml(file_path: str):
    """
    YAML 파일을 안전하게 열어서 Python 딕셔너리 형태로 반환합니다.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def get_env_variable(key: str, default=None):
    """
    환경 변수(.env에 정의된 값)를 불러옵니다.
    환경 변수가 존재하지 않을 경우, default를 반환합니다.
    """
    return os.getenv(key, default)
