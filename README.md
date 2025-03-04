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
│   ├── main.py                # API 서버 및 메인 스레드 진입점
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
├── main.py                    # 전체 프로젝트 진입점 (FastAPI & PyQt5 통합)
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

## main.py 함수별 설명

`main.py` 파일은 FastAPI 서버를 실행하고, PyQt5의 이벤트 루프와 통합하여 키움증권 API와의 실시간 상호작용을 처리합니다. 아래는 주요 함수 및 API 엔드포인트에 대한 설명입니다.

- **초기 설정 및 인스턴스 생성**
  - **PyQt5 애플리케이션 생성**: `app_qt = QApplication(sys.argv)`  
    PyQt5 애플리케이션을 생성하여 이벤트 루프를 준비합니다.
  - **설정 파일 로드**: `config = open_yaml('common/config.yaml')`  
    YAML 파일을 통해 필요한 설정값을 불러옵니다.
  - **키움증권 인스턴스 생성 및 로그인**:  
    ```python
    kiwoom = Kiwoom(config)
    kiwoom.comm_connect()  # 로그인
    kiwoom.set_account()
    ```  
    키움증권 API와 연결하고 계좌 정보를 설정합니다.
  - **서비스 초기화**:  
    ```python
    account_service = AccountService(kiwoom)
    stock_service = StockService(kiwoom)
    order_service = OrderService(kiwoom)
    ```  
    계좌, 주식, 주문 관련 서비스를 각각 초기화합니다.
  - **큐 생성**:  
    ```python
    request_queue = Queue()
    response_queue = Queue()
    ```  
    API 요청과 응답을 위한 큐를 생성하여 비동기 작업을 관리합니다.

- **FastAPI 애플리케이션 및 API 엔드포인트**
  - **GET /account/balance**  
    - **설명**: 계좌 잔고를 조회하는 API 엔드포인트입니다.  
    - **동작**: 요청 큐에 `"get_account_balance"` 메시지를 넣고, 응답 큐에서 결과를 받아 반환합니다.
  
  - **GET /account/deposit**  
    - **설명**: 예수금(입금 가능한 금액)을 조회하는 API 엔드포인트입니다.
    - **동작**: `"get_deposit"` 메시지를 큐에 전달하여 예수금 정보를 가져옵니다.
  
  - **GET /account/holdings**  
    - **설명**: 보유 중인 종목 목록을 조회하는 API 엔드포인트입니다.
    - **동작**: `"get_holding_stocks"` 요청을 큐에 넣고, 보유 종목 정보를 응답 큐에서 가져옵니다.
  
  - **GET /stock/current/{code}**  
    - **설명**: 특정 종목의 현재가를 조회하는 API 엔드포인트입니다.
    - **동작**: 요청 큐에 `("get_current_price", code)` 튜플을 넣어 현재가 데이터를 요청합니다.
  
  - **GET /stock/daily/{code}**  
    - **설명**: 특정 종목의 일봉(일별) 데이터를 조회하는 API 엔드포인트입니다.
    - **동작**: 종목 코드와 조회 기간(`start_date`, `end_date`)을 전달하여 일봉 데이터를 요청합니다.
  
  - **GET /stock/minute/{code}**  
    - **설명**: 특정 종목의 분봉(분별) 데이터를 조회하는 API 엔드포인트입니다.
    - **동작**: 종목 코드와 기간(분 단위, 기본값 1분)을 전달하여 분봉 데이터를 요청합니다.
  
  - **POST /order/buy**  
    - **설명**: 매수 주문을 실행하는 API 엔드포인트입니다.
    - **동작**: 종목 코드, 주문 수량, 가격, (옵션으로) 유효기간을 받아 `"buy_order"` 요청을 큐에 넣습니다. 유효기간이 없으면 현재 시간 기준 90일 후로 설정합니다.
  
  - **POST /order/sell**  
    - **설명**: 매도 주문을 실행하는 API 엔드포인트입니다.
    - **동작**: 종목 코드, 주문 수량, 가격을 받아 `"sell_order"` 요청을 큐에 넣어 매도 주문을 처리합니다.
  
  - **POST /order/cancel**  
    - **설명**: 기존 주문을 취소하는 API 엔드포인트입니다.
    - **동작**: 주문 번호, 종목 코드, 수량을 받아 `"cancel_order"` 요청을 큐에 넣어 주문 취소를 처리합니다.
  
  - **GET /conditions/list**  
    - **설명**: 조건식 목록을 조회하는 API 엔드포인트입니다.
    - **동작**: `"get_conditions"` 메시지를 큐에 넣어 조건식 목록을 불러옵니다.
  
  - **GET /conditions/search**  
    - **설명**: 조건식에 해당하는 종목을 검색하는 API 엔드포인트입니다.
    - **동작**: 조건식 이름, 인덱스, 실시간 여부를 받아 `("search_conditions", condition_name, condition_index, is_real_time)` 요청을 큐에 넣습니다.
  
  - **POST /conditions/stop**  
    - **설명**: 진행 중인 조건식 검색을 중지하는 API 엔드포인트입니다.
    - **동작**: 조건식 이름과 인덱스를 받아 `("stop_conditions", condition_name, condition_index)` 요청을 큐에 넣어 조건 검색 중지를 실행합니다.

- **백그라운드 작업 처리 함수**
  - **process_requests**  
    - **설명**: 큐에 들어온 요청들을 지속적으로 처리하는 함수입니다.  
    - **동작**:  
      - 큐에서 요청(task)을 확인한 후, 요청 타입에 따라 적절한 서비스(계좌, 주식, 주문) 메서드를 호출합니다.
      - 처리 결과를 응답 큐에 넣어 API 엔드포인트에서 결과를 반환할 수 있도록 합니다.
  
  - **run_fastapi**  
    - **설명**: FastAPI 애플리케이션을 실행하는 함수입니다.
    - **동작**: `uvicorn.run`을 통해 로컬호스트(127.0.0.1)의 8000 포트에서 서버를 실행합니다.

- **메인 실행 흐름**
  - **스레드 생성 및 실행**:  
    - `process_requests` 함수와 `run_fastapi` 함수를 각각 별도의 데몬 스레드로 실행하여, API 요청과 백그라운드 작업이 병행되도록 합니다.
  - **PyQt5 애플리케이션 실행**:  
    - 메인 스레드에서는 PyQt5의 이벤트 루프(`app_qt.exec_()`)를 실행하여, GUI 관련 작업 및 키움증권 API와의 실시간 상호작용을 처리합니다.

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
- 키움증권 API가 Python3 32비트 Windows 환경에 고정되어 있어, 해당 환경에 맞게 개발되어야 하므로 제한 사항이 존재합니다.
- 온라인 상의 다양한 전문가들과 함께 프로젝트를 발전시켜 나갈 계획이므로, 자유로운 의견 개진 및 기여를 부탁드립니다.

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다.

---

문의 사항이나 제안 사항이 있으시면, 언제든지 이슈를 등록해 주세요.
