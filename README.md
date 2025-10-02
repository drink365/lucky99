# 幸運99（Lucky99）— Stripe 訂閱 + Webhook 版

## 安裝
```
pip install -r requirements.txt
```

## 設定 `.streamlit/secrets.toml`
```
[stripe]
secret_key = "sk_live_or_test_xxx"
publishable_key = "pk_live_or_test_xxx"
price_pro = "price_xxx_pro_monthly"
price_vip = "price_xxx_vip_monthly"
webhook_secret = "whsec_xxx"
app_base_url = "https://你的 App 網址"
```

## 啟動 App
```
streamlit run app.py
```

## 啟動 Webhook 伺服器（本機或雲端）
```
export STRIPE_SECRET=sk_test_xxx
export STRIPE_WEBHOOK_SECRET=whsec_xxx
python webhook.py
```
或以 Stripe CLI 轉送到本機：
```
stripe login
stripe listen --forward-to localhost:8000/stripe/webhook
```

## Stripe 設定步驟
1. 建立 Products：`Lucky99 Pro`、`Lucky99 VIP`
2. 各自建立 Prices（Monthly）→ 把 `price_id` 填入 secrets 的 `price_pro` / `price_vip`
3. 建立 Webhook endpoint（或用 CLI）→ 事件至少勾選：
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. 把 Webhook signing secret 貼到 `webhook_secret`

事件到達後，`webhook.py` 會把授權寫入 `data/subscriptions.csv`：
```
user,plan,stripe_customer,stripe_subscription,current_period_end,status,updated_at
Grace,VIP,cus_xxx,sub_xxx,1735689600,active,2025-10-02T12:00:00
```
App 讀取該檔決定是否解鎖 Pro/VIP。
