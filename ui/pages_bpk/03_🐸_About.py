import streamlit as st
from config import DEV, get_page_config, init_session

# 设置页面配置并初始化会话
st.set_page_config(**get_page_config())
init_session(st.session_state)
# 如果在开发模式下，则渲染会话状态
if DEV:
    with st.expander("Session state"):
        st.write(st.session_state)

st.write("## 🐸 &nbsp; `嗨，我是Froggo！`")
st.write("---")

st.write(
    """
#### `我在这里帮助您轻松浏览、搜索和导航您的音视频内容。`

#### `我还在不断成长中 - 还是一只蝌蚪，但我正在迅速长大！`
"""
)

st.write("---")

