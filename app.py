import os, sys, hashlib
from datetime import datetime, timedelta, date
import pandas as pd
import streamlit as st
import stripe
from utils.storage import DRAW_LOG, SIGNIN_LOG, COLS, safe_read_csv, append_row, get_subscription
from utils.share_image import build_share_image
from utils.reports import make_monthly_report
from schools.registry import SCHOOLS
from schools.lifepath import decorate_note
from schools.tarot import draw_one as tarot_draw_one, draw_three as tarot_draw_three
from schools.west_astrology import sun_sign, tip_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

st.set_page_config(page_title="幸運99", page_icon="assets/favicon.png", layout="wide")
st.markdown("<style>.block-container{max-width:1280px}</style>", unsafe_allow_html=True)

cfg = st.secrets.get("stripe", {})
STRIPE_SECRET = cfg.get("secret_key", "")
PUBLISHABLE = cfg.get("publishable_key", "")
PRICE_PRO = cfg.get("price_pro", "")
PRICE_VIP = cfg.get("price_vip", "")
APP_BASE_URL = cfg.get("app_base_url", "")
if STRIPE_SECRET: stripe.api_key = STRIPE_SECRET

def current_app_url(): return (APP_BASE_URL or "http://localhost:8501").rstrip("/")
def create_checkout_session(username: str, plan: str):
    price = PRICE_PRO if plan=="Pro" else PRICE_VIP
    assert price, "請先在 secrets.toml 設定 price_pro / price_vip"
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price, "quantity": 1}],
        success_url=f"{current_app_url()}?success=1",
        cancel_url=f"{current_app_url()}?canceled=1",
        customer_email=None,
        metadata={"user": username or "訪客", "plan": plan},
    )
    return session.url

# Header
st.image("assets/logo.png", width=80)
st.title("🌟 幸運99｜抽卡 × 專業學派 × 情緒療癒")

# User panel
with st.container(border=True):
    c1,c2,c3 = st.columns([2,2,1])
    with c1:
        username = st.text_input("你的稱呼", value=st.session_state.get("username",""))
        st.session_state["username"] = username
    with c2:
        st.markdown("**推薦碼**")
        code = hashlib.md5((username or "guest").encode("utf-8")).hexdigest()[:8]
        st.code(code, language="text")
    with c3:
        plan_now = get_subscription(username or "訪客")
        st.markdown(f"目前方案：**{plan_now}**")

# Upgrade buttons
colp, colv = st.columns(2)
with colp:
    st.markdown("**Pro（訂閱）**：解鎖 *塔羅三張*")
    if st.button("升級 Pro（Stripe 訂閱）"):
        if not (STRIPE_SECRET and PUBLISHABLE and PRICE_PRO):
            st.error("請設定 secret_key / publishable_key / price_pro")
        else:
            st.link_button("前往 Stripe 訂閱（Pro）", create_checkout_session(username, "Pro"))
with colv:
    st.markdown("**VIP（訂閱）**：含 Pro + *每月 PDF 報告*")
    if st.button("升級 VIP（Stripe 訂閱）"):
        if not (STRIPE_SECRET and PUBLISHABLE and PRICE_VIP):
            st.error("請設定 secret_key / publishable_key / price_vip")
        else:
            st.link_button("前往 Stripe 訂閱（VIP）", create_checkout_session(username, "VIP"))

st.markdown("---")

# School selection
left, right = st.columns([7,5])
with left:
    school_key = st.selectbox("選擇學派", options=list(SCHOOLS.keys()), format_func=lambda k: SCHOOLS[k]["name"])
with right:
    st.markdown(f"**學派簡介**：{SCHOOLS[school_key]['desc']}")

# Inputs
user_inputs = {}
reqs = SCHOOLS[school_key]["requires"]
a,b,c = st.columns(3)
if "birth_date" in reqs:
    with a: user_inputs["birth_date"] = st.date_input("生日", value=None, min_value=date(1900,1,1), max_value=date.today())
