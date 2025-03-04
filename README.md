```markdown
# Kiwoom-Server

이 프로젝트는 한국의 키움증권 관련 Python 코드를 보다 쉽게 활용할 수 있도록 FastAPI 기반의 서버를 구현한 오픈 소스 프로젝트입니다. 단, 키움증권 API가 Python3 32비트 Windows 환경에 고정되어 있어 개발에 여러 한계가 존재합니다. 현재는 초기 버전으로, 온라인상의 다양한 전문가들과 함께 기능을 확장하고 완성도를 높여나갈 계획입니다.


## 주요 특징

- **FastAPI 기반 서버**: 비동기 처리를 지원하는 FastAPI를 활용하여 효율적인 API 서버를 구현했습니다.
- **모듈화된 구조**: API, Backend, Database, Common, Tests 등 각 기능별로 체계적으로 분리되어 있어 관리 및 확장이 용이합니다.
- **테스트 코드 포함**: 통합 테스트와 단위 테스트를 통해 코드의 안정성과 신뢰성을 검증합니다.

## 프로젝트 구조

```
kiwoom-server
├── README.md                  # 프로젝트 설명서
├── api                        # API 관련 파일 및 라우트
│   ├── dependencies.py        # API 의존성 관리
│   ├── main.py                # API 서버 진입점
│   └── routes                 # 개별 API 라우트
│       ├── account.py         # 계좌 관련 API
│       ├── condition.py       # 조건 검색 관련 API
│       ├── order.py           # 주문 관련 API
│       └── stock.py           # 주식 관련 API
├── backend                    # 백엔드 비즈니스 로직
│   ├── kiwoom                 # 키움증권 관련 모듈
│   │   ├── errors.py          # 에러 핸들링
│   │   ├── kiwoom.py          # 키움증권 API 연동
│   │   ├── models.py          # 데이터 모델
│   │   └── utils.py           # 유틸리티 함수
│   ├── models                 # 기타 데이터 모델
│   │   ├── account.py
│   │   ├── order.py
│   │   └── stock.py
│   └── services               # 서비스 계층
│       ├── account_service.py
│       ├── condition_service.py
│       ├── order_service.py
│       └── stock_service.py
├── common                     # 공통 설정 및 문서
│   ├── config.yaml            # 설정 파일
│   └── folder_summary.md      # 폴더 구조 요약
├── database                   # 데이터베이스 관련 파일
│   ├── database_manager.py    # 데이터베이스 관리 모듈
├── main.py                    # 전체 프로젝트 진입점
├── requirements.txt           # Python 패키지 의존성 목록
└── tests                      # 테스트 코드
    ├── integration            # 통합 테스트
    │   ├── test_api.py
    │   └── test_backend.py
    └── unit                   # 단위 테스트
        ├── test_account.py
        ├── test_order.py
        └── test_stock.py
```

## 설치 및 실행 방법

1. **의존성 설치**

   ```bash
   pip install -r requirements.txt
   ```

2. **서버 실행**

   ```bash
   uvicorn api.main:app --reload
   ```

3. **테스트 실행**

   ```bash
   pytest
   ```

## 기여 방법

- 프로젝트는 오픈 소스로 공개되어 있으며, 기능 추가 및 개선을 위한 기여를 환영합니다.
- GitHub 이슈와 풀 리퀘스트(PR)를 통해 제안 및 수정 사항을 공유해 주세요.
- 코드 스타일과 컨벤션을 준수해 주시면 감사하겠습니다.

## 주의 사항

- 현재는 초기 버전으로 완성본이 아니며, 지속적인 업데이트와 개선이 이루어질 예정입니다.
- 온라인 상의 다양한 전문가들과 함께 프로젝트를 발전시켜 나갈 계획이므로, 자유로운 의견 개진 및 기여를 부탁드립니다.

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다.

---

문의 사항이나 제안 사항이 있으시면, 언제든지 이슈를 등록해 주세요.
```