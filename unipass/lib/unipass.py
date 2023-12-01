import json
import os
import datetime
from enum import Enum

UNIPASS_HOST = "https://unipass.customs.go.kr:38010/ext/rest"
"""UNI-PASS API 호스트"""


class ExportDeclarationStatus(Enum):
    OK = "해당 차대번호로 수출 신고된 건은 수리된 상태입니다."
    CACNEL = "해당 차대번호로 수출 신고된 건은 수리 후 취소되었습니다."
    COMPLETE = "해당 차대번호로 수출 신고된 건은 선적이 완료된 상태입니다."
    NONE = "조회결과가 존재하지 않습니다."  # 없으면 그냥 (tCnt: 0)


today = datetime.date.today()
before_one_year = (today - datetime.timedelta(days=365))
start_date = before_one_year.strftime("%Y%m%d")
"""조회기간 시작일자"""
end_date = today.strftime("%Y%m%d")
"""조회기간 종료일자"""


class UnipassApi002:
    def __init__(self, number):
        self.number = number
        """수출신고번호"""
        self.path: str = f"{UNIPASS_HOST}/expDclrNoPrExpFfmnBrkdQry/retrieveExpDclrNoPrExpFfmnBrkd"
        """API002 경로"""

    @property
    def params(self):
        return UnipassApi002Params(self.number)


class UnipassApi002Params:
    def __init__(self, number):
        self.crkyCn: str = os.getenv('UNIPASS_API_002_KEY')
        """인증키"""
        self.expDclrNo: str = number
        """수출신고번호"""
        self.blNo: str = ''
        """B/L 번호"""

    def to_dict(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))


class UnipassApiResponse002:
    def __init__(self, json_dict: dict):
        API_002_RESPONSE = 'expDclrNoPrExpFfmnBrkdQryRtnVo'
        """API002 응답 객체의 최상위 노드 (XML)"""
        API_002_RECORD = 'expDclrNoPrExpFfmnBrkdQryRsltVo'
        """API036 수출 이행 내역"""
        API_002_RECORD_DETAIL = 'expDclrNoPrExpFfmnBrkdDtlQryRsltVo'
        """API036 수출 이행 내역 상세"""

        self.record_count = json_dict[API_002_RESPONSE]['tCnt']
        """응답 레코드 수: -1이면 오류 코드."""
        self.notice_info = json_dict[API_002_RESPONSE]['ntceInfo']
        """오류 메시지"""

        # 수출 이행 내역이 여러개인 경우 list 중 첫번째 레코드를 사용한다.
        record = json_dict[API_002_RESPONSE][API_002_RECORD]
        record_detail = json_dict[API_002_RESPONSE][API_002_RECORD_DETAIL]

        self.departure_date = record_detail['tkofDt']
        """출항일자"""
        self.bill_of_landing_number = record_detail['blNo']
        """B/L 번호"""
        self.manufacturer_company_name = record['mnurConm']
        """제조자 상호"""
        self.exporter_company_name = record['exppnConm']
        """수출자 상호"""
        self.vessel_name = record['sanm']
        """선박/편명"""
        self.accept_date = record['acptDt']
        """수리일자"""
        self.accept_date_time = record['acptDttm']
        """수리일시"""
        self.shipment_completed_yn = record['shpmCmplYn']
        """선적 완료 여부"""
        self.shipment_weight = record['shpmWght']
        """선적 중량"""
        self.export_declaration_number = record['expDclrNo']
        """수출 신고 번호"""
        self.loading_deadline = record['loadDtyTmlm']
        """적재 의무 기한"""
        self.loading_area_inspection_yn = record['ldpInscTrgtYn']
        """적재지 검사 대상 여부"""
        self.customs_clearance_weight = record['csclWght']
        """통관 중량"""
        self.customs_clearance_package_unit = record['csclPckUt']
        """통관 포장 단위"""
        self.customs_clearance_package_count = record['csclPckGcnt']
        """통관 포장 개수"""
        self.shipment_package_unit = record['shpmPckUt']
        """선(기)적 포장 단위"""
        self.shipment_package_count = record['shpmPckGcnt']
        """선(기)적 포장 개수"""

    def __str__(self):
        return str(self.__dict__)


class UnipassApi036:
    def __init__(self, vin):
        self.vin = vin
        """차대번호"""
        self.path: str = f"{UNIPASS_HOST}/expFfmnBrkdCbnoQry/retrieveExpFfmnBrkdCbnoQryRtnVo"
        """API036 경로"""

    @property
    def params(self):
        return UnipassApi036Params(self.vin)


class UnipassApi036Params:
    def __init__(self, vin):
        self.crkyCn: str = os.getenv('UNIPASS_API_036_KEY')
        """인증키"""
        self.dclrStrDttm: str = start_date
        """조회기간 시작일자"""
        self.dclrEndDttm: str = end_date
        """조회기간 종료일자"""
        self.cbno = vin
        """차대번호"""

    def to_dict(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))


class _DeprecatedUnipassResponse036:
    """Deprecated"""

    def __init__(self, json_dict: dict):
        for key, value in json_dict.items():
            setattr(self, key, json_dict[key])

    def __str__(self):
        return str(self.__dict__)


class UnipassApiResponse036:
    def __init__(self, json_dict: dict):
        API_036_RESPONSE = 'expFfmnBrkdCbnoQryRtnVo'
        """API036 응답 객체의 최상위 노드 (XML)"""
        API_036_RECORD = 'expFfmnBrkdCbnoQryRsltVo'
        """API036 수출 이행 내역"""

        self.record_count = json_dict[API_036_RESPONSE]['tCnt']
        """응답 레코드 수: -1이면 오류 코드."""
        self.notice_info = json_dict[API_036_RESPONSE]['ntceInfo']
        """오류 메시지"""

        # 수출 이행 내역이 여러개인 경우 list 중 첫번째 레코드를 사용한다.
        _result = json_dict[API_036_RESPONSE][API_036_RECORD]
        if int(self.record_count) > 1:
            result = _result[0]
        else:
            result = _result

        self.export_declaration_date = result['dclrDttm']
        """수출 신고 일자"""
        self.vin = result['cbno']
        """차대번호"""
        self.progress_status = result['vhclPrgsStts']
        """차량 진행 상태"""
        self.export_declaration_number = result['expDclrNo']
        """수출 신고 번호"""

    def __str__(self):
        return str(self.__dict__)