if "birth_time" in reqs:
    with b: user_inputs["birth_time"] = st.time_input("出生時間", value=None)
if "birth_place" in reqs:
    with c: user_inputs["birth_place"] = st.text_input("出生地（城市）")
if "gender" in reqs:
    with a: user_inputs["gender"] = st.selectbox("性別", ["女","男","其他/不方便透露"])
if "question" in reqs:
    user_inputs["question"] = st.text_input("你的提問（例如：本月適合談合作嗎？）")

st.markdown("---")

# Draw section
CARD_SYSTEMS = {
    "貴人":{"color_primary":"#F2D9B3","color_secondary":"#FBEDE3","samples":{"占星":{"fortune":"星盤顯示貴人正在靠近你。","note":"你不必獨自一人走完全程，宇宙已經在安排相遇。","task":"主動問候一位好久不聯絡的朋友。"},"心理":{"fortune":"你內在的守護者原型正準備出場。","note":"允許自己接受幫助，是成熟與勇氣。","task":"今天說出一句『需要幫忙』，並接受它。"},"宇宙":{"fortune":"銀光小狐將在你需要時出現。","note":"當你善待自己，貴人就會看見你的光。","task":"寫下感謝清單 3 件事。"}}},
    "幸運":{"color_primary":"#C5E7D4","color_secondary":"#FFD5A5","samples":{"占星":{"fortune":"今晚的月亮帶來幸運星塵。","note":"做一件平常不會做的小事，宇宙喜愛你的好奇。","task":"換一家咖啡店，點一個新口味。"},"心理":{"fortune":"你正在進入心流區。","note":"放鬆不是偷懶，而是讓能量回到你身上。","task":"安排 15 分鐘步行，留意沿途的小美好。"},"宇宙":{"fortune":"一顆彩色彗星剛經過。","note":"今天任何小事都可能變成大驚喜。","task":"對遇到的第一位店員說『今天辛苦了』。"}}},
    "勇氣":{"color_primary":"#FF9B58","color_secondary":"#FF6B6B","samples":{"占星":{"fortune":"火星能量正旺盛。","note":"別再等待完美時機，行動就是最好的時機。","task":"將拖延的一件事，現在做 5 分鐘。"},"心理":{"fortune":"你正在從恐懼區走向成長區。","note":"害怕不會消失，但你可以帶著害怕往前走。","task":"寫下你最小可行的下一步，立刻執行。"},"宇宙":{"fortune":"宇宙給你一枚勇氣勳章。","note":"今天就是你的主場，舞台燈已經打開。","task":"主動提出一個想法，無論大小。"}}},
    "靈感":{"color_primary":"#A3A8F5","color_secondary":"#D8C7F5","samples":{"占星":{"fortune":"水瓶座的風帶來新的視角。","note":"換個角度看，你會發現新的路。","task":"把今天的困擾寫成一個問題，問問明天的你。"},"心理":{"fortune":"答案其實一直在你心裡。","note":"空白不是空無，而是孕育新意的土壤。","task":"10 分鐘自由書寫，不要修改。"},"宇宙":{"fortune":"星雲精靈低語：把不可能當作遊戲來玩。","note":"創造力來自允許自己犯錯。","task":"畫一張完全不在乎好壞的塗鴉。"}}},
}

st.subheader("🎲 抽卡體驗")
cA,cB = st.columns([7,5])
tone_map = {"占星":["west_astrology"], "心理":["lifepath"], "宇宙":["tarot"]}
def tone_for_school(key):
    for tone, keys in tone_map.items():
        if key in keys: return tone
    return "心理"
