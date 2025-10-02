import os, csv, hashlib
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="幸運99", page_icon="assets/favicon.png", layout="wide")
st.markdown("""
<style>
  .block-container {max-width: 1280px; padding-top: 1rem; padding-bottom: 2rem;}
  .stButton>button {height: 48px; font-size: 1.05rem;}
  .stSelectbox, .stTextInput, .stDateInput, .stTimeInput {font-size: 1rem;}
</style>
""", unsafe_allow_html=True)

from utils.storage import DRAW_LOG, SIGNIN_LOG, COLS, safe_read_csv, append_row
from utils.share_image import build_share_image
from schools.registry import SCHOOLS
from schools.lifepath import decorate_note

CARD_SYSTEMS = {
    "貴人": {"color_primary":"#F2D9B3","color_secondary":"#FBEDE3","samples":{
        "占星":{"fortune":"星盤顯示貴人正在靠近你。","note":"你不必獨自一人走完全程，宇宙已經在安排相遇。","task":"主動問候一位好久不聯絡的朋友。"},
        "心理":{"fortune":"你內在的守護者原型正準備出場。","note":"允許自己接受幫助，是成熟與勇氣。","task":"今天說出一句『需要幫忙』，並接受它。"},
        "宇宙":{"fortune":"銀光小狐將在你需要時出現。","note":"當你善待自己，貴人就會看見你的光。","task":"寫下感謝清單 3 件事。"},
    }},
    "幸運": {"color_primary":"#C5E7D4","color_secondary":"#FFD5A5","samples":{
        "占星":{"fortune":"今晚的月亮帶來幸運星塵。","note":"做一件平常不會做的小事，宇宙喜愛你的好奇。","task":"換一家咖啡店，點一個新口味。"},
        "心理":{"fortune":"你正在進入心流區。","note":"放鬆不是偷懶，而是讓能量回到你身上。","task":"安排 15 分鐘步行，留意沿途的小美好。"},
        "宇宙":{"fortune":"一顆彩色彗星剛經過。","note":"今天任何小事都可能變成大驚喜。","task":"對遇到的第一位店員說『今天辛苦了』。"},
    }},
    "勇氣": {"color_primary":"#FF9B58","color_secondary":"#FF6B6B","samples":{
        "占星":{"fortune":"火星能量正旺盛。","note":"別再等待完美時機，行動就是最好的時機。","task":"將拖延的一件事，現在做 5 分鐘。"},
        "心理":{"fortune":"你正在從恐懼區走向成長區。","note":"害怕不會消失，但你可以帶著害怕往前走。","task":"寫下你最小可行的下一步，立刻執行。"},
        "宇宙":{"fortune":"宇宙給你一枚勇氣勳章。","note":"今天就是你的主場，舞台燈已經打開。","task":"主動提出一個想法，無論大小。"},
    }},
    "靈感": {"color_primary":"#A3A8F5","color_secondary":"#D8C7F5","samples":{
        "占星":{"fortune":"水瓶座的風帶來新的視角。","note":"換個角度看，你會發現新的路。","task":"把今天的困擾寫成一個問題，問問明天的你。"},
        "心理":{"fortune":"答案其實一直在你心裡。","note":"空白不是空無，而是孕育新意的土壤。","task":"10 分鐘自由書寫，不要修改。"},
        "宇宙":{"fortune":"星雲精靈低語：把不可能當作遊戲來玩。","note":"創造力來自允許自己犯錯。","task":"畫一張完全不在乎好壞的塗鴉。"},
    }},
}

DEFAULT_USER = "訪客"

def user_code(name: str) -> str:
    if not name: return "guest"
    import hashlib
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

st.image("assets/logo.png", width=80)
st.title("🌟 幸運99｜抽卡 × 專業學派 × 情緒療癒")

with st.container(border=True):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        username = st.text_input("你的稱呼", value=st.session_state.get("username",""))
        st.session_state["username"] = username
    with col2:
        st.markdown("**推薦碼**")
        st.code(user_code(username), language="text")
    with col3:
        st.markdown("")

st.markdown("---")

left, right = st.columns([7,5])
with left:
    school_key = st.selectbox(
        "選擇學派",
        options=list(SCHOOLS.keys()),
        format_func=lambda k: SCHOOLS[k]["name"]
    )
with right:
    st.markdown(f"**學派簡介**：{SCHOOLS[school_key]['desc']}")

user_inputs = {}
reqs = SCHOOLS[school_key]["requires"]
c1, c2, c3 = st.columns(3)
if "birth_date" in reqs:
    with c1: user_inputs["birth_date"] = st.date_input("生日")
if "birth_time" in reqs:
    with c2: user_inputs["birth_time"] = st.time_input("出生時間", value=None)
if "birth_place" in reqs:
    with c3: user_inputs["birth_place"] = st.text_input("出生地（城市）")
if "gender" in reqs:
    with c1: user_inputs["gender"] = st.selectbox("性別", ["女","男","其他/不方便透露"])
if "question" in reqs:
    user_inputs["question"] = st.text_input("你的提問（例如：本月適合談合作嗎？）")

st.markdown("---")

st.subheader("🎲 抽卡體驗")
colA, colB = st.columns([7,5])

