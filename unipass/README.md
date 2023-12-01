# UNI-PASS

```shell
python3 -m venv venv
source venv/bin/activate
```

```shell
python3 -m pip install -r requirements.txt
```

환경 변수에 API 키를 등록한다.

```shell
export UNIPASS_API_036_KEY=...
export UNIPASS_API_002_KEY=...
# printenv | grep UNIPASS_API_
```

조회할 VIN을 `main.py` 파일의 `vins` 변수에 등록한다.

```python
vins: list[str] = [
    "VIN_REQUIRED"
]
```

```shell
# UNIPASS_API_036_KEY=<api_036_key> UNIPASS_API_002_KEY=<api_002_key> python3 main.py
python3 main.py
```
