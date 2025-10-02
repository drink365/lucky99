import os, csv, hashlib, textwrap, random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ---------------------------
# 基本設定（單頁、無側欄）
# ---------------------------
st.set_page_config(page_title="幸運99", page_icon="assets/favicon.png", layout="centered")

# 資料目錄（相對路徑，雲端安全）
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DRAW_LOG   = os.path.join(DATA_DIR, "draw_log.csv")
SIGNIN_LOG = os.path.join(DATA_DIR, "signin_log.csv")

# 中文字型（避免亂碼）：請把 NotoSansTC-Regular.ttf 放到 assets/
FONT_PATH = "assets/NotoSansTC-Regular.ttf"
def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        # 後備：若未提供中文字型，會仍可顯示英數，但中文可能亂碼
        return ImageFont.load_default()

# -------------------------------------
# 內容資料（學派 × 四大卡系）
# -------------------------------------
CARD_SYSTEMS = {
    "貴人": {
        "color_primary": "#F2D9B3",
        "color_secondary": "#FBEDE3",
        "samples": {
            "占星": {"fortune": "星盤顯示貴人正在靠近你。", "note": "你不必獨自一人走完全程，宇宙已經在安排相遇。", "task": "主動問候一位好久不聯絡的朋友。"},
            "心理": {"fortune": "你內在的守護者原型正準備出場。", "note": "允許自己接受幫助，是成熟與勇氣。", "task": "今天說出一句『需要幫忙』，並接受它。"},
            "宇宙": {"fortune": "銀光小狐將在你需要時出現。", "note": "當你善待自己，貴人就會看見你的光。", "task": "寫下感謝清單 3 件事。"},
        },
    },
    "幸運": {
        "color_primary": "#C5E7D4",
        "color_secondary": "#FFD5A5",
        "samples": {
            "占星": {"fortune": "今晚的月亮帶來幸運星塵。", "note": "做一件平常不會做的小事，宇宙喜愛你的好奇。", "task": "換一家咖啡店，點一個新口味。"},
            "心理": {"fortune": "你正在進入心流區。", "note": "放鬆不是偷懶，而是讓能量回到你身上。", "task": "安排 15 分鐘步行，留意沿途的小美好。"},
            "宇宙": {"fortune": "一顆彩色彗星剛經過。", "note": "今天任何小事都可能變成大驚喜。", "task": "對遇到的第一位店員說『今天辛苦了』。"},
        },
    },
    "勇氣": {
        "color_primary": "#FF9B58",
        "color_secondary": "#FF6B6B",
        "samples": {
            "占星": {"fortune": "火星能量正旺盛。", "note": "別再等待完美時機，行動就是最好的時機。", "task": "將拖延的一件事，現在做 5 分鐘。"},
            "心理": {"fortune": "你正在從恐懼區走向成長區。", "note": "害怕不會消失，但你可以帶著害怕往前走。", "task": "寫下你最小可行的下一步，立刻執行。"},
            "宇宙": {"fortune": "宇宙給你一枚勇氣勳章。", "note": "今天就是你的主場，舞台燈已經打開。", "task": "主動提出一個想法，無論大小。"},
        },
    },
    "靈感": {
        "color_primary": "#A3A8F5",
        "color_secondary": "#D8C7F5",
        "samples": {
            "占星": {"fortune": "水瓶座的風帶來新的視角。", "note": "換個角度看，你會發現新的路。", "task": "把今天的困擾寫成一個問題，問問明天的你。"},
            "心理": {"fortune": "答案其實一直在你心裡。", "note": "空白不是空無，而是孕育新意的土壤。", "task": "10 分鐘自由書寫，不要修改。"},
            "宇宙": {"fortune": "星雲精靈低語：把不可能當作遊戲來玩。", "note": "創造力來自允許自己犯錯。", "task": "畫一張完全不在乎好壞的塗鴉。"},
        },
    },
}
SCHOOLS = ["占星", "心理", "宇宙"]
DEFAULT_USER = "訪客"

