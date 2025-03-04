# kiwoom/kiwoom.py
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
import logging
from datetime import datetime
from pandas import DataFrame
import time
import sys
from .errors import ParameterTypeError, KiwoomProcessingError
from .models import *
from database.database_manager import *


class Kiwoom(QAxWidget):
    def __init__(self, config):
        super().__init__()
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.config = config

        # 이벤트 루프
        self.login_loop = None
        self.request_loop = None
        self.order_loop = None
        self.order_loop = None
        self.condition_loop = None

        # 서버구분
        self.server = None

        # 조건식
        self.condition = None

        # 에러
        self.error = None

        # 주문번호
        self.order_no = ""

        # 조회
        self.inquiry = 0

        # 서버에서 받은 메시지
        self.msg = ""

        # 예수금 d+2
        self.opw00001_data = 0

        # 보유종목 정보
        self.opw00018_data = {'accountEvaluation': [], 'stocks': []}

        # 데이터 저장
        self.stock_data = {}
        self.order_data = {}
        
        self.due_date = None
        
        # 이벤트 연결
        self.OnEventConnect.connect(self.event_connect)
        self.OnReceiveTrData.connect(self.receive_tr_data)
        self.OnReceiveChejanData.connect(self.receive_chejan_data)
        self.OnReceiveConditionVer.connect(self.receive_condition_ver)
        self.OnReceiveTrCondition.connect(self.receive_tr_condition)
        # self.OnReceiveRealCondition.connect(self.receive_real_condition)

    def set_account(self):
        self.account = self.get_account()

    def get_account(self):
        cnt = int(self.get_login_info("ACCOUNT_CNT"))
        accountList = self.get_login_info("ACCNO").split(';')
        accountList = accountList[:cnt]
        try:
            idx = accountList.index(self.config['account_no'])
        except ValueError:
            raise('해당 account가 없습니다.')
        
        return accountList[idx]

    def event_connect(self, return_code):
        """로그인 이벤트 핸들러"""
        if return_code == 0:
            print("로그인 성공")
            self.server = self.get_login_info("GetServerGubun")           
            if len(self.server) == 0 or self.server != "1":
                self.msg += "실서버 연결 성공" + "\r\n\r\n"

            else:
                self.msg += "모의투자서버 연결 성공" + "\r\n\r\n"

        else:
            print(f"로그인 실패: {return_code}")

        if self.login_loop:
            self.login_loop.exit()

    def receive_tr_data(self, screen_no, request_name, tr_code, record_name, inquiry):
        """TR 데이터 수신 이벤트 핸들러"""
        print(f"TR 데이터 수신: {request_name}, account no: {self.get_account()}")
        self.order_no = self.get_comm_data(tr_code, request_name, 0, "주문번호")
        print("order_no: ", self.order_no)
        
        if request_name == "주식현재가요청":
            self.stock_data = self.get_stock_current_data(tr_code, request_name)
        elif request_name == "주식일봉차트요청":
            self.stock_data = self.get_stock_daily_data(tr_code, request_name)
        elif request_name == "주식분봉차트조회":
            self.stock_data = self.get_stock_minute_data(tr_code, record_name)
        elif request_name == "계좌평가잔고내역요청":
            self.opw00018_data = self.get_opw00018_data(tr_code, request_name)
        elif request_name == "예수금상세현황요청":
            self.opw00001_data = self.get_opw00001_data(tr_code, request_name)

        if self.request_loop:
            self.request_loop.exit()
    
    def get_opw00018_data(self, tr_code, request_name):
        """계좌평가잔고내역요청 데이터 조회"""
        data = {
            "accountEvaluation": {
                "총매입금액": self.get_comm_data(tr_code, request_name, 0, "총매입금액"),
                "총평가금액": self.get_comm_data(tr_code, request_name, 0, "총평가금액"),
                "총평가손익금액": self.get_comm_data(tr_code, request_name, 0, "총평가손익금액"),
                "총수익률": self.get_comm_data(tr_code, request_name, 0, "총수익률(%)"),
                "추정예탁자산": self.get_comm_data(tr_code, request_name, 0, "추정예탁자산"),
            },
            "stocks": [],
        }

        # 보유 종목 데이터 조회
        count = self.get_repeat_cnt(tr_code, request_name)
        for i in range(count):
            stock = {
                "종목코드": self.get_comm_data(tr_code, request_name, i, "종목코드"),
                "종목명": self.get_comm_data(tr_code, request_name, i, "종목명"),
                "보유수량": self.get_comm_data(tr_code, request_name, i, "보유수량"),
                "매입가": self.get_comm_data(tr_code, request_name, i, "매입가"),
                "현재가": self.get_comm_data(tr_code, request_name, i, "현재가"),
                "평가손익": self.get_comm_data(tr_code, request_name, i, "평가손익"),
                "수익률": self.get_comm_data(tr_code, request_name, i, "수익률(%)"),
            }
            data["stocks"].append(stock)
        return data

    def get_opw00001_data(self, tr_code, request_name):
        """예수금상세현황요청 데이터 조회"""
        data = {
            "예수금": self.get_comm_data(tr_code, request_name, 0, "예수금"),
            "출금가능금액": self.get_comm_data(tr_code, request_name, 0, "출금가능금액"),
        }
        return data

    def set_order_data(self, fid_list):
        # 주문 데이터 생성
        order_data = {}
        for fid in map(int, fid_list.split(';')):
            if fid in self.config['chejan_data_mapping']:
                key = self.config['chejan_data_mapping'][fid]

                if key == 'order_time':
                    value = datetime.now().strftime('%Y%m%d') + self.get_chejan_data(fid).strip() # 시간만 있기 때문에 날짜를 더한다.
                elif key == 'code':
                    value = self.get_chejan_data(fid).strip()[1:] # prefix remove
                else:
                    value = self.get_chejan_data(fid).strip()
                
                order_data[key] = value
        return order_data

    def receive_chejan_data(self, gubun, item_cnt, fid_list):        
        """체결 데이터 수신 이벤트 핸들러"""
        print(f"체결 데이터 수신: {gubun}")

        if gubun != '0':
            if self.order_loop:
                self.order_loop.exit()
            return

        self.order_data = self.set_order_data(fid_list)
        if 'order_num' not in self.order_data:
            self.order_data['order_num'] = ''

        # Order시 저장
        db_path = self.config['db_path']
        insert_order_response(self.order_data, db_path)

        if self.order_data['cum_price'] == '0':
            if self.order_loop:
                self.order_loop.exit()
            return
        
        print(self.order_data)

        # 체결시 저장
        if self.order_data['remain_qty'] == '0':
            self.order_data['due_date'] = self.due_date
            update_hold_list_and_trade_history(self.order_data, db_path)

        if self.order_loop:
            self.order_loop.exit()

    def get_stock_current_data(self, tr_code, request_name):
        """현재가 데이터 조회"""
        data = {
            "code": self.get_comm_data(tr_code, request_name, 0, "종목코드"),
            "name": self.get_comm_data(tr_code, request_name, 0, "종목명"),
            "price": self.get_comm_data(tr_code, request_name, 0, "현재가"),
            "volume": self.get_comm_data(tr_code, request_name, 0, "거래량"),
        }
        return data

    def get_stock_daily_data(self, tr_code, request_name):
        """일봉 데이터 조회"""
        data = []
        count = self.get_repeat_cnt(tr_code, request_name)

        for i in range(count):
            item = {
                "date": self.get_comm_data(tr_code, request_name, i, "일자"),
                "open": self.get_comm_data(tr_code, request_name, i, "시가"),
                "high": self.get_comm_data(tr_code, request_name, i, "고가"),
                "low": self.get_comm_data(tr_code, request_name, i, "저가"),
                "close": self.get_comm_data(tr_code, request_name, i, "현재가"),
                "volume": self.get_comm_data(tr_code, request_name, i, "거래량"),
            }
            data.append(item)
        return data[::-1]
        
    def get_stock_minute_data(self, trcode: str, record_name: str):
        """분봉 데이터 가공"""
        data_count = self.get_repeat_cnt(trcode, record_name)
        stock_data = []
        
        for i in range(data_count):
            time = self.get_comm_data(trcode, record_name, i, "체결시간")
            open = self.get_comm_data(trcode, record_name, i, "시가")
            low = self.get_comm_data(trcode, record_name, i, "저가")
            high = self.get_comm_data(trcode, record_name, i, "고가")
            close = self.get_comm_data(trcode, record_name, i, "현재가")
            volume = self.get_comm_data(trcode, record_name, i, "거래량")

            stock_data.append({
                "time": time,
                "open": open,
                "low": low,
                "high": high,
                "close": close,
                "volume": volume
            })
        
        return stock_data

    def get_chejan_data(self, fid):
        """체결 데이터 조회"""
        if not isinstance(fid, int):
            raise ParameterTypeError()

        cmd = 'GetChejanData("%s")' % fid
        data = self.dynamicCall(cmd)
        return data

    def comm_connect(self):
        """로그인 요청"""
        self.dynamicCall("CommConnect()")
        self.login_loop = QEventLoop()
        self.login_loop.exec_()

    def get_login_info(self, tag):
        """로그인 정보 조회"""
        return self.dynamicCall("GetLoginInfo(QString)", tag)

    def set_input_value(self, key, value):
        """TR 입력값 설정"""
        self.dynamicCall("SetInputValue(QString, QString)", key, value)

    def comm_rq_data(self, request_name, tr_code, inquiry, screen_no):
        """TR 요청"""
        self.dynamicCall("CommRqData(QString, QString, int, QString)", request_name, tr_code, inquiry, screen_no)
        self.request_loop = QEventLoop()
        self.request_loop.exec_()

    def get_comm_data(self, tr_code, request_name, index, item_name):
        """TR 데이터 조회"""
        return self.dynamicCall("GetCommData(QString, QString, int, QString)", tr_code, request_name, index, item_name).strip()

    def get_repeat_cnt(self, tr_code, request_name):
        """반복 데이터 개수 조회"""
        return self.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, request_name)

    def send_order(self, request_name, screen_no, account_no, order_type, code, quantity, price, hoga_type, order_no, due_date=None):
        """
        주식 주문 메서드

        sendOrder() 메소드 실행시,
        OnReceiveMsg, OnReceiveTrData, OnReceiveChejanData 이벤트가 발생한다.
        이 중, 주문에 대한 결과 데이터를 얻기 위해서는 OnReceiveChejanData 이벤트를 통해서 처리한다.
        OnReceiveTrData 이벤트를 통해서는 주문번호를 얻을 수 있는데, 주문후 이 이벤트에서 주문번호가 ''공백으로 전달되면,
        주문접수 실패를 의미한다.

        :param requestName: string - 주문 요청명(사용자 정의)
        :param screenNo: string - 화면번호(4자리)
        :param accountNo: string - 계좌번호(10자리)
        :param orderType: int - 주문유형(1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정)
        :param code: string - 종목코드
        :param qty: int - 주문수량
        :param price: int - 주문단가
        :param hogaType: string - 거래구분(00: 지정가, 03: 시장가, 05: 조건부지정가, 06: 최유리지정가, 그외에는 api 문서참조)
        :param originOrderNo: string - 원주문번호(신규주문에는 공백, 정정및 취소주문시 원주문번호르 입력합니다.)
        """
        if due_date:
            self.due_date = due_date

        returnCode = self.dynamicCall(
            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            [request_name, screen_no, account_no, order_type, code, quantity, price, hoga_type, order_no],
        )
        if returnCode != ReturnCode.OP_ERR_NONE:
            raise KiwoomProcessingError("sendOrder(): " + ReturnCode.CAUSE[returnCode])

        self.order_loop = QEventLoop()
        self.order_loop.exec_()

    def get_condition_load(self):
        """ 조건식 목록 요청 메서드 """
        if not self.get_connect_state():
            raise Exception("Not connected")

        isLoad = self.dynamicCall("GetConditionLoad()")

        if not isLoad:
            raise Exception("get_condition_load(): 조건식 요청 실패")

        self.condition_loop = QEventLoop()
        self.condition_loop.exec_()

    def get_condition_name_list(self):
        """ 조건식 획득 메서드 """
        data = self.dynamicCall("GetConditionNameList()")

        if data == "":
            raise Exception("get_condition_name_list(): 사용자 조건식이 없습니다.")

        condition_list = data.split(';')
        del condition_list[-1]

        condition_dictionary = {}
        for condition in condition_list:
            key, value = condition.split('^')
            condition_dictionary[int(key)] = value

        return condition_dictionary

    def send_condition(self, screen_no, condition_name, condition_index, is_real_time):
        """ 종목 조건검색 요청 메서드 """
        if not self.get_connect_state():
            raise Exception("Not connected")

        isRequest = self.dynamicCall("SendCondition(QString, QString, int, int)",
                                     screen_no, condition_name, condition_index, is_real_time)

        if not isRequest:
            raise Exception("send_condition(): 조건검색 요청 실패")

        self.condition_loop = QEventLoop()
        self.condition_loop.exec_()

        return self.codeList

    def send_condition_stop(self, screen_no, condition_name, condition_index):
        """ 종목 조건검색 중지 메서드 """
        if not self.get_connect_state():
            raise Exception("Not connected")

        self.dynamicCall("SendConditionStop(QString, QString, int)", screen_no, condition_name, condition_index)

    def receive_condition_ver(self, ret, msg):
        """ 조건식 목록 요청 이벤트 핸들러 """
        if ret == 1:
            print("조건식 목록 요청 성공")
        else:
            print("조건식 목록 요청 실패")
        if self.condition_loop:
            self.condition_loop.exit()

    def receive_tr_condition(self, screen_no, code_list, condition_name, condition_index, inquiry):
        """ 종목 조건검색 요청 이벤트 핸들러 """
        self.codeList = code_list.split(';') if code_list else []
        if self.condition_loop:
            self.condition_loop.exit()

    def receive_real_condition(self, code, event, condition_name, condition_index):
        """ 종목 조건검색 실시간 이벤트 핸들러 """
        print(f"실시간 조건검색: 종목코드: {code}, 이벤트: {event}, 조건명: {condition_name}, 조건인덱스: {condition_index}")

    def get_connect_state(self):
        """ 연결 상태 확인 메서드 """
        state = self.dynamicCall("GetConnectState()")
        return state
