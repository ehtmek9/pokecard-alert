"""재고 조회 부분.

- "demo"   : 테스트용. 무작위 재고를 돌려줌 (텔레그램 알림이 오는지 확인할 때 사용)
- "custom" : config.json 의 "api" 설정대로 실제 서버에 요청
             앱 트래픽에서 확인한 주소/파라미터/응답 구조를 config.json 에 적으면 코드 수정 없이 동작
"""
import json
import os
import random

import requests


def demo_fetch(store_code, product_code):
    return random.choice([0, 0, 0, 1, 3])


def _fill(obj, store_code, product_code):
    """설정 안의 {store}, {product} 자리표시자를 실제 값으로 바꿈"""
    if isinstance(obj, str):
        return obj.replace("{store}", store_code).replace("{product}", product_code)
    if isinstance(obj, dict):
        return {k: _fill(v, store_code, product_code) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fill(v, store_code, product_code) for v in obj]
    return obj


def _dig(data, path):
    """'data.items.0.stockQty' 같은 경로로 응답 JSON 에서 값 꺼내기"""
    for part in path.split("."):
        data = data[int(part)] if isinstance(data, list) else data[part]
    return data


def make_custom_fetch(api):
    method = api.get("method", "GET").upper()
    headers = dict(api.get("headers", {}))
    # 로그인 토큰 같은 민감한 헤더는 config.json 대신 GitHub Secret(API_HEADERS)에 JSON 으로
    if os.environ.get("API_HEADERS"):
        headers.update(json.loads(os.environ["API_HEADERS"]))

    def fetch(store_code, product_code):
        url = _fill(api["url"], store_code, product_code)
        params = _fill(api.get("params"), store_code, product_code)
        body = _fill(api.get("json"), store_code, product_code)
        r = requests.request(
            method, url, params=params, json=body, headers=headers, timeout=10
        )
        r.raise_for_status()
        qty = _dig(r.json(), api["qty_path"])
        return int(qty or 0)

    return fetch


def get_fetcher(cfg):
    mode = cfg.get("mode", "demo")
    if mode == "demo":
        return demo_fetch
    if mode == "custom":
        return make_custom_fetch(cfg["api"])
    raise ValueError(f"알 수 없는 mode: {mode}")
