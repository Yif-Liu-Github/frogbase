import re
from datetime import datetime
from pathlib import Path

import openai
import streamlit as st
from config import DATADIR, DEV, OPENAI_KEY, TEMP_DIR, get_page_config, init_session
from tinydb import Query
from utils import get_formatted_media_info
from tinydb import Query, TinyDB
import shutil

# 设置页面配置并初始化会话
st.set_page_config(**get_page_config())
init_session(st.session_state)

# 如果在开发模式下，则渲染会话状态
if DEV:
    with st.sidebar.expander("会话状态"):
        st.write(st.session_state)

if DEV:
    openai.api_key = OPENAI_KEY

# 别名以便阅读
# --------------------------------
fb = st.session_state.fb


# 列表视图
# --------------------------------
if st.session_state.listview:  # noqa: C901
    # 重置详细视图的会话状态

    # 找到datadir中所有的tinydb.json文件，并将其显示为库
    dbs = list(Path(DATADIR).glob("**/tinydb*.json"))
    if len(dbs) == 1:
        st.info("🐸 &nbsp; 删除唯一剩下的库将重置应用并重新创建默认库")

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

    with st.sidebar.form("select_library"):
        selected_library = st.selectbox(
            "📚 选择库", options=existing_libraries, index=existing_libraries.index(st.session_state.library)
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            sel_library = st.form_submit_button(label="📌 &nbsp; 选择")
        with col2:
            del_library = st.form_submit_button(label="🗑️ &nbsp; 删除")
        success_container = st.empty()
    # 按钮来删除库
    if del_library:
        for dbpath in dbs:
            if selected_library == dbpath.parent.name:
                shutil.rmtree(dbpath.parent)
                init_session(st.session_state, reset=True)
                st.experimental_rerun()
    if sel_library:
        if selected_library != st.session_state.library:
            # 更新会话状态
            init_session(st.session_state, library=selected_library, reset=True)
            st.experimental_rerun()

    # 添加媒体部件
    # --------------------------------
    with st.sidebar.expander("➕ &nbsp; 添加媒体", expanded=False):
        # 在侧边栏和表单中呈现媒体类型选择
        source_type = st.radio("媒体来源", ["网页", "上传"], label_visibility="collapsed")
        with st.form("input_form"):
            # 添加 web_url 和 input_files 的默认值，以避免 pylance 警告
            web_url = None
            input_files = None
            if source_type == "网页":
                web_url = st.text_area("网址（每行一个）", help="每行输入一个URL")
                audio_only = st.checkbox("仅音频", value=True)

                st.caption(
                    """
                    支持: bilibili、YouTube等[(查看列表)](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
                """
                )
            elif source_type == "Upload":
                input_files = st.file_uploader(
                    "添加一个或多个文件",
                    type=["mp4", "avi", "mov", "mkv", "mp3", "wav"],
                    accept_multiple_files=True,
                )

            lang_options = [
                "en",
                "zh",
                "de",
                "es",
                "ru",
                "ko",
                "fr",
                "ja",
                "pt",
                "tr",
                "pl",
                "ca",
                "nl",
                "ar",
                "sv",
                "it",
                "id",
                "hi",
                "fi",
                "vi",
                "he",
                "uk",
                "el",
                "ms",
                "cs",
                "ro",
                "da",
                "hu",
                "ta",
                "no",
                "th",
                "ur",
                "hr",
                "bg",
                "lt",
                "la",
                "mi",
                "ml",
                "cy",
                "sk",
                "te",
                "fa",
                "lv",
                "bn",
                "sr",
                "az",
                "sl",
                "kn",
                "et",
                "mk",
                "br",
                "eu",
                "is",
                "hy",
                "ne",
                "mn",
                "bs",
                "kk",
                "sq",
                "sw",
                "gl",
                "mr",
                "pa",
                "si",
                "km",
                "sn",
                "yo",
                "so",
                "af",
                "oc",
                "ka",
                "be",
                "tg",
                "sd",
                "gu",
                "am",
                "yi",
                "lo",
                "uz",
                "fo",
                "ht",
                "ps",
                "tk",
                "nn",
                "mt",
                "sa",
                "lb",
                "my",
                "bo",
                "tl",
                "mg",
                "as",
                "tt",
                "haw",
                "ln",
                "ha",
                "ba",
                "jw",
                "su",
            ]
            fb.models.whisper.language = st.selectbox("选择语种", options=lang_options,
                                                      index=lang_options.index(fb.models.whisper.language))
            add_media = st.form_submit_button(label="添加媒体！")

        if add_media:
            if source_type == "网页":
                if web_url:
                    sources = [url.strip() for url in web_url.split("\n")]
                    opts = {"audio_only": audio_only}
                    st.success("正在下载和处理媒体。")
                else:
                    st.error("请输入 URL")
            elif source_type == "Upload":
                if input_files:
                    # Streamlit 文件上传器返回一个 BytesIO 对象的列表
                    # frogbase 目前还不支持这种格式。现在，
                    # 字节将首先保存到临时目录，然后作为文件路径列表传递给 frogbase。
                    sources = []
                    # 将文件从临时目录移动到 libdir
                    opts = {"move": True}

                    for input_file in input_files:
                        # 目标路径
                        dest_path = TEMP_DIR / input_file.name
                        # 将文件保存到目标路径
                        with open(dest_path, "wb") as f:
                            f.write(input_file.getvalue())
                        # 添加到 sources 列表
                        sources.append(str(dest_path.resolve()))
                else:
                    st.error("请上传文件")
            # elif source_type == "Record":
            #     pass

            if sources:
                fb.add(sources, **opts)
                st.success("正在下载和处理媒体。")

            # 将列表模式设置为 true
            st.session_state.listview = True
            st.experimental_rerun()

    # 筛选部件
    # --------------------------------
    with st.sidebar.expander("🚫 &nbsp; 筛选器", expanded=False):
        # 注意: 目前支持使用 tinydb 查询语法的复合筛选器
        # https://tinydb.readthedocs.io/en/latest/usage.html#queries
        # 这里的 UI 暗示筛选器之间的 'AND' 操作
        filters = None
        Media = Query()

        # 添加日期范围筛选器
        date_range = st.date_input("日期范围", value=(), help="按上传日期筛选。留空以忽略。")
        if date_range:
            start_date = date_range[0].strftime("%Y%m%d")
            # 构造子筛选器并添加到 filters
            subfilter = Media.upload_date >= start_date
            filters = filters & subfilter if filters else subfilter
            if len(date_range) == 2:
                end_date = date_range[1].strftime("%Y%m%d")
                subfilter = Media.upload_date <= end_date
                filters = filters & subfilter if filters else subfilter

            # 添加搜索筛选器
        title_contains = st.text_input(
            "标题包含",
            help="通过标题中的关键词搜索媒体（不区分大小写）",
        )
        if title_contains:
            subfilter = Media.title.matches(f".*{title_contains}.*", flags=re.IGNORECASE)
            filters = filters & subfilter if filters else subfilter

        # 添加上传者筛选器
        uploader_name = st.text_input("上传者", help="按上传者名称/用户名筛选")
        if uploader_name:
            subfilter = Media.uploader_name.matches(f".*{uploader_name}.*", flags=re.IGNORECASE)
            filters = filters & subfilter if filters else subfilter

        # 添加来源类型筛选器
        source = st.text_input(
            "来源", placeholder="youtube, bilibili.", help="按原始媒体的来源筛选"
        )

        if source:
            subfilter = Media.source.matches(f".*{source}.*", flags=re.IGNORECASE)
            filters = filters & subfilter if filters else subfilter

        # 主要内容
        # --------------------------------

    for dbpath in dbs:
        if st.session_state.library == dbpath.parent.name:
            db = TinyDB(dbpath)
            st.write(f"## 📚 &nbsp; 媒体库 - `{st.session_state.library}`")
            st.markdown(
                f"""
                        <b>媒体: `{len(db.table('Media'))}`</b>; &nbsp;
                        <b>字幕: `{len(db.table('Captions'))}`</b>
                        <b>路径: `{dbpath.parent}`</b>
                        """,
                unsafe_allow_html=True,
            )


    st.write("---")

    query = st.sidebar.text_input(
        "搜索",
        help="这是一个语义搜索引擎，根据内容进行媒体库的搜索",
    )
    if query:
        # TODO: This is currently a hack.
        results = fb.search(query)
        search_quality = st.sidebar.slider("质量", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        if DEV:
            with st.expander("🐞 &nbsp; 结果 JSON", expanded=False):
                st.write(results)

        # 筛选结果。阈值暂定为 0.5
        results = [result for result in results if result["score"] > search_quality]

        if not results:
            st.info("未找到结果。尝试其他查询或降低质量阈值。")
        else:
            # 渲染结果
            for result in results:
                media = result["media"]
                segment = result["segment"]
                # 创建 2 列
                meta_col, media_col = st.columns([2, 1], gap="large")

                with meta_col:
                    # 添加元标题
                    st.write(f"#### `{segment['text']}`")
                    st.markdown(get_formatted_media_info(media), unsafe_allow_html=True)
                    st.markdown("")

                    # 添加导航按钮
                    if st.button("🧐 &nbsp; 详情", key=f"detail-{media.id}-{segment['id']}"):
                        st.session_state.listview = False
                        st.session_state.selected_media = media
                        st.experimental_rerun()

                with media_col:
                    if media.src_name.lower() == "youtube":
                        st.video(media.src, start_time=int(segment["start"]))
                    elif media.is_video:
                        st.video(str(media._loc.resolve()), start_time=int(segment["start"]))
                    else:
                        st.audio(str(media._loc.resolve()), start_time=int(segment["start"]))
                st.write("---")

    else:
        # 获取符合筛选条件的媒体对象列表
        media_objs = fb.media.search(filters) if filters else fb.media.all()

        if media_objs:
            # 渲染每个媒体对象
            for media_obj in media_objs:
                # 创建 2 列
                meta_col, media_col = st.columns([2, 1], gap="large")

                with meta_col:
                    # 添加元标题
                    st.write(f"#### {media_obj.title}")
                    # 如果开发模式打开，则显示原始媒体对象
                    if DEV:
                        with st.expander("原始媒体对象", expanded=False):
                            st.json(media_obj.model_dump())

                    st.markdown(get_formatted_media_info(media_obj), unsafe_allow_html=True)

                    # 添加导航按钮
                    if st.button("🧐 &nbsp; 详情", key=f"detail-{media_obj.id}"):
                        st.session_state.listview = False
                        st.session_state.selected_media = media_obj
                        st.experimental_rerun()

                    if st.button("🗑️ &nbsp; 删除", key=f"delete-{media_obj.id}"):
                        media_obj.delete()
                        st.experimental_rerun()

                # 渲染媒体
                with media_col:
                    # YouTube 视频可以直接嵌入到 streamlit 中
                    if media_obj.src_name.lower() == "youtube":
                        st.video(media_obj.src)
                    elif media_obj.is_video:
                        st.video(str(media_obj._loc.resolve()))
                    else:
                        st.audio(str(media_obj._loc.resolve()))

                st.write("---")
        else:
            if filters:
                st.warning("未找到符合筛选条件的媒体。请尝试不同的筛选条件。")
            else:
                st.info("未找到媒体。添加一些媒体以开始使用。")
                st.write("如果只是想测试应用程序，请单击下面的按钮添加一些示例媒体。")
                if st.button("添加示例媒体"):
                    fb.demo()
                    st.experimental_rerun()

# 详细视图
# -----------
if not st.session_state.listview:
    # 获取所选媒体对象
    media_obj = st.session_state.selected_media

    MAX_TITLE_LEN = 80
    if len(media_obj.title) > MAX_TITLE_LEN:
        st.write(f"### {media_obj.title[:MAX_TITLE_LEN]}...")
    else:
        st.write(f"### {media_obj.title}")

    if DEV:
        with st.expander("媒体对象", expanded=False):
            st.write(media_obj.model_dump())
            # 这目前隐藏在这里以防止混乱，稍后将删除
            context = st.text_area(
                "Context",
                value=(
                    "Using the following content as transcript, your job is answer the following questions.\n"
                    "Answer with a couple of sentences in Snoop Dogg's style. Be very snazzy and creative. "
                ),
            )
            temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.5, step=0.05)

    # 渲染迷你导航
    back_col, del_col = st.sidebar.columns(2)
    with back_col:
        # 添加一个按钮以显示列表视图
        if st.button("◀️ &nbsp; 返回列表", key="back-to-list-main"):
            st.session_state.listview = True
            st.experimental_rerun()
    with del_col:
        if st.button("🗑️ 删除媒体", key=f"delete-{media_obj.id}"):
            fb.media.delete(media_obj)
            st.session_state.listview = True
            st.experimental_rerun()

    # YouTube 视频可以直接嵌入 streamlit
    st.sidebar.audio(str(media_obj._loc.resolve()), start_time=st.session_state.selected_media_offset)
    if media_obj.src_name.lower() == "youtube":
        st.sidebar.video(media_obj.src, start_time=st.session_state.selected_media_offset)
    elif media_obj.is_video:
        st.sidebar.video(str(media_obj._loc.resolve()), start_time=st.session_state.selected_media_offset)

    with st.expander("📝 &nbsp; 关于"):
        st.markdown(get_formatted_media_info(media_obj, details=True), unsafe_allow_html=True)

    if DEV:
        with st.expander("🤔 &nbsp; 提问", expanded=False):
            qcol, acol = st.columns(
                [6, 1],
            )
            question = qcol.text_input("提问", key="question", label_visibility="collapsed")
            ask = acol.button("告诉我！", key="ask")
            captions_obj = media_obj.captions.latest()
            transcript = "\n".join([segment["text"] for segment in captions_obj.load()])
            context_style = context.split("\n")[-1]
            if ask:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    stream=True,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": f"{context}\n\n{transcript}\n\n{context_style}"},
                        {"role": "user", "content": question},
                    ],
                )
                with st.empty():
                    text = ""
                    for chunk in response:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            text += delta["content"]
                        st.write(f"### 🐸 &nbsp; `{text}`")

    # 渲染字幕
    captions = media_obj.captions.all()

    if captions:
        tabs = st.tabs([f"{c.lang} ({c.by[:7]})" for c in captions])

        # TODO: 为加快加载速度，对字幕进行分页
        for i, caption_obj in enumerate(captions):
            tab = tabs[i]
            with tab:
                with st.expander("📝 &nbsp; 字幕信息", expanded=False):
                    st.json(caption_obj.model_dump())

                # 字幕下载链接（VTT 文件）
                caption_file_path = st.session_state.fb.config.libdir / caption_obj.loc
                with open(caption_file_path) as f:
                    st.download_button("下载 WebVTT（VTT 文件）", f, file_name=f"{media_obj.title}.vtt")

                # 加载字幕文件
                segments = caption_obj.load()

                for segment in segments:
                    if not segment["text"].strip():
                        continue
                    # 创建 2 列
                    meta_col, text_col = st.columns([1, 6], gap="small")

                    with meta_col:
                        if st.button(
                            f"▶️ &nbsp; {int(segment['start'])} - {int(segment['end'])}",
                            key=f"play-{segment['start']}-{segment['end']}",
                        ):
                            st.session_state.selected_media_offset = int(segment["start"])
                            st.experimental_rerun()

                    with text_col:
                        st.write(f"##### `{segment['text']}`")