tone_map = {
    "占星": ["west_astrology"],
    "心理": ["lifepath","bazi","ziwei"],
    "宇宙": ["tarot","iching"]
}
def tone_for_school(key):
    for tone, keys in tone_map.items():
        if key in keys: return tone
    return "心理"

with colA:
    system = st.selectbox("選擇卡系", list(CARD_SYSTEMS.keys()), index=0)
    if st.button("今天抽一張", use_container_width=True):
        tone = tone_for_school(school_key)
        base = CARD_SYSTEMS[system]["samples"][tone]
        card = {
            "system": system,
            "school": SCHOOLS[school_key]["name"],
            "fortune": base["fortune"],
            "note": base["note"],
            "task": base["task"],
            "color_primary": CARD_SYSTEMS[system]["color_primary"],
            "color_secondary": CARD_SYSTEMS[system]["color_secondary"],
            "ts": datetime.now().isoformat(timespec="seconds"),
            "user": username or DEFAULT_USER,
            "school_key": school_key,
            "inputs": user_inputs,
        }
        if school_key == "lifepath" and user_inputs.get("birth_date"):
            card["note"] = decorate_note(card["note"], user_inputs["birth_date"])
        st.session_state["last_card"] = card
        append_row(DRAW_LOG, card, COLS)

card = st.session_state.get("last_card")
with colA:
    if card:
        st.success(f"你抽到：**{card['system']}卡**（學派：{card['school']}）")
        with st.container(border=True):
            st.markdown(f"**籤語**：{card['fortune']}")
            st.markdown(f"**小語**：{card['note']}")
            st.markdown(f"**今日任務**：{card['task']}")
    else:
        st.info("填好上方資料後，點擊按鈕抽出你的今日幸運卡 ✨")

with colB:
    st.markdown("🖼️ **生成分享圖卡**")
    if st.button("生成 PNG 圖卡", use_container_width=True, disabled=not bool(card)):
        out_path, preview = build_share_image(card, os.path.join(os.getcwd(), "data"))
        st.image(preview, caption="分享圖預覽", use_container_width=True)
        with open(out_path, "rb") as fr:
            st.download_button("下載分享圖（PNG）", data=fr.read(),
                               file_name=os.path.basename(out_path), mime="image/png",
                               use_container_width=True)

st.markdown("---")

st.subheader("📚 我的收藏與簽到")
df_cols = ["ts","user","system","school","fortune","note","task","school_key","inputs"]
df = safe_read_csv(DRAW_LOG, df_cols)
df = df[df["user"].fillna(DEFAULT_USER) == (st.session_state.get("username") or DEFAULT_USER)]
df = df.sort_values("ts", ascending=False)

colC, colD = st.columns([7,5])
with colC:
    if df.empty:
        st.info("目前沒有收藏紀錄，先去抽一張吧！")
    else:
        for _, r in df.head(12).iterrows():
            with st.expander(f"🃏 {r['ts']}｜{r['system']}卡（{r['school']}）"):
                st.markdown(f"**籤語**：{r['fortune']}")
                st.markdown(f"**小語**：{r['note']}")
                st.markdown(f"**今日任務**：{r['task']}")

def sign_in(user):
    path = SIGNIN_LOG
    exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if not exists: w.writerow(["date","user"])
        w.writerow([datetime.now().date().isoformat(), user or DEFAULT_USER])

def load_signins(user):
    if not os.path.exists(SIGNIN_LOG) or os.path.getsize(SIGNIN_LOG) == 0:
        return []
    try:
        df = pd.read_csv(SIGNIN_LOG, on_bad_lines="skip", engine="python")
        df = df[df["user"]==(user or DEFAULT_USER)]
        return sorted(df["date"].tolist())
    except Exception:
        try:
            import shutil
            shutil.copy(SIGNIN_LOG, SIGNIN_LOG + ".bak")
        except Exception:
            pass
        return []

def calc_streak(days):
    streak = 0
    cur = datetime.now().date()
    s = set(days)
    while cur.isoformat() in s:
        streak += 1
        cur = cur - timedelta(days=1)
    return streak

with colD:
    today = datetime.now().date().isoformat()
    days = load_signins(st.session_state.get("username"))
    signed = today in days
    if signed:
        st.success(f"今日（{today}）已簽到")
    else:
        if st.button("📍 今日簽到", use_container_width=True):
            sign_in(st.session_state.get("username"))
            st.success("已簽到！重新整理即可看到更新。")
            days = load_signins(st.session_state.get("username"))
    st.info(f"✨ 你的連續簽到天數：**{calc_streak(days)}** 天")
    st.caption("連續 7 天將解鎖『限定主題卡』（未來版本）")

st.markdown("---")

st.subheader("💎 升級方案（即將推出）")
colp, colv = st.columns(2)
with colp:
    st.markdown("""
**Pro（月 NT$99）**
- 無限抽卡、去廣告
- 學派進階解讀（生命靈數＋塔羅 3 張牌）
- 收藏雲端同步
""")
with colv:
    st.markdown("""
**VIP（月 NT$299）**
- 全學派深度解讀（占星/八字/紫微/易經）
- 每月個人運勢報告（PDF）
- 專屬客服與貴人卡特典
""")

st.caption("© 2025 幸運99（Lucky99）｜情緒療癒品牌 MVP")
