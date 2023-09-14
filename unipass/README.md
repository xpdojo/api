# UNI-PASS

```shell
python3 -m venv .venv
source .venv/bin/activate
```

```shell
python3 -m pip install -r requirements.txt
```

```shell
export UNIPASS_API_036_KEY=...
export UNIPASS_API_002_KEY=...
```

```python
vins: list[str] = [
    "VIN_REQUIRED"
]
```

```shell
# UNIPASS_API_036_KEY=<api_036_key> UNIPASS_API_002_KEY=<api_002_key> python3 main.py
python3 main.py
```
