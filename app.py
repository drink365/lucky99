import os, sys, hashlib
from datetime import datetime, date
import streamlit as st
import pandas as pd
import stripe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.storage import DRAW_LOG, COLS, append_row, get_subscription, get_subscription_detail
from utils.share_image import build_share_image
from schools.registry import SCHOOLS
from schools.lifepath import analysis as lifepath_analysis
from schools.west_astrology import analysis as west_analysis
from schools.tarot import analysis as tarot_intro, draw_one, draw_three
from schools.zodiac_cn import analysis as zodiac_analysis
from schools.ziwei import analysis as ziwei_analysis
from schools.bazi import analysis as bazi_analysis

st.set_page_config(page_title="幸運99", page_icon="assets/favicon.png", layout="wide")
st.markdown("<style>.block-container{max-width:1280px}</style>", unsafe_allow_html=True)

# Stripe config (optional)
cfg = st.secrets.get("stripe", {})
stripe.api_key = cfg.get("secret_key", "")

def status_and_expiry(sub: dict):
    if not sub:
        return "free", None, "Free"
    status = sub.get("status","canceled")
    plan = sub.get("plan","Free")
    ts = sub.get("current_period_end")
    expiry = None
    if pd.notnull(ts):
        try:
            expiry = datetime.fromtimestamp(int(ts))
        except Exception:
            expiry = None
    return status, expiry, plan

def show_past_due_banner(user: str, sub: dict):
    st.warning("⚠️ 您的帳號付款失敗，目前功能受限，請重新付款以恢復使用權限。")
    if st.button("💳 重新付款", key="retry_payment"):
        st.info("請在 secrets.toml 設定你的 price_id 與 app_base_url 後啟用 Stripe Checkout。")

# Header
st.image("assets/logo.png", width=80)
st.title("🌟 幸運99｜抽卡與運勢平台（完整版）")

username = st.text_input("請輸入你的稱呼（測試：test_pro / test_vip / test_trial / test_expired / test_past_due）", value=st.session_state.get("username",""))
st.session_state["username"] = username or "訪客"

# Load subscription
# subscriptions.csv 放在 data/ 中，這裡使用 utils.storage 的 get_subscription_detail 讀取
plan_label, expiry_ts, status_flag = get_subscription_detail(st.session_state["username"])
# 兼容老函式語意
status = status_flag
expiry = datetime.fromtimestamp(expiry_ts) if expiry_ts else None
plan = plan_label

# Banner by status
if status in ("active","trialing"):
    st.success(f"✅ 歡迎回來，{username}！目前方案：{plan}（到期日 {expiry if expiry else '—'}）")
elif status == "past_due":
    show_past_due_banner(username, {"plan":plan})
elif status in ("canceled", None) or plan=="Free":
    st.info(f"🔓 哈囉 {username}！你目前是 Free 方案。可先體驗基本功能。")
else:
    st.warning(f"狀態：{status}")

