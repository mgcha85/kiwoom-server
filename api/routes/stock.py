from fastapi import APIRouter, Depends, HTTPException
from backend.services.stock_service import StockService
from backend.kiwoom import Kiwoom

router = APIRouter()

def get_stock_service(kiwoom: Kiwoom) -> StockService:
    return StockService(kiwoom)

@router.get("/current/{code}")
def get_current_price(code: str, kiwoom: Kiwoom = Depends()):
    """현재가 조회"""
    stock_service = get_stock_service(kiwoom)
    try:
        return stock_service.get_current_price(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/daily/{code}")
def get_daily_data(code: str, start_date: str, end_date: str, kiwoom: Kiwoom = Depends()):
    """일봉 데이터 조회"""
    stock_service = get_stock_service(kiwoom)
    try:
        return stock_service.get_daily_data(code, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
