import csv
import time
import argparse

import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc

# python3 verify-edge-ip.py waf-dropped.csv -o waf-dropped-edge-ip.csv
# example: https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials
"""
[default] 
client_secret = abcdEcSnaAt123FNkBxy456z25qx9Yp5CPUxlEfQeTDkfh4QA=I 
host = akab-lmn789n2k53w7qrs10cxy-nfkxaa4lfk3kd6ym.luna.akamaiapis.net 
access_token = akab-zyx987xa6osbli4k-e7jf5ikib5jknes3
client_token = akab-nomoflavjuc4422-fa2xznerxrm3teg7
"""

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


def main():
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='Akamai Edge IP 검증 도구')
    parser.add_argument('input_file', help='입력 CSV 파일 경로')
    parser.add_argument('-o', '--output', dest='output_file', default='output.csv', help='출력 CSV 파일 경로 (기본값: output.csv)')
    args = parser.parse_args()

    # Excel 파일 경로
    input_file = args.input_file
    output_file = args.output_file

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
            ip_address = row[2]  # 세 번째 컬럼(row[2])
            ip_list.append(ip_address)

    # 중복 제거
    unique_ips = list(set(ip_list))
    print(f"총 IP 개수: {len(ip_list)}, 중복 제거 후: {len(unique_ips)}")

    # IP 리스트를 10개씩 나누기 위한 함수
    def chunk_list(_list, n):
        for i in range(0, len(_list), n):
            yield _list[i:i + n]

    for ip_chunk in chunk_list(unique_ips, 10):  # 10개씩 묶음
        api_responses = verify_edge_ip(ip_chunk)
        print(api_responses)

        if api_responses is None:
            raise ValueError("API 요청에 실패하여 응답을 처리할 수 없습니다.")

        # 응답의 'results'에서 IP와 'isEdgeIp' 값 추출
        results = api_responses.get('results', [])
        # isEdgeIp가 True인 것만 필터링
        ip_to_edge_ip = [{'ipAddress': result['ipAddress'], 'isEdgeIp': result['isEdgeIp']} 
                        for result in results if result['isEdgeIp'] is True]

        # 4. 응답 데이터를 CSV 파일에 추가
        with open(output_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['ipAddress', 'isEdgeIp'])
            writer.writerows(ip_to_edge_ip)

        # Rate Limiting
        # https://techdocs.akamai.com/edge-diagnostics/reference/rate-limiting
        time.sleep(1)  # 1초 대기 (Rate Limiting : 60/minute)


if __name__ == "__main__":
    main()
