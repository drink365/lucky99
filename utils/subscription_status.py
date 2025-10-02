from datetime import datetime
import streamlit as st
def show_user_status():
    username = st.session_state.get("username") or "訪客"
    plan = st.session_state.get("plan") or "Free"
    expiry = st.session_state.get("expiry_date")
    if isinstance(expiry, (int, float)):
        expiry = datetime.fromtimestamp(expiry).strftime("%Y-%m-%d")
    elif isinstance(expiry, datetime):
        expiry = expiry.strftime("%Y-%m-%d")
    else:
        expiry = expiry or "—"
    st.markdown(
        f"""
        <div style="position: sticky; top: 0; z-index: 1000;">
          <div style="text-align:right; font-size:14px; color:#333;">
            😊 {username} ｜ <b>{plan}</b> ｜ 有效期限：{expiry}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
