"""편의점 재고 알림 봇
- config.json 의 상품 x 매장 조합을 조회
- 재고가 0 -> 1개 이상으로 바뀌면 텔레그램 알림
- 직전 결과는 state.json 에 저장 (GitHub Actions 가 커밋해서 다음 실행에 이어감)
"""
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from fetchers import get_fetcher

BASE = Path(__file__).parent
CONFIG_PATH = BASE / "config.json"
STATE_PATH = BASE / "state.json"
KST = timezone(timedelta(hours=9))


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def send_telegram(text):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("[알림 - 텔레그램 미설정이라 출력만]\n" + text)
        return
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    r.raise_for_status()


def main():
    cfg = load_json(CONFIG_PATH, None)
    if cfg is None:
        raise SystemExit("config.json 이 없습니다.")
    state = load_json(STATE_PATH, {})
    fetch = get_fetcher(cfg)
    notify_soldout = cfg.get("notify_soldout", False)
    now = datetime.now(KST).strftime("%m/%d %H:%M")
    changed = False

    for product in cfg["products"]:
        for store in cfg["stores"]:
            key = f'{store["code"]}:{product["code"]}'
            try:
                qty = int(fetch(store["code"], product["code"]))
            except Exception as e:  # 한 건 실패해도 나머지는 계속
                print(f"조회 실패 {store['name']} / {product['name']}: {e}")
                continue

            prev = state.get(key, 0)
            print(f"{store['name']} / {product['name']}: {prev} -> {qty}")

            if prev == 0 and qty > 0:
                send_telegram(
                    f"🔔 재고 입고! ({now})\n"
                    f"상품: {product['name']}\n매장: {store['name']}\n수량: {qty}개"
                )
            elif prev > 0 and qty == 0 and notify_soldout:
                send_telegram(
                    f"품절 ({now})\n상품: {product['name']}\n매장: {store['name']}"
                )

            if prev != qty:
                state[key] = qty
                changed = True

            # 서버에 부담 주지 않도록 요청 사이 간격
            time.sleep(random.uniform(1.0, 3.0))

    if changed:
        STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("state.json 갱신")


if __name__ == "__main__":
    main()
