from fastapi import APIRouter, Depends, HTTPException
from backend.services.account_service import AccountService
from backend.kiwoom import Kiwoom

router = APIRouter()

def get_account_service(kiwoom: Kiwoom) -> AccountService:
    return AccountService(kiwoom)

@router.get("/balance")
def get_account_balance(kiwoom: Kiwoom = Depends()):
    """계좌 잔고 조회"""
    account_service = get_account_service(kiwoom)
    try:
        return account_service.get_account_balance()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/holdings")
def get_holding_stocks(kiwoom: Kiwoom = Depends()):
    """보유 종목 조회"""
    account_service = get_account_service(kiwoom)
    try:
        return account_service.get_holding_stocks()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
