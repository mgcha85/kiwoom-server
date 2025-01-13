# api/routes/condition.py
from fastapi import APIRouter, HTTPException, Depends
from backend.services.condition_service import ConditionService
from api.dependencies import get_kiwoom

router = APIRouter()

@router.get("/conditions")
def get_condition_list(kiwoom: ConditionService = Depends(get_kiwoom)):
    """조건식 목록 조회"""
    try:
        return kiwoom.get_condition_list()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search")
def search_by_condition(condition_name: str, condition_index: int, is_real_time: bool = False, kiwoom: ConditionService = Depends(get_kiwoom)):
    """조건식으로 종목 검색"""
    try:
        return kiwoom.search_by_condition(condition_name, condition_index, is_real_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stop")
def stop_condition_search(condition_name: str, condition_index: int, kiwoom: ConditionService = Depends(get_kiwoom)):
    """조건식 검색 중지"""
    try:
        kiwoom.stop_condition_search(condition_name, condition_index)
        return {"message": "Condition search stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
