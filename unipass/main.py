"""
관세청 API를 이용한 수출 신고 번호 조회
국가관세종합정보망 UNI-PASS

Open API 연계 가이드_v3.0
https://unipass.customs.go.kr/csp/framework/filedownload/kcs4gDownload.do?attchFileId=MYC-20230208-00050113206OVVAQ
"""
import asyncio
import json
import os
import time
import datetime
from enum import Enum
from typing import Any

import aiohttp
import xmltodict

import lib.ansi_color as cprint

# logging.basicConfig(level=logging.DEBUG)

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
vins: list[str] = [
    "VIN_REQUIRED"
]
"""차대번호 목록"""

API_002_RESPONSE = 'expDclrNoPrExpFfmnBrkdQryRtnVo'
"""API002 응답 객체의 최상위 노드 (XML)"""


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


class UnipassResponse036:
    def __init__(self, json_dict: dict):
        for key, value in json_dict.items():
            setattr(self, key, json_dict[key])

    def __str__(self):
        return str(self.__dict__)


API_036_RESPONSE = 'expFfmnBrkdCbnoQryRtnVo'
"""API036 응답 객체의 최상위 노드 (XML)"""
API_036_RECORD_COUNT = 'tCnt'
"""응답 레코드 수"""
API_036_RECORD = 'expFfmnBrkdCbnoQryRsltVo'
"""API036 수출 이행 내역"""
API_036_RECORD_STATUS = 'vhclPrgsStts'  # API036 수출 이행 내역
"""API036 수출 이행 내역"""


async def get_export_declaration_number():
    """
    API036: 수출이행내역 조회 by 차대번호
    이미 수출이 이행된 경우 신고번호가 조회되지 않는다.
    """
    export_declaration_numbers = []

    async with aiohttp.ClientSession() as session:

        for vin in vins:
            _api = UnipassApi036(vin)
            _params: UnipassApi036Params = _api.params
            cprint.debug(f"API036 params: {_params.to_dict()}")

            async with session.get(url=_api.path, params=_params.to_dict()) as response:
                cprint.meta(f"API036 response status: {response.status}")
                xml_text = await response.text(encoding='utf-8')
                response_json = xmltodict.parse(xml_text)
                json_dict: dict = convert_to_json(response_json)
                unipass: UnipassResponse036 = UnipassResponse036(json_dict)
                cprint.debug(f"API036 response {str(unipass)}")
                _cnt = int(response_json[API_036_RESPONSE][API_036_RECORD_COUNT])
                if _cnt <= 0:
                    cprint.error(
                        f"{_params.dclrStrDttm} ~ {_params.dclrEndDttm} 기간 동안 차대번호(VIN) '{vin}'인 차량의 수출 신고된 건은 없습니다.")
                    exit(0)

                cprint.error(f"API036 response record count: {_cnt}")

                _result = response_json[API_036_RESPONSE][API_036_RECORD]
                if _cnt > 1:
                    result = _result[0]
                else:
                    result = _result

                # cprint.debug(result[API_036_RECORD_STATUS])
                export_declaration_numbers.append(result['expDclrNo'])

    # cprint.debug(f"export_declaration_numbers: {export_declaration_numbers}")
    return export_declaration_numbers


async def get_export_shipment_record(export_declaration_numbers: list[str]):
    """
    API002: 수출이행내역 조회 by 신고번호

    수출의무기한을 조회하기 위해 요청한다.

    Export Shipment Record 명칭 참조: https://www.customs.go.kr/english/cm/cntnts/cntntsView.do?mi=8056&cntntsId=2732
    """
    export_shipment_records = []

    async with aiohttp.ClientSession() as session:
        for number in export_declaration_numbers:
            _api = UnipassApi002(number)
            _params = _api.params
            async with session.get(url=_api.path, params=_params.to_dict()) as response:
                cprint.meta(f"API002 response status: {response.status}")
                text = await response.text(encoding='utf-8')
                export_shipment_records.append(xmltodict.parse(text, encoding='utf-8'))

        return export_shipment_records


def convert_to_json(json_data: Any):
    """
    JSON 데이터를 출력한다.
    """
    # None, null 데이터를 처리하지 못함
    # json.decoder.JSONDecodeError: Expecting value: line 1 column 50 (char 49)
    # str 타입이어야 함
    # TypeError: the JSON object must be str, bytes or bytearray, not list
    str_records = json.dumps(json_data)
    # single quote는 JSON 형식이 아님
    # json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 3 (char 2)
    double_quote_records = str_records.replace("\'", "\"")
    json_object = json.loads(double_quote_records)
    return json_object


def main():
    start_time = time.time()

    # 수출 신고 번호 조회
    export_declaration_number = asyncio.run(get_export_declaration_number())
    # 수출 이행 내역 조회
    export_shipment_records = asyncio.run(get_export_shipment_record(export_declaration_number))

    cprint.info(f"API002 response: {convert_to_json(export_shipment_records)}")

    cprint.meta("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    main()
