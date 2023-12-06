import datetime
import json
import os
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


class UnipassApi036Response:
    def __init__(
            self,
            expFfmnBrkdCbnoQryRtnVo: dict,
    ):
        self.record = Api036ExportQueryResponse(**expFfmnBrkdCbnoQryRtnVo)
        print(f"self.record.count {self.record.count}")

    def __str__(self):
        return str(self.__dict__)


class Api036ExportQueryResponse:
    """API036 응답 객체의 최상위 노드 (XML)"""

    def __init__(
            self,
            tCnt,
            ntceInfo,
            expFfmnBrkdCbnoQryRsltVo: dict,
    ):
        self.count = tCnt
        """응답 레코드 수: -1이면 오류 코드."""
        self.notice_info = ntceInfo
        """오류 메시지"""

        # 수출 이행 내역이 여러개인 경우 list 중 첫번째 레코드를 사용한다.
        _result = expFfmnBrkdCbnoQryRsltVo
        if int(self.count) > 1:
            result = _result[0]
        else:
            result = _result

        self.result = Api036ExportQueryResult(**result)

    def __str__(self):
        return str(self.__dict__)


class Api036ExportQueryResult:
    """API036 수출 이행 내역"""

    def __init__(
            self,
            dclrDttm,
            cbno,
            vhclPrgsStts,
            expDclrNo,
    ):
        self.export_declaration_date = dclrDttm
        """수출 신고 일자"""
        self.vin = cbno
        """차대번호"""
        self.progress_status = vhclPrgsStts
        """차량 진행 상태"""
        self.export_declaration_number = expDclrNo
        """수출 신고 번호"""

    def __str__(self):
        return str(self.__dict__)


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


class UnipassApi002Response:
    def __init__(
            self,
            expDclrNoPrExpFfmnBrkdQryRtnVo: dict
    ):
        """
        수출 이행 내역 export_shipment_record
        """
        self.record = Api002ExportQueryResponse(**expDclrNoPrExpFfmnBrkdQryRtnVo)
        print(self.record.count)

    def __str__(self):
        return str(self.__dict__)


class Api002ExportQueryResponse:
    """API002 응답 객체의 최상위 노드 (XML)"""

    def __init__(
            self,
            tCnt,
            ntceInfo,
            expDclrNoPrExpFfmnBrkdQryRsltVo: dict,
            expDclrNoPrExpFfmnBrkdDtlQryRsltVo: dict,
    ):
        self.count = tCnt
        """응답 레코드 수: -1이면 오류 코드."""
        self.notice_info = ntceInfo
        """오류 메시지"""
        self.result = Api002ExportQueryResult(**expDclrNoPrExpFfmnBrkdQryRsltVo)
        """수출 이행 내역"""
        self.result_detail = Api002ExportQueryResultDetail(**expDclrNoPrExpFfmnBrkdDtlQryRsltVo)
        """수출 이행 내역 상세"""

    def __str__(self):
        return str(self.__dict__)


class Api002ExportQueryResult:
    """API002 수출 이행 내역"""

    def __init__(self,
                 mnurConm,
                 exppnConm,
                 sanm,
                 acptDt,
                 acptDttm,
                 shpmCmplYn,
                 shpmWght,
                 expDclrNo,
                 loadDtyTmlm,
                 ldpInscTrgtYn,
                 csclWght,
                 csclPckUt,
                 csclPckGcnt,
                 shpmPckUt,
                 shpmPckGcnt,
                 ):
        self.manufacturer_company_name = mnurConm
        """제조자 상호"""
        self.exporter_company_name = exppnConm
        """수출자 상호"""
        self.vessel_name = sanm
        """선박/편명"""
        self.accept_date = acptDt
        """수리일자"""
        self.accept_date_time = acptDttm
        """수리일시"""
        self.shipment_completed_yn = shpmCmplYn
        """선적 완료 여부"""
        self.shipment_weight = shpmWght
        """선적 중량"""
        self.export_declaration_number = expDclrNo
        """수출 신고 번호"""
        self.loading_deadline = loadDtyTmlm
        """적재 의무 기한"""
        self.loading_area_inspection_yn = ldpInscTrgtYn
        """적재지 검사 대상 여부"""
        self.customs_clearance_weight = csclWght
        """통관 중량"""
        self.customs_clearance_package_unit = csclPckUt
        """통관 포장 단위"""
        self.customs_clearance_package_count = csclPckGcnt
        """통관 포장 개수"""
        self.shipment_package_unit = shpmPckUt
        """선(기)적 포장 단위"""
        self.shipment_package_count = shpmPckGcnt
        """선(기)적 포장 개수"""

    def __str__(self):
        return str(self.__dict__)


class Api002ExportQueryResultDetail:
    """API002 수출 이행 내역 상세"""

    def __init__(self,
                 blNo,
                 shpmPckGcnt,
                 shpmPckUt,
                 shpmWght,
                 tkofDt,
                 ):
        self.departure_date = tkofDt
        """출항일자"""
        self.bill_of_landing_number = blNo
        """B/L 번호"""

    def __str__(self):
        return str(self.__dict__)
