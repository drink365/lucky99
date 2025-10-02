import os
import streamlit as st
import pandas as pd
import stripe
import datetime

# 初始化 Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_xxx")  # 改成你的 key

DATA_DIR = "data"
SUBS_FILE = os.path.join(DATA_DIR, "subscriptions.csv")

# ---------------------------
# 工具函數
# ---------------------------
def safe_read_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

def get_subscription(user):
    df = safe_read_csv(SUBS_FILE)
    if df.empty:
        return None
    row = df[df["user"] == user]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

def subscription_status(sub):
    """根據 subscription dict 回傳狀態與到期日"""
    if not sub:
        return "free", None
    status = sub.get("status", "canceled")
    ts = sub.get("current_period_end")
    expiry = None
    if pd.notnull(ts):
        try:
            expiry = datetime.datetime.fromtimestamp(int(ts))
        except:
            expiry = None
    return status, expiry

# ---------------------------
# past_due banner
# ---------------------------
def show_past_due_banner(user, sub):
    st.warning("⚠️ 您的帳號付款失敗，目前功能受限，請重新付款以恢復使用權限。")

    if st.button("💳 重新付款", key="retry_payment"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{
                    "price": "price_xxxxxxxx",  # 換成你的 Stripe price_id
                    "quantity": 1,
                }],
                customer=sub.get("stripe_customer", ""),
                success_url="https://lucky99.streamlit.app/success",
                cancel_url="https://lucky99.streamlit.app/cancel"
            )
            st.markdown(f"[👉 前往付款頁面]({session.url})", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"建立付款連結時發生錯誤：{e}")

# ---------------------------
# Streamlit 介面
# ---------------------------
st.set_page_config(page_title="幸運99", page_icon="🍀", layout="wide")
st.title("🍀 幸運99｜抽卡與運勢平台")

username = st.text_input("請輸入你的稱呼（測試：test_pro / test_vip / test_trial / test_expired / test_past_due）")

if username:
    sub = get_subscription(username)
    status, expiry = subscription_status(sub)

    # 狀態顯示
    if status in ["active", "trialing"]:
        st.success(f"✅ 歡迎回來，{username}！目前方案：{sub['plan']}（到期日 {expiry}）")
        st.write("👉 你可以使用所有付費功能，包括詳細分析與多張抽卡。")

    elif status == "past_due":
        show_past_due_banner(username, sub)

    elif status == "canceled" or not sub:
        st.info(f"🔓 哈囉 {username}！你目前是 Free 方案。")
        st.write("👉 升級後可以解鎖更多學派與功能！")

    else:
        st.warning(f"⚠️ 狀態：{status}（可能是未知或測試狀態）")

else:
    st.info("請先輸入你的稱呼，才能體驗抽卡。")