# --- Main body ---
def render_main(username: str, status: str, plan_label: str):
    st.markdown("---")
    st.header("📘 學派分析")
    detail = (status in ("active","trialing")) and (plan_label in ("Pro","VIP"))

    left, right = st.columns([7,5])
    with left:
        key = st.selectbox("選擇學派", list(SCHOOLS.keys()), format_func=lambda k: SCHOOLS[k]['name'])
    with right:
        st.markdown(f"**學派簡介**：{SCHOOLS[key]['desc']}")

    reqs = SCHOOLS[key]["requires"]
    a,b,c = st.columns(3)
    user_inputs = {}
    if "birth_date" in reqs:
        with a: user_inputs["birth_date"] = st.date_input("生日", value=None, min_value=date(1900,1,1), max_value=date.today())
    if "birth_time" in reqs:
        with b: user_inputs["birth_time"] = st.time_input("出生時間", value=None)
    if "gender" in reqs:
        with c: user_inputs["gender"] = st.selectbox("性別", ["女","男","其他/不方便透露"])
    if "question" in reqs:
        user_inputs["question"] = st.text_input("你的提問（例如：本月適合談合作嗎？）")

    text = ""
    if key == "lifepath":
        text = lifepath_analysis(user_inputs.get("birth_date"), detail=detail)
    elif key == "west_astrology":
        text = west_analysis(user_inputs.get("birth_date"), detail=detail)
    elif key == "tarot":
        text = tarot_intro(user_inputs.get("question"), detail=detail)
    elif key == "zodiac_cn":
        text = zodiac_analysis(user_inputs.get("birth_date"), detail=detail)
    elif key == "ziwei":
        text = ziwei_analysis(user_inputs.get("birth_date"), user_inputs.get("gender"), detail=detail)
    elif key == "bazi":
        text = bazi_analysis(user_inputs.get("birth_date"), user_inputs.get("birth_time"), detail=detail)

    if text:
        if not detail and key in ("zodiac_cn","ziwei","bazi","west_astrology","lifepath"):
            text += "\n\n👉 想看【詳細版】學派分析？升級 Pro / VIP 立即解鎖。"
        st.write(text)
    else:
        st.info("填入必要資料後，將顯示你的分析報告。")

    st.markdown("---")
    st.header("🎲 抽卡提醒")
    colA, colB = st.columns([7,5])
    with colA:
        system = st.selectbox("選擇卡系", ["貴人","幸運","勇氣","靈感"])
        tarot_mode = "單張（Free）"
        if key == "tarot":
            tarot_mode = st.radio("塔羅模式", ["單張（Free）","三張（Pro）"], horizontal=True)

        if st.button("抽一張提醒", use_container_width=True):
            samples = {
                "貴人": {"fortune":"貴人正在靠近你。","note":"允許自己接受幫助，是成熟與勇氣。","task":"主動問候一位好久不聯絡的朋友。"},
                "幸運": {"fortune":"今天的小改變會帶來好運。","note":"宇宙喜愛你的好奇。","task":"換一家咖啡店，點新口味。"},
                "勇氣": {"fortune":"行動是最好的時機。","note":"帶著害怕也能往前走。","task":"把拖延的一件事，做5分鐘。"},
                "靈感": {"fortune":"新的視角正在形成。","note":"空白是孕育新意的土壤。","task":"10分鐘自由書寫，不要修改。"},
            }
            base = samples[system]
            card = {
                "system": system,
                "school": SCHOOLS[key]["name"],
                "fortune": base["fortune"],
                "note": base["note"],
                "task": base["task"],
                "color_primary": "#F2D9B3", "color_secondary": "#FBEDE3",
                "ts": datetime.now().isoformat(timespec="seconds"),
                "user": username or "訪客",
                "school_key": key,
                "inputs": user_inputs
            }

            if key == "tarot":
                seed = f"{username}-{datetime.now().date()}-{system}"
                if "三張" in tarot_mode and not detail:
                    card["fortune"]="（Pro 付費功能）"
                    card["note"]="升級後可解鎖『過去-現在-未來』三張牌。"
                    card["task"]="先用單張模式體驗看看。"
                elif "三張" in tarot_mode:
                    tri = draw_three(seed=seed)
                    lines = [f"{t['slot']}：《{t['name']}·{t['pose']}》{t['meaning']}" for t in tri]
                    q = user_inputs.get("question") or "今天的提醒"
                    card["fortune"] = " / ".join(lines)
                    card["note"] = f"針對「{q}」，三張牌給出路徑。｜{card['note']}"
                    card["task"] = "把三件可行的小步驟寫下，先完成第一步。"
                else:
                    one = draw_one(seed=seed)
                    q = user_inputs.get("question") or "今天的提醒"
                    card["fortune"] = f"塔羅《{one['name']}·{one['pose']}》：{one['meaning']}"
                    card["note"] = f"針對「{q}」，掌握牌義行動的第一步。｜{card['note']}"
                    card["task"] = "把你可行的一步寫下，今天就做。"

            st.session_state["last_card"] = card

        card = st.session_state.get("last_card")
        if card:
            st.success(f"你抽到：**{card['system']}卡**（學派：{card['school']}）")
            with st.container(border=True):
                st.markdown(f"**籤語**：{card['fortune']}")
                st.markdown(f"**小語**：{card['note']}")
                st.markdown(f"**今日任務**：{card['task']}")
        else:
            st.info("完成上方學派分析後，再抽一張今日提醒卡 ✨")

    with colB:
        st.markdown("🖼️ **生成分享圖卡**")
        card = st.session_state.get("last_card")
        if st.button("生成 PNG 圖卡", use_container_width=True, disabled=not bool(card)):
            out_path, preview = build_share_image(card, os.path.join(os.getcwd(), "data"))
            st.image(preview, caption="分享圖預覽", use_container_width=True)
            with open(out_path, "rb") as fr:
                st.download_button("下載分享圖（PNG）", data=fr.read(), file_name=os.path.basename(out_path), mime="image/png", use_container_width=True)

# Call main render
plan_effective = plan if status in ("active","trialing") else "Free"
render_main(username, status, plan_effective)

st.caption("© 2025 幸運99（Lucky99）｜完整版（學派 + 抽卡 + 分享圖 + 訂閱狀態）")
