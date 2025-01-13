# kiwoom/errors.py
class ParameterTypeError(Exception):
    """파라미터 타입이 일치하지 않을 경우 발생하는 예외"""
    def __init__(self, msg="파라미터 타입이 일치하지 않습니다."):
        self.msg = msg

    def __str__(self):
        return self.msg


class ParameterValueError(Exception):
    """파라미터로 사용할 수 없는 값을 사용할 경우 발생하는 예외"""
    def __init__(self, msg="파라미터로 사용할 수 없는 값입니다."):
        self.msg = msg

    def __str__(self):
        return self.msg


class KiwoomProcessingError(Exception):
    """키움 API 처리 실패 시 발생하는 예외"""
    def __init__(self, msg="키움 API 처리 실패"):
        self.msg = msg

    def __str__(self):
        return self.msg


class KiwoomConnectError(Exception):
    """키움 API 연결 실패 시 발생하는 예외"""
    def __init__(self, msg="키움 API 연결 실패"):
        self.msg = msg

    def __str__(self):
        return self.msg
