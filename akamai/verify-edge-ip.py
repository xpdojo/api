import csv
import time

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc

# https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials
# https://techdocs.akamai.com/developer/docs/authenticate-with-edgegrid
# https://techdocs.akamai.com/developer/docs/python
EDGERC_PATH: str = "./.edgerc"
edgerc = EdgeRc(EDGERC_PATH)
section = "default"
baseurl = "https://%s" % edgerc.get(section, "host")
s = requests.Session()
s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

# https://www.postman.com/akamai/workspace/akamai-apis/request/13085889-40173a25-c198-4826-83cf-7cb5aeb411fb
print(baseurl)


# Edge Diagnostics API > Verify Edge IP
# https://techdocs.akamai.com/edge-diagnostics/reference/post-verify-edge-ip
def verify_edge_ip(addresses: list[str]) -> dict:
    return s.post(
        url=f"{baseurl}/edge-diagnostics/v1/verify-edge-ip",
        json={"ipAddresses": addresses},
    ).json()


# Excel 파일 경로
input_file = 'input.csv'
output_file = 'output.csv'

with open(output_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['ipAddress', 'isEdgeIp'])
    writer.writeheader()

# 세 번째 컬럼의 IP 주소들을 담을 리스트
ip_list = []

# CSV 파일 읽고 IP 주소 추출
with open(input_file, mode='r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # 헤더 스킵
    for row in csv_reader:
        ip_list.append(row[2])  # 세 번째 컬럼이므로 인덱스 2


# IP 리스트를 10개씩 나누기 위한 함수
def chunk_list(_list, n):
    for i in range(0, len(_list), n):
        yield _list[i:i + n]


for ip_chunk in chunk_list(ip_list, 10):  # 10개씩 묶음
    api_responses = verify_edge_ip(ip_chunk)
    print(api_responses)

    if api_responses is None:
        raise ValueError("API 요청에 실패하여 응답을 처리할 수 없습니다.")

    # 응답의 'results'에서 IP와 'isEdgeIp' 값 추출
    results = api_responses.get('results', [])
    ip_to_edge_ip = [{'ipAddress': result['ipAddress'], 'isEdgeIp': result['isEdgeIp']} for result in results]

    # 4. 응답 데이터를 CSV 파일에 추가
    with open(output_file, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['ipAddress', 'isEdgeIp'])
        writer.writerows(ip_to_edge_ip)

    # Rate Limiting
    # https://techdocs.akamai.com/edge-diagnostics/reference/rate-limiting
    time.sleep(1)  # 1초 대기 (Rate Limiting : 60/minute)
