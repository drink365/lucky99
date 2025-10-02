
import streamlit as st
import hashlib
from PIL import Image

st.set_page_config(page_title='AI 幸運卡平台', page_icon='assets/favicon.png', layout='wide')

if 'username' not in st.session_state:
    st.session_state.username = ''
if 'school' not in st.session_state:
    st.session_state.school = '占星'

logo = Image.open('assets/logo.png')
st.sidebar.image(logo, use_container_width=True)
st.sidebar.markdown('### 登入 / 基本設定')
st.session_state.username = st.sidebar.text_input('你的稱呼（用於收藏與推薦碼）', value=st.session_state.username or '')
st.session_state.school = st.sidebar.selectbox('偏好學派', ['占星', '心理', '宇宙'], index=0)

def user_code(name: str):
    if not name:
        return 'guest'
    return hashlib.md5(name.encode('utf-8')).hexdigest()[:8]

code = user_code(st.session_state.username)
st.sidebar.markdown(f'**你的推薦碼**：`{code}`')

st.title('🌟 AI 幸運卡平台｜品牌核心宣言')

st.markdown(
    """
在這個快到令人窒息的 AI 時代，
我們把「抽卡」升級為 **日常療癒的儀式**。

- 不是算命，而是 **安心 × 陪伴 × 幸福感**
- 每日一抽：一句籤語 · 一段溫暖小語 · 一個小任務
- 三大學派切換：占星 / 心理 / 宇宙
- 建立收藏圖鑑、生成分享圖卡、還能推薦朋友一起來玩

> 讓你每天都能笑一笑、安心一點、前進一小步。
"""
)

st.markdown('---')
st.subheader('🚀 快速開始')
col1, col2, col3 = st.columns(3)
with col1:
    st.page_link('pages/1_抽卡體驗.py', label='抽卡體驗', icon='✨')
with col2:
    st.page_link('pages/2_我的收藏與簽到.py', label='我的收藏與簽到', icon='📚')
with col3:
    st.page_link('pages/3_分享與推薦.py', label='分享與推薦', icon='📣')

st.markdown('---')
st.caption('© 2025 永傳家族傳承導師｜AI 幸運卡平台（MVP）')
