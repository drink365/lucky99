import os, csv, hashlib, textwrap, random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ---------------------------
# 版面設定（寬版）
# ---------------------------
st.set_page_config(page_title="幸運99", page_icon="assets/favicon.png", layout="wide")
st.markdown("""
<style>
  .block-container {max-width: 1280px; padding-top: 1rem; padding-bottom: 2rem;}
  .stButton>button {height: 48px; font-size: 1.05rem;}
  .stSelectbox, .stTextInput, .stDateInput, .stTimeInput {font-size: 1rem;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 資料目錄（相對路徑，雲端安全）
# ---------------------------
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DRAW_LOG   = os.path.join(DATA_DIR, "draw_log.csv")
SIGNIN_LOG = os.path.join(DATA_DIR, "signin_log.csv")

# ---------------------------
# 中文字型（避免亂碼）
# ---------------------------
FONT_PATH = "assets/NotoSansTC-Regular.ttf"
def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

# ---------------------------
# 四大卡系（品牌體驗）
# ---------------------------
CARD_SYSTEMS = {
    "貴人": {
        "color_primary": "#F2D9B3",
        "color_secondary": "#FBEDE3",
        "samples": {
            "占星": {"fortune":"星盤顯示貴人正在靠近你。","note":"你不必獨自一人走完全程，宇宙已經在安排相遇。","task":"主動問候一位好久不聯絡的朋友。"},
            "心理": {"fortune":"你內在的守護者原型正準備出場。","note":"允許自己接受幫助，是成熟與勇氣。","task":"今天說出一句『需要幫忙』，並接受它。"},
            "宇宙": {"fortune":"銀光小狐將在你需要時出現。","note":"當你善待自己，貴人就會看見你的光。","task":"寫下感謝清單 3 件事。"},
        },
    },
    "幸運": {
        "color_primary": "#C5E7D4",
        "color_secondary": "#FFD5A5",
        "samples": {
            "占星": {"fortune":"今晚的月亮帶來幸運星塵。","note":"做一件平常不會做的小事，宇宙喜愛你的好奇。","task":"換一家咖啡店，點一個新口味。"},
            "心理": {"fortune":"你正在進入心流區。","note":"放鬆不是偷懶，而是讓能量回到你身上。","task":"安排 15 分鐘步行，留意沿途的小美好。"},
            "宇宙": {"fortune":"一顆彩色彗星剛經過。","note":"今天任何小事都可能變成大驚喜。","task":"對遇到的第一位店員說『今天辛苦了』。"},
        },
    },
    "勇氣": {
        "color_primary": "#FF9B58",
        "color_secondary": "#FF6B6B",
        "samples": {
            "占星": {"fortune":"火星能量正旺盛。","note":"別再等待完美時機，行動就是最好的時機。","task":"將拖延的一件事，現在做 5 分鐘。"},
            "心理": {"fortune":"你正在從恐懼區走向成長區。","note":"害怕不會消失，但你可以帶著害怕往前走。","task":"寫下你最小可行的下一步，立刻執行。"},
            "宇宙": {"fortune":"宇宙給你一枚勇氣勳章。","note":"今天就是你的主場，舞台燈已經打開。","task":"主動提出一個想法，無論大小。"},
        },
    },
    "靈感": {
        "color_primary": "#A3A8F5",
        "color_secondary": "#D8C7F5",
        "samples": {
            "占星": {"fortune":"水瓶座的風帶來新的視角。","note":"換個角度看，你會發現新的路。","task":"把今天的困擾寫成一個問題，問問明天的你。"},
            "心理": {"fortune":"答案其實一直在你心裡。","note":"空白不是空無，而是孕育新意的土壤。","task":"10 分鐘自由書寫，不要修改。"},
            "宇宙": {"fortune":"星雲精靈低語：把不可能當作遊戲來玩。","note":"創造力來自允許自己犯錯。","task":"畫一張完全不在乎好壞的塗鴉。"},
        },
    },
}

# ---------------------------
# 專業學派（可收費）
# ---------------------------
SCHOOLS = {
    "west_astrology": {
        "name": "西洋占星（本命盤）",
        "desc": "以行星落宮與相位解讀你的天賦與課題。",
        "requires": ["birth_date", "birth_time", "birth_place"]
    },
    "tarot": {
        "name": "塔羅（78 張）",
        "desc": "針對具體問題給出象徵與建議，適合短期抉擇。",
        "requires": ["question"]
    },
    "ziwei": {
        "name": "紫微斗數",
        "desc": "以命宮三方四正綜觀人生格局與流年趨勢。",
        "requires": ["birth_date", "birth_time", "gender"]
    },
    "bazi": {
        "name": "四柱八字（子平）",
        "desc": "以日主強弱、十神喜忌判斷運勢與用神方向。",
        "requires": ["birth_date", "birth_time"]
    },
    "iching": {
        "name": "易經卜卦",
        "desc": "以起卦時刻或擲銅錢得卦，解讀當下變化。",
        "requires": ["question"]
    },
    "lifepath": {
        "name": "生命靈數",
        "desc": "由生日推導生命靈數 1–9，對應性格與任務（MVP 已內建）。",
        "requires": ["birth_date"]
    },
    "meihua": {
        "name": "梅花易數（簡化）",
        "desc": "以時間與象數快速占時運，輕量易入門。",
        "requires": []
    }
}

DEFAULT_USER = "訪客"

# ---------------------------
# 小工具
# ---------------------------
def user_code(name: str) -> str:
    if not name: return "guest"
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

def save_draw(card):
    header = ["ts","user","system","school","fortune","note","task","school_key","inputs"]
    first = not os.path.exists(DRAW_LOG)
    with open(DRAW_LOG, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if first: w.writerow(header)
        w.writerow([card["ts"], card["user"], card["system"], card["school"],
                    card["fortune"], card["note"], card["task"],
                    card["school_key"], str(card.get("inputs", {}))])

def load_draws_for(user):
    cols = ["ts","user","system","school","fortune","note","task","school_key","inputs"]
    if not os.path.exists(DRAW_LOG):
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(DRAW_LOG)
    df = df[df["user"].fillna(DEFAULT_USER) == (user or DEFAULT_USER)]
    return df.sort_values("ts", ascending=False)

def sign_in(user):
    first = not os.path.exists(SIGNIN_LOG)
    with open(SIGNIN_LOG, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if first: w.writerow(["date","user"])
        w.writerow([datetime.now().date().isoformat(), user or DEFAULT_USER])

def load_signins(user):
    if not os.path.exists(SIGNIN_LOG):
        return []
    df = pd.read_csv(SIGNIN_LOG)
    return sorted(df[df["user"]==(user or DEFAULT_USER)]["date"].tolist())

def calc_streak(days):
    streak = 0
    cur = datetime.now().date()
    s = set(days)
    while cur.isoformat() in s:
        streak += 1
        cur = cur - timedelta(days=1)
    return streak

# 生命靈數
def calc_life_path(date_obj):
    if not date_obj: return None
    s = "".join([c for c in date_obj.strftime("%Y%m%d") if c.isdigit()])
    n = sum(int(c) for c in s)
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n

LIFE_MEANINGS = {
    1:"領導與開創。今日適合主動提案、做決策。",
    2:"協作與傾聽。適合溝通協調、拉近關係。",
    3:"表達與創意。適合寫作發言、內容創作。",
    4:"制度與穩定。適合收斂心神、完成待辦。",
    5:"變化與冒險。適合嘗試新方法或新路線。",
    6:"責任與關懷。適合關心家人夥伴、經營信任。",
    7:"洞察與學習。適合閱讀研究、安靜思考。",
    8:"目標與成果。適合衝刺 KPI、談判資源。",
    9:"願景與助人。適合公益、分享、回饋社群。",
}

# ---------------------------
# 單頁介面
# ---------------------------
st.image("assets/logo.png", width=80)
st.title("🌟 幸運99｜抽卡 × 專業學派 × 情緒療癒")

# 頂部：使用者資料
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

# 學派選擇 + 動態欄位
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

# 抽卡 + 產圖
st.subheader("🎲 抽卡體驗")
colA, colB = st.columns([7,5])

with colA:
    system = st.selectbox("選擇卡系", list(CARD_SYSTEMS.keys()), index=0)
    if st.button("今天抽一張", use_container_width=True):
        # 用學派對應語氣
        tone = "占星" if school_key in ("west_astrology",) else ("心理" if school_key in ("lifepath","bazi","ziwei") else "宇宙")
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
            "inputs": user_inputs
        }

        # 生命靈數定製
        if school_key == "lifepath" and user_inputs.get("birth_date"):
            lp = calc_life_path(user_inputs["birth_date"])
            if lp:
                extra = LIFE_MEANINGS.get(lp,"")
                card["note"] = f"[生命靈數 {lp}] {extra}｜{card['note']}"

        st.session_state["last_card"] = card
        save_draw(card)

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
        W, H = 1080, 1350
        bg = Image.new("RGB", (W, H), card["color_primary"])
        draw = ImageDraw.Draw(bg)
        pad = 64

        font_title = load_font(64)
        font_label = load_font(42)
        font_body  = load_font(40)
        font_meta  = load_font(32)

        draw.text((pad, pad), f"幸運99｜{card['system']}", font=font_title, fill=(30,30,30))

        def write_block(y, label, content):
            draw.text((pad, y), label, font=font_label, fill=(50,50,50))
            y += 56
            wrapped = textwrap.fill(content, width=18)
            draw.multiline_text((pad, y), wrapped, font=font_body, fill=(20,20,20), spacing=8)
            lines = wrapped.count("\n") + 1
            return y + 42*lines + 28

        y = 180
        y = write_block(y, "籤語", card["fortune"])
        y = write_block(y, "小語", card["note"])
        y = write_block(y, "今日任務", card["task"])

        draw.text((pad, H-96), f"{card['user']} · {datetime.now().date()}", font=font_meta, fill=(40,40,40))
        draw.text((W-520, H-96), "lucky99.app（示例）", font=font_meta, fill=(40,40,40))

        out_path = os.path.join(DATA_DIR, f"share_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        bg.save(out_path, "PNG")
        st.image(bg, caption="分享圖預覽", use_container_width=True)
        with open(out_path, "rb") as fr:
            st.download_button("下載分享圖（PNG）", data=fr.read(),
                               file_name=os.path.basename(out_path), mime="image/png",
                               use_container_width=True)

st.markdown("---")

# 收藏 & 簽到
st.subheader("📚 我的收藏與簽到")
df = load_draws_for(st.session_state.get("username"))
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

# 收費方案（先占位，後續串金流）
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
