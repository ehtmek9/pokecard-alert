# 편의점 재고 알림 봇

5분마다 재고를 조회해서, 재고가 들어오면 텔레그램으로 알려줘요. GitHub Actions에서 돌아가니까 컴퓨터를 켜둘 필요가 없어요.

## 1단계: 텔레그램 봇 만들기 (5분)

1. 텔레그램에서 **@BotFather** 를 검색해 `/newbot` 을 입력해요. 이름을 정하면 **토큰**(`123456:ABC...`)을 받아요.
2. 방금 만든 봇과의 대화방에 들어가서 아무 메시지나 보내요.
3. 브라우저에서 `https://api.telegram.org/bot<토큰>/getUpdates` 를 열어 `"chat":{"id":숫자` 부분의 숫자를 찾아요. 이게 **채팅 ID**예요.

## 2단계: GitHub에 올리기

1. GitHub에서 새 저장소를 만들어요. Public(공개)이면 Actions를 무제한 무료로 쓸 수 있어요. 비공개는 월 2,000분까지만 무료라 5분 간격으로 돌리면 한도를 넘어요. 토큰은 Secrets에 넣기 때문에 공개 저장소여도 노출되지 않아요.
2. 이 폴더 안의 파일을 전부 업로드해요. `.github` 폴더도 꼭 함께 올려야 해요.
3. 저장소의 **Settings → Secrets and variables → Actions → New repository secret** 에서 아래 두 개를 추가해요.
   - `TELEGRAM_TOKEN` : 봇 토큰
   - `TELEGRAM_CHAT_ID` : 채팅 ID
4. **Actions** 탭 → `stock-check` → **Run workflow** 를 눌러 수동으로 실행해봐요.
   - 처음 설정은 `"mode": "demo"`(무작위 재고)라서, 실행하면 텔레그램 알림이 와야 정상이에요.

## 3단계: 실제 재고 조회 연결

`config.json` 에서 다음을 바꿔요.

- `"mode": "demo"` → `"mode": "custom"`
- `products` : 감시할 상품 이름과 바코드(13자리)
- `stores` : 감시할 매장 이름과 매장코드
- `api` : 앱 트래픽에서 확인한 재고조회 요청 정보
  - `url`, `params` : 매장코드 자리에는 `{store}`, 상품코드 자리에는 `{product}` 를 넣어요.
  - POST 요청이면 `"method": "POST"` 로 바꾸고 본문 내용을 `json` 에 넣어요.
  - `qty_path` : 응답 JSON에서 재고 수량이 있는 위치예요.
    예를 들어 응답이 `{"data":{"items":[{"qty":3}]}}` 라면 `data.items.0.qty` 라고 적어요.
- 로그인 토큰처럼 민감한 헤더는 `config.json` 에 적지 말고, Secret `API_HEADERS` 에 JSON 형식으로 넣어요.
  예: `{"Authorization":"Bearer ..."}`

## 내 PC에서 테스트

```
pip install requests
python main.py
```

텔레그램 환경변수가 없으면 알림 내용을 화면에 출력만 해요.

## 참고

- `notify_soldout: true` 로 바꾸면 품절될 때도 알림이 와요.
- 해외 IP라서 편의점 서버가 막는 경우에는, 같은 코드를 집 PC나 국내 서버에서 작업 스케줄러나 cron으로 5분마다 실행하면 돼요.
- 너무 짧은 간격이나 너무 많은 매장/상품 조합은 차단의 원인이 돼요. 꼭 필요한 만큼만 설정하세요.
