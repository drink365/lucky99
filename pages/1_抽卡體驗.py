
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

import streamlit as st, os, pandas as pd, random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title='抽卡體驗', page_icon='✨', layout='centered')

st.title('✨ 抽卡體驗')
username = st.session_state.get('username') or DEFAULT_USER
school = st.session_state.get('school', '占星')

st.markdown(f'使用者：**{username}**｜偏好學派：**{school}**')

today_key = f'{username}-{datetime.now().date()}-seed'
if 'seed' not in st.session_state or st.session_state.get('seed_key') != today_key:
    import random
    st.session_state.seed = random.randint(0, 10**9)
    st.session_state.seed_key = today_key
rng = random.Random(st.session_state.seed)

selected_system = st.selectbox('選擇卡系', list(CARD_SYSTEMS.keys()), index=0)

def draw_card(system_name, school_name):
    data = CARD_SYSTEMS[system_name]['samples'][school_name]
    return {
        'system': system_name,
        'school': school_name,
        'fortune': data['fortune'],
        'note': data['note'],
        'task': data['task'],
        'color_primary': CARD_SYSTEMS[system_name]['color_primary'],
        'color_secondary': CARD_SYSTEMS[system_name]['color_secondary'],
        'ts': datetime.now().isoformat(timespec='seconds'),
        'user': username
    }

if st.button('🎲 今天抽一張', use_container_width=True):
    result = draw_card(selected_system, school)
    st.session_state.last_card = result

card = st.session_state.get('last_card')
if card:
    st.success(f"你抽到：**{card['system']}卡**（學派：{card['school']}）")
    with st.container(border=True):
        st.markdown(f"**籤語**：{card['fortune']}" )
        st.markdown(f"**小語**：{card['note']}" )
        st.markdown(f"**今日任務**：{card['task']}" )
    import csv
    header = ['ts','user','system','school','fortune','note','task']
    first = not os.path.exists(DRAW_LOG)
    with open(DRAW_LOG, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if first: w.writerow(header)
        w.writerow([card['ts'], card['user'], card['system'], card['school'], card['fortune'], card['note'], card['task']])

    st.markdown('—')
    st.subheader('🖼️ 生成分享圖卡')
    if st.button('生成 PNG 圖卡', use_container_width=True):
        W, H = 1080, 1350
        from PIL import Image, ImageDraw
        bg = Image.new('RGB', (W,H), card['color_primary'])
        draw = ImageDraw.Draw(bg)
        pad = 64
        title = f"AI 幸運卡｜{card['system']}"
        draw.text((pad, pad), title, fill=(30,30,30))

        def write_block(y, label, content):
            draw.text((pad, y), label, fill=(50,50,50))
            y += 48
            import textwrap
            wrapped = textwrap.fill(content, width=18)
            draw.multiline_text((pad, y), wrapped, fill=(20,20,20), spacing=8)
            lines = wrapped.count('\n') + 1
            return y + 32*lines + 24

        y = 160
        y = write_block(y, '籤語', card['fortune'])
        y = write_block(y, '小語', card['note'])
        y = write_block(y, '今日任務', card['task'])
        draw.text((pad, H-100), f"{username} · {datetime.now().date()}", fill=(40,40,40))
        draw.text((W-520, H-100), 'gracefo.com · 永傳家族傳承導師', fill=(40,40,40))

        out_path = os.path.join(DATA_DIR, f"share_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        bg.save(out_path, 'PNG')
        st.image(bg, caption='分享圖預覽', use_container_width=True)
        st.download_button('下載分享圖（PNG）', data=open(out_path, 'rb').read(), file_name=os.path.basename(out_path), mime='image/png', use_container_width=True)
else:
    st.info('點擊上方按鈕，抽出你的今日幸運卡 ✨')
