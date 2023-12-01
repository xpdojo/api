import json
from typing import Any


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