with cA:
    system = st.selectbox("選擇卡系", list(CARD_SYSTEMS.keys()), index=0)
    tarot_mode = "單張"
    if school_key == "tarot":
        tarot_mode = st.radio("塔羅模式", ["單張（Free）","三張（Pro）"], horizontal=True)
    if st.button("今天抽一張", use_container_width=True):
        tone = tone_for_school(school_key)
        base = CARD_SYSTEMS[system]["samples"][tone]
        card = {"system":system,"school":SCHOOLS[school_key]["name"],"fortune":base["fortune"],"note":base["note"],"task":base["task"],
                "color_primary":CARD_SYSTEMS[system]["color_primary"],"color_secondary":CARD_SYSTEMS[system]["color_secondary"],
                "ts":datetime.now().isoformat(timespec="seconds"),"user":st.session_state.get("username") or "訪客","school_key":school_key,"inputs":user_inputs}
        if school_key=="tarot":
            seed = f"{st.session_state.get('username')}-{datetime.now().date()}-{system}"
            plan_now = get_subscription(st.session_state.get("username") or "訪客")
            if "三張" in tarot_mode and plan_now not in ("Pro","VIP"):
                card["fortune"]="（Pro 付費功能）"; card["note"]="升級後可解鎖『過去-現在-未來』三張牌。"; card["task"]="先用單張模式體驗看看。"
            elif "三張" in tarot_mode:
                tri = tarot_draw_three(seed=seed)
                lines = [f"{t['slot']}：《{t['name']}·{t['pose']}》{t['meaning']}" for t in tri]
                q = user_inputs.get("question") or "今天的提醒"
                card["fortune"]=" / ".join(lines); card["note"]=f"針對「{q}」，三張牌已提供路徑。｜{card['note']}"; card["task"]="把三件可行的小步驟寫下，先完成第一步。"
            else:
                one = tarot_draw_one(seed=seed)
                q = user_inputs.get("question") or "今天的提醒"
                card["fortune"]=f"塔羅《{one['name']}·{one['pose']}》：{one['meaning']}"; card["note"]=f"針對「{q}」，掌握牌義行動的第一步。｜{card['note']}"; card["task"]="把你可行的一步寫下，今天就做。"
        if school_key=="west_astrology" and user_inputs.get("birth_date"):
            sign = sun_sign(user_inputs["birth_date"]); tip = tip_for(sign); card["note"]=f"[{sign}] {tip}｜{card['note']}"
        if school_key=="lifepath" and user_inputs.get("birth_date"):
            card["note"]=decorate_note(card["note"], user_inputs["birth_date"])
        st.session_state["last_card"]=card; append_row(DRAW_LOG, card, COLS)

card = st.session_state.get("last_card")
with cA:
    if card:
        st.success(f"你抽到：**{card['system']}卡**（學派：{card['school']}）")
        with st.container(border=True):
            st.markdown(f"**籤語**：{card['fortune']}"); st.markdown(f"**小語**：{card['note']}"); st.markdown(f"**今日任務**：{card['task']}")
    else:
        st.info("填好上方資料後，點擊按鈕抽出你的今日幸運卡 ✨")
with cB:
    st.markdown("🖼️ **生成分享圖卡**")
    if st.button("生成 PNG 圖卡", use_container_width=True, disabled=not bool(card)):
        out_path, preview = build_share_image(card, os.path.join(os.getcwd(), "data"))
        st.image(preview, caption="分享圖預覽", use_container_width=True)
        with open(out_path, "rb") as fr:
            st.download_button("下載分享圖（PNG）", data=fr.read(), file_name=os.path.basename(out_path), mime="image/png", use_container_width=True)

# VIP PDF
plan_now = get_subscription(st.session_state.get("username") or "訪客")
if plan_now=="VIP":
    st.markdown("**🎁 VIP 專屬：每月運勢報告（PDF）**")
    if st.button("產生本月 PDF 報告"):
        content = "本月關鍵字：專注、節奏、信任\n\n建議：\n1. 確認你的首要目標\n2. 設定每週固定檢視\n3. 建立可被信任的節奏"
        path = make_monthly_report(st.session_state.get("username"), content, os.path.join(os.getcwd(), "data"))
        with open(path, "rb") as fr:
            st.download_button("下載 PDF 報告", data=fr.read(), file_name=os.path.basename(path), mime="application/pdf")

st.caption("© 2025 幸運99（Lucky99）｜Stripe 訂閱 + Webhook 版")
