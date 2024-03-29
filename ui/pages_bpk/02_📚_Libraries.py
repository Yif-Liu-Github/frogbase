import shutil
from pathlib import Path

import streamlit as st
from config import DATADIR, DEV, get_page_config, init_session
from tinydb import Query, TinyDB

# 设置页面配置并初始化会话
st.set_page_config(**get_page_config())
init_session(st.session_state)

# 如果在开发模式下，则渲染会话状态
if DEV:
    with st.sidebar.expander("Session state"):
        st.write(st.session_state)

st.write("## 📚 &nbsp; 库")
st.write("---")

# 创建和选择库的部件
# -----------------------------------
# 创建一个表单来添加新的库
with st.sidebar.form("create_library"):
    new_library = st.text_input("创建新的库", help="输入新的库名称")
    add_library = st.form_submit_button(label="➕ 创建")
    success_container = st.empty()

# 如果表单被提交，则创建一个新的库
if add_library:
    if new_library:
        # 更新会话状态
        init_session(st.session_state, library=new_library, reset=True)
        st.experimental_rerun()
    else:
        success_container.error("请输入库名称")

existing_libraries = [p.name for p in Path(DATADIR).iterdir() if p.is_dir()]
selected_library = st.sidebar.selectbox(
    "📚 选择库", options=existing_libraries, index=existing_libraries.index(st.session_state.library)
)
if selected_library != st.session_state.library:
    # 更新会话状态
    init_session(st.session_state, library=selected_library, reset=True)
    st.experimental_rerun()


# 找到datadir中所有的tinydb.json文件，并将其显示为库
dbs = list(Path(DATADIR).glob("**/tinydb*.json"))
if len(dbs) == 1:
    st.info("🐸 &nbsp; 删除唯一剩下的库将重置应用并重新创建默认库")

# 按创建日期排序dbs
dbs = sorted(dbs, key=lambda x: x.stat().st_ctime, reverse=True)
for dbpath in dbs:
    libname = dbpath.parent.name
    db = TinyDB(dbpath)
    # 渲染库名称和选定状态
    st.write(f"#### `{libname}`")

    st.markdown(
        f"""
    <b>路径: `{dbpath.parent}`</b><br>
    <b>媒体: `{len(db.table('Media'))}`</b>; &nbsp;
    <b>字幕: `{len(db.table('Captions'))}`</b>
    """,
        unsafe_allow_html=True,
    )

    # 按钮来选择库。如果已经选择，则呈现为禁用状态
    if libname == st.session_state.library:
        st.button("📌 &nbsp; 已选定", disabled=True)
    else:
        # 按钮来选择库
        if st.button("📌 &nbsp; 选择", key=libname + "select"):
            init_session(st.session_state, library=libname, reset=True)
            st.experimental_rerun()

    # 按钮来删除库
    if st.button("🗑️ &nbsp; 删除", key=libname + "delete"):
        shutil.rmtree(dbpath.parent)
        init_session(st.session_state, reset=True)
        st.experimental_rerun()

    st.write("---")