# ---------------------------
# 小工具
# ---------------------------
def user_code(name: str) -> str:
    if not name: return "guest"
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

def save_draw(card):
    header = ["ts","user","system","school","fortune","note","task"]
    first = not os.path.exists(DRAW_LOG)
    with open(DRAW_LOG, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if first: w.writerow(header)
        w.writerow([card["ts"], card["user"], card["system"], card["school"], card["fortune"], card["note"], card["task"]])

def load_draws_for(user):
    if not os.path.exists(DRAW_LOG):
        return pd.DataFrame(columns=["ts","user","system","school","fortune","note","task"])
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

# ---------------------------
# 介面：單頁流程
# ---------------------------
st.image("assets/logo.png", width=80)
st.title("🌟 幸運99｜抽卡 × 情緒療癒 × 分享")

# 基本資料（頂部區）
with st.container(border=True):
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        username = st.text_input("你的稱呼", value=st.session_state.get("username", ""))
        st.session_state["username"] = username
    with col2:
        school = st.selectbox("偏好學派", SCHOOLS, index=0, key="school_select")
        st.session_state["school"] = school
    with col3:
        st.markdown("**推薦碼**")
        st.code(user_code(username), language="text")

st.markdown("---")

# 抽卡區
st.subheader("🎲 抽卡體驗")
colA, colB = st.columns([2,1])
with colA:
    system = st.selectbox("選擇卡系", list(CARD_SYSTEMS.keys()), index=0)
    if st.button("今天抽一張", use_container_width=True):
        data = CARD_SYSTEMS[system]["samples"][school]
        card = {
            "system": system,
            "school": school,
            "fortune": data["fortune"],
            "note": data["note"],
            "task": data["task"],
            "color_primary": CARD_SYSTEMS[system]["color_primary"],
            "color_secondary": CARD_SYSTEMS[system]["color_secondary"],
            "ts": datetime.now().isoformat(timespec="seconds"),
            "user": username or DEFAULT_USER,
        }
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
        st.info("點擊上方按鈕抽出你的今日幸運卡 ✨")

# 生成分享圖（中文不亂碼）
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

        # 標題
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

        draw.text((pad, H-96), f"{username or DEFAULT_USER} · {datetime.now().date()}", font=font_meta, fill=(40,40,40))
        draw.text((W-520, H-96), "lucky99.app（示例）", font=font_meta, fill=(40,40,40))

        out_path = os.path.join(DATA_DIR, f"share_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        bg.save(out_path, "PNG")
        st.image(bg, caption="分享圖預覽", use_container_width=True)
        with open(out_path, "rb") as fr:
            st.download_button("下載分享圖（PNG）", data=fr.read(), file_name=os.path.basename(out_path), mime="image/png", use_container_width=True)

st.markdown("---")

# 收藏 & 簽到
st.subheader("📚 我的收藏與簽到")
df = load_draws_for(username)
colC, colD = st.columns([2,1])
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
    days = load_signins(username)
    signed = today in days
    if signed:
        st.success(f"今日（{today}）已簽到")
    else:
        if st.button("📍 今日簽到", use_container_width=True):
            sign_in(username)
            st.success("已簽到！重新整理即可看到更新。")
            days = load_signins(username)
    st.info(f"✨ 你的連續簽到天數：**{calc_streak(days)}** 天")
    st.caption("連續 7 天將解鎖『限定主題卡』（未來版本）")

st.markdown("---")

# 推薦分享
st.subheader("📣 分享與推薦")
code = user_code(username)
share_text = f"""今天抽到我的 幸運99 ✨
感覺被宇宙溫柔地照顧著：）

想一起抽嗎？輸入我的推薦碼 {code} 加入，
我們會共同解鎖一張「友情卡」！"""
st.text_area("一鍵分享文案（可複製貼上）", value=share_text, height=140)

st.caption("© 2025 幸運99（Lucky99）｜情緒療癒品牌 MVP")
