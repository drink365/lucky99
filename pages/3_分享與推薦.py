
CARD_SYSTEMS = {
    "貴人": {
        "color_primary": "#F2D9B3",
        "color_secondary": "#FBEDE3",
        "samples": {
            "占星": {
                "fortune": "星盤顯示貴人正在靠近你。",
                "note": "你不必獨自一人走完全程，宇宙已經在安排相遇。",
                "task": "主動問候一位好久不聯絡的朋友。"
            },
            "心理": {
                "fortune": "你內在的守護者原型正準備出場。",
                "note": "允許自己接受幫助，是成熟與勇氣。",
                "task": "今天說出一句『需要幫忙』，並接受它。"
            },
            "宇宙": {
                "fortune": "銀光小狐將在你需要時出現。",
                "note": "當你善待自己，貴人就會看見你的光。",
                "task": "寫下感謝清單 3 件事。"
            }
        }
    },
    "幸運": {
        "color_primary": "#C5E7D4",
        "color_secondary": "#FFD5A5",
        "samples": {
            "占星": {
                "fortune": "今晚的月亮帶來幸運星塵。",
                "note": "做一件平常不會做的小事，宇宙喜愛你的好奇。",
                "task": "換一家咖啡店，點一個新口味。"
            },
            "心理": {
                "fortune": "你正在進入心流區。",
                "note": "放鬆不是偷懶，而是讓能量回到你身上。",
                "task": "安排 15 分鐘步行，留意沿途的小美好。"
            },
            "宇宙": {
                "fortune": "一顆彩色彗星剛經過。",
                "note": "今天任何小事都可能變成大驚喜。",
                "task": "對遇到的第一位店員說『今天辛苦了』。"
            }
        }
    },
    "勇氣": {
        "color_primary": "#FF9B58",
        "color_secondary": "#FF6B6B",
        "samples": {
            "占星": {
                "fortune": "火星能量正旺盛。",
                "note": "別再等待完美時機，行動就是最好的時機。",
                "task": "將拖延的一件事，現在做 5 分鐘。"
            },
            "心理": {
                "fortune": "你正在從恐懼區走向成長區。",
                "note": "害怕不會消失，但你可以帶著害怕往前走。",
                "task": "寫下你最小可行的下一步，立刻執行。"
            },
            "宇宙": {
                "fortune": "宇宙給你一枚勇氣勳章。",
                "note": "今天就是你的主場，舞台燈已經打開。",
                "task": "主動提出一個想法，無論大小。"
            }
        }
    },
    "靈感": {
        "color_primary": "#A3A8F5",
        "color_secondary": "#D8C7F5",
        "samples": {
            "占星": {
                "fortune": "水瓶座的風帶來新的視角。",
                "note": "換個角度看，你會發現新的路。",
                "task": "把今天的困擾寫成一個問題，問問明天的你。"
            },
            "心理": {
                "fortune": "答案其實一直在你心裡。",
                "note": "空白不是空無，而是孕育新意的土壤。",
                "task": "10 分鐘自由書寫，不要修改。"
            },
            "宇宙": {
                "fortune": "星雲精靈低語：把不可能當作遊戲來玩。",
                "note": "創造力來自允許自己犯錯。",
                "task": "畫一張完全不在乎好壞的塗鴉。"
            }
        }
    }
}
SCHOOLS = ["占星", "心理", "宇宙"]
DEFAULT_USER = "訪客"
import os
DATA_DIR = os.path.join(os.getcwd(), "data") if os.path.exists(os.path.join(os.getcwd(), "data")) else "/mnt/data"
DRAW_LOG = os.path.join(DATA_DIR, "draw_log.csv")
SIGNIN_LOG = os.path.join(DATA_DIR, "signin_log.csv")
os.makedirs(DATA_DIR, exist_ok=True)

import streamlit as st, hashlib

st.set_page_config(page_title='分享與推薦', page_icon='📣', layout='centered')
st.title('📣 分享與推薦')

username = st.session_state.get('username') or DEFAULT_USER

def user_code(name: str):
    if not name:
        return 'guest'
    import hashlib
    return hashlib.md5(name.encode('utf-8')).hexdigest()[:8]

code = user_code(username)

st.subheader('你的推薦碼')
st.code(code, language='text')

st.markdown('當朋友輸入你的推薦碼註冊（未來版本），你們將共同解鎖 **友情卡** 🎁')

st.markdown('---')
st.subheader('一鍵分享文案（可複製貼上 IG / LINE）')

share_text = f"""
今天抽到我的 AI 幸運卡 ✨
感覺被宇宙溫柔地照顧著：）

想一起抽嗎？輸入我的推薦碼 {code} 加入，
我們會共同解鎖一張「友情卡」！
"""
st.text_area('分享文案', value=share_text, height=180)
st.caption('提示：可搭配「抽卡體驗」頁面生成的分享圖卡一起貼出，更吸睛。')

st.markdown('---')
st.subheader('品牌聯名（示例構想）')
st.write('- 抽到「貴人卡」 → 咖啡 9 折券')
st.write('- 抽到「幸運卡」 → 書店單本 95 折')
st.write('（此區為示例，實際合作可於後台設定贊助卡）')
