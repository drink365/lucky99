# 幸運99（Lucky99）— ALL-IN-ONE（學派擴充 + Stripe 訂閱 + 會員浮標）

## 方案
- Free：單張塔羅 + 各學派【基本】分析
- Pro：解鎖塔羅三張 + 各學派【詳細】分析（星座 / 生肖 / 紫微 / 八字 / 靈數）
- VIP：Pro 全部 + 每月 PDF 報告

## 安裝
```
pip install -r requirements.txt
streamlit run app.py
```

## 設定 `.streamlit/secrets.toml`
```
[stripe]
secret_key = "sk_test_xxx"
publishable_key = "pk_test_xxx"
price_pro = "price_xxx_pro_monthly"
price_vip = "price_xxx_vip_monthly"
webhook_secret = "whsec_xxx"
app_base_url = "https://你的 App 網址"
```

## 啟動 Webhook（本機）
```
export STRIPE_SECRET=sk_test_xxx
export STRIPE_WEBHOOK_SECRET=whsec_xxx
python webhook.py
# Stripe CLI
stripe login
stripe listen --forward-to localhost:8000/stripe/webhook
```
