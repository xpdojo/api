"""
관세청 API를 이용한 수출 신고 번호 조회
국가관세종합정보망 UNI-PASS

Open API 연계 가이드_v3.0
https://unipass.customs.go.kr/csp/framework/filedownload/kcs4gDownload.do?attchFileId=MYC-20230208-00050113206OVVAQ
"""
import asyncio
import time
from pprint import pprint

import aiohttp
import xmltodict

import lib.ansi_color as cprint
import lib.json_util as json_util
from lib.unipass import (
    UnipassApi036,
    UnipassApi036Params,
    UnipassApi036Response,
    UnipassApi002,
    UnipassApi002Params,
    UnipassApi002Response,
)

vins: list[str] = [
    "HERE",
]
"""차대번호 목록"""


# logging.basicConfig(level=logging.DEBUG)


async def get_export_declaration_numbers():
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
                json_dict: dict = json_util.convert_to_json(response_json)
                pprint(json_dict)
                api_036_response: UnipassApi036Response = UnipassApi036Response(**json_dict)
                _cnt = int(api_036_response.record.count)
                if _cnt <= 0:
                    cprint.error(
                        f"{_params.dclrStrDttm} ~ {_params.dclrEndDttm} 기간 동안 차대번호(VIN) '{vin}'인 차량의 수출 신고된 건은 없습니다.")
                    exit(0)

                cprint.error(f"API036 response record count: {_cnt}")

                # cprint.debug(result[API_036_RECORD_STATUS])
                export_declaration_numbers.append(api_036_response.record.result.export_declaration_number)

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
            cprint.meta(f"export_declaration_numbers: {number}")
            _api = UnipassApi002(number)
            _params: UnipassApi002Params = _api.params
            async with session.get(url=_api.path, params=_params.to_dict()) as response:
                cprint.meta(f"API002 response status: {response.status}")
                text = await response.text(encoding='utf-8')

                # export_shipment_records.append(xmltodict.parse(text, encoding='utf-8'))
                response_json = xmltodict.parse(text, encoding='utf-8')
                json_dict: dict = json_util.convert_to_json(response_json)
                pprint(json_dict)

                api_002_response = UnipassApi002Response(**json_dict)
                cprint.error(f"API002 response record count: {api_002_response.record.count}")

                export_shipment_records.append(api_002_response)

        return export_shipment_records


if __name__ == '__main__':
    start_time = time.time()

    # 수출 신고 번호 조회
    export_declaration_numbers = asyncio.run(get_export_declaration_numbers())
    # export_declaration_numbers = ["1234567890123X"]
    for number in export_declaration_numbers:
        cprint.debug(f"API036 response: {number}")

    # 수출 이행 내역 조회
    export_shipment_responses = asyncio.run(get_export_shipment_record(export_declaration_numbers))
    for response in export_shipment_responses:
        cprint.debug(f"API002 result: {response.record.result}")
        cprint.debug(f"API002 result_detail: {response.record.result_detail}")

    cprint.meta("--- %s seconds ---" % (time.time() - start_time))
