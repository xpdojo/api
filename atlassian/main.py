import json
import os
import sys
from datetime import datetime

import requests

# Bitbucket repository > Download 에서 가장 최근 업로드 된 파일을 다운로드한다.

workspace = "BITBUCKET_WORKSPACE"
repo_slug = "BITBUCKET_REPO_SLUG"
repository_access_token = 'BITBUCKET_REPOSITORY_ACCESS_TOKEN'

# username = 'BITBUCKET_USERNAME'
# app_password = 'BITBUCKET_PERSONAL_APP_PASSWORD'

bitbucket_download_api_url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/downloads'
headers = {
    'Authorization': f'Bearer {repository_access_token}'
}


def main():
    response = requests.get(
        url=bitbucket_download_api_url,
        # auth=HTTPBasicAuth(username, app_password))
        headers=headers)
    # pprint(response.__dir__())
    res_json = response.json()
    values = res_json.get('values')
    sorted_data = sorted(
        values,
        key=lambda x: parse_date(x['created_on']),
        reverse=True
    )
    print(json.dumps(sorted_data[0], indent=2))
    artifact = requests.get(
        url=sorted_data[0].get('links').get('self').get('href'),
        # auth=HTTPBasicAuth(username, app_password),
        headers=headers,
        stream=True
    )

    hide_cursor()
    temp_path_base = '/tmp'
    try:
        temp_path = os.path.join(temp_path_base, sorted_data[0].get('name'))
        with open(temp_path, 'wb') as f:
            total_size = sorted_data[0].get('size')
            downloaded_size = 0

            for chunk in artifact.iter_content(chunk_size=128):
                f.write(chunk)
                downloaded_size += len(chunk)
                # \r로 줄의 시작으로 커서 이동, end=''로 줄바꿈 방지 -> 한줄에 다운로드 진행률 출력
                progress_percentage = downloaded_size / total_size * 100
                print(f'\r{round(progress_percentage, 1)}% downloaded', end='')
    finally:
        show_cursor()

    # with tarfile.open(temp_path, 'r:gz') as tar:
    #     tar.extractall(temp_path_base)
    # os.remove(temp_path)


def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()


# 날짜 파싱과 정렬
def parse_date(date_str):
    return datetime.fromisoformat(date_str[:-6])  # ISO 8601 포맷을 datetime 객체로 변환


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
