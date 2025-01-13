import sqlite3
import pandas as pd
from datetime import datetime, timedelta


def get_hold_list(db_path="sqlite3/trading.sqlite3"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM hold_list", con=conn, index_col='code')
    conn.close()
    return df

def get_order_list(db_path="sqlite3/trading.sqlite3"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM order_list WHERE status='OPEN'", con=conn, index_col='order_id')
    conn.close()
    return df

def get_trade_history(db_path="sqlite3/trading.sqlite3"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM trade_history", con=conn, index_col='trade_id')
    conn.close()
    return df

def insert_order_response(order_response, db_path="sqlite3/trading.sqlite3"):
    """
    주문 응답 데이터를 `order_list` 테이블에 삽입하거나 업데이트합니다.

    Args:
        db_path (str): SQLite 데이터베이스 파일 경로
        order_response (dict): 서버로부터 받은 주문 응답 데이터
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # 주문 응답 데이터
    order_id = order_response["order_num"]
    code = order_response["code"]
    name = order_response["name"].strip()
    order_type = order_response["order_type"].strip()
    qty = int(order_response["qty"])
    remain_qty = int(order_response["remain_qty"])
    cum_price = int(order_response["cum_price"])
    fee = float(order_response["fee"])
    tax = float(order_response["tax"])
    status = order_response["status"]
    order_time = order_response.get("order_time", None)

    # INSERT 또는 UPDATE
    cursor.execute("""
    INSERT INTO order_list (order_id, code, name, order_type, qty, remain_qty, 
                            cum_price, fee, tax, status, order_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(order_id)
    DO UPDATE SET 
        remain_qty=excluded.remain_qty,
        cum_price=excluded.cum_price,
        status=excluded.status
    """, (order_id, code, name, order_type, qty, remain_qty, cum_price, fee, tax, status, order_time))

    connection.commit()
    connection.close()
    print(f"Order {order_id} processed successfully.")

def update_hold_list_and_trade_history(order_response, db_path="sqlite3/trading.sqlite3"):
    """
    주문 응답 데이터를 기반으로 `hold_list`와 `trade_history`를 업데이트합니다.

    Args:
        db_path (str): SQLite 데이터베이스 파일 경로
        order_response (dict): 서버로부터 받은 주문 응답 데이터
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # 주문 응답 데이터
    order_id = order_response["order_num"]
    code = order_response["code"]
    qty = int(order_response["qty"])
    remain_qty = int(order_response["remain_qty"])
    cum_price = int(order_response["cum_price"])
    order_type = order_response["order_type"].strip()
    fee = float(order_response["fee"])
    tax = float(order_response["tax"])
    due_date = order_response["due_date"]

    if "매수" in order_type:  # 매수 완료 시
        # hold_list 추가 또는 업데이트 (이미 존재한 경우)
        cursor.execute("""
        INSERT INTO hold_list (code, qty, avg_price, remain_qty, order_id, stop_price, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(code)
        DO UPDATE SET 
            qty = hold_list.qty + excluded.qty,
            avg_price = ((hold_list.qty * hold_list.avg_price) + (excluded.qty * excluded.avg_price)) / (hold_list.qty + excluded.qty),
            num_buy = hold_list.num_buy + 1
        """, (code, qty, cum_price // qty, remain_qty, order_id, 0, due_date))
        
        # # order_list 상태 업데이트 
        # cursor.execute("""
        # UPDATE order_list
        # SET status = '체결'
        # WHERE order_id = ? AND remain_qty = 0 AND status != '체결'
        # """, (order_id,))

    elif "매도" in order_type:  # 매도 완료 시
        # hold_list에서 데이터 가져오기
        cursor.execute("SELECT avg_price, qty, fee, tax FROM hold_list WHERE code=?", (code,))
        hold_data = cursor.fetchone()

        if hold_data:
            hold_avg_price, hold_qty, hold_fee, hold_tax = hold_data

            # 매도 후 수익 계산
            sell_price = cum_price // qty
            profit = (sell_price - hold_avg_price) * qty - fee - tax

            # 거래 기록 추가
            cursor.execute("""
            INSERT INTO trade_history (code, avg_price, qty, sell_price, stop_price, num_buy, buy_price, profit, fee, tax, buy_time, due_date, sell_time, order_id)
            SELECT code, avg_price, ?, ?, stop_price, num_buy, avg_price, ?, fee + ?, tax + ?, buy_time, due_date, CURRENT_TIMESTAMP, ?
            FROM hold_list WHERE code=?
            """, (qty, sell_price, profit, fee, tax, order_id, code))

            # 보유 수량 업데이트
            cursor.execute("""
            UPDATE hold_list
            SET qty = qty - ?, 
                num_buy = CASE WHEN qty - ? = 0 THEN 0 ELSE num_buy END
            WHERE code=?
            """, (qty, qty, code))

            # 보유 수량이 0이면 삭제
            cursor.execute("DELETE FROM hold_list WHERE qty <= 0")

    connection.commit()
    connection.close()
    print(f"Hold list and trade history updated for order {order_id}.")


def initialize_database(db_path="sqlite3/trading.sqlite3"):
    """
    SQLite 데이터베이스를 초기화하고 테이블을 생성합니다.
    :param db_path: 데이터베이스 파일 경로
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # 1. order_list 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_list (
        order_id TEXT PRIMARY KEY,          -- 주문 번호
        code TEXT NOT NULL,                 -- 종목 코드
        name TEXT,                          -- 종목명
        order_type TEXT NOT NULL,           -- 주문 유형 (매수, 매도, 매도취소 등)
        qty INTEGER NOT NULL,               -- 주문 수량
        remain_qty INTEGER,                 -- 남은 수량
        cum_price INTEGER,                  -- 체결 가격 합계
        fee FLOAT DEFAULT 0,                -- 수수료
        tax FLOAT DEFAULT 0,                -- 세금
        order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 주문 시간 (자동 설정)
        status TEXT                         -- 주문 상태 (접수, 체결 등)
    );
    """)

    # 2. hold_list 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hold_list (
        code TEXT PRIMARY KEY,              -- 종목 코드
        qty INTEGER NOT NULL,               -- 보유 수량
        avg_price INTEGER NOT NULL,         -- 평균 매수가
        remain_qty INTEGER DEFAULT 0,       -- 남은 수량
        order_id TEXT,                      -- 관련 주문 번호
        num_buy INTEGER DEFAULT 1,          -- 매수 횟수
        buy_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 매수일 (자동 설정)
        due_date TIMESTAMP,                 -- 매도 예정일
        stop_price INTEGER DEFAULT 0,       -- 스탑로스 가격
        fee FLOAT DEFAULT 0,                -- 수수료
        tax FLOAT DEFAULT 0,                -- 세금
        FOREIGN KEY(order_id) REFERENCES order_list(order_id)
    );
    """)

    # 3. trade_history 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trade_history (
        trade_id INTEGER PRIMARY KEY AUTOINCREMENT, -- 거래 번호
        code TEXT NOT NULL,                         -- 종목 코드
        avg_price INTEGER NOT NULL,                 -- 평균 매수가
        qty INTEGER NOT NULL,                       -- 매도 수량
        sell_price INTEGER NOT NULL,                -- 매도가
        stop_price INTEGER DEFAULT 0,               -- 스탑로스 가격
        num_buy INTEGER DEFAULT 1,                  -- 매수 횟수
        buy_price INTEGER NOT NULL,                 -- 매수가 (평균 매수가)
        profit INTEGER,                             -- 거래 이익 (수익)
        fee FLOAT DEFAULT 0,                        -- 수수료
        tax FLOAT DEFAULT 0,                        -- 세금
        buy_time TIMESTAMP,                         -- 매수일 (자동 설정)
        due_date TIMESTAMP,                         -- 매도 예정일
        sell_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 매도 시간 (자동 설정)
        order_id TEXT,                              -- 관련 주문 번호
        FOREIGN KEY(order_id) REFERENCES order_list(order_id)
    );
    """)

    # 4. triggers 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS triggers (
        trigger_id INTEGER PRIMARY KEY AUTOINCREMENT, -- 트리거 ID
        code TEXT NOT NULL,                            -- 종목 코드
        trigger_type TEXT NOT NULL,                    -- 트리거 유형 (예: Stop-Loss, Take-Profit)
        value INTEGER NOT NULL,                        -- 트리거 기준값 (예: 가격)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 트리거 생성 시간 (자동 설정)
    );
    """)

    connection.commit()
    connection.close()
    print("Database initialized and tables created successfully.")



if __name__ == "__main__":
    initialize_database(db_path="../kiwoom-client/sqlite3/trading.sqlite3")
