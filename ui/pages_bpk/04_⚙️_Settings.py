import streamlit as st
from config import DEV, get_page_config, init_session

# 设置页面配置并初始化会话
st.set_page_config(**get_page_config())
init_session(st.session_state)
# 如果在开发模式下，则渲染会话状态
if DEV:
    with st.expander("会话状态"):
        st.write(st.session_state)

# 别名以提高可读性
# --------------------------------
fb = st.session_state.fb

# Whisper 配置
# --------------------------------
st.write("#### 🗣️✍️ OpenAI Whisper")
with st.expander("# ⚙️ 设置", expanded=False), st.form("whisper_config"):
    model_options = ["tiny", "base", "small", "medium", "large", "tiny.en", "base.en", "small.en", "medium.en"]
    selected_model = model_options.index(fb.models.whisper.model)
    whisper_model = st.selectbox("Model", options=model_options, index=selected_model)
    temperature = st.text_input(
        "Temperature",
        value=", ".join([str(t) for t in fb.models.whisper.temperature]),
        help="Comma separated list of floats",
    )
    no_speech_threshold = st.slider(
        "No Speech Threshold",
        min_value=0.0,
        max_value=1.0,
        value=fb.models.whisper.no_speech_threshold,
        step=0.05,
    )
    logprob_threshold = st.slider(
        "Logprob Threshold",
        min_value=-20.0,
        max_value=0.0,
        value=fb.models.whisper.logprob_threshold,
        step=0.1,
    )
    compression_ratio_threshold = st.slider(
        "Compression Ratio Threshold",
        min_value=0.0,
        max_value=10.0,
        value=fb.models.whisper.compression_ratio_threshold,
        step=0.1,
    )
    condition_on_previous_text = st.checkbox(
        "Condition on previous text", value=fb.models.whisper.condition_on_previous_text
    )
    task_options = ["transcribe", "translate"]
    task = st.selectbox("Default mode", options=task_options, index=task_options.index(fb.models.whisper.task))
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
    language = st.selectbox("Language", options=lang_options, index=lang_options.index(fb.models.whisper.language))

    save_config = st.form_submit_button(label="💾 保存")
    success_container = st.empty()

    if save_config:
        # Parse temperature as a comma separated list
        temperature = tuple(float(x.strip()) for x in temperature.split(","))
        fb.models.whisper.model = whisper_model
        fb.models.whisper.temperature = temperature
        fb.models.whisper.no_speech_threshold = no_speech_threshold
        fb.models.whisper.logprob_threshold = logprob_threshold
        fb.models.whisper.compression_ratio_threshold = compression_ratio_threshold
        fb.models.whisper.condition_on_previous_text = condition_on_previous_text
        fb.models.whisper.task = task
        fb.models.whisper.language = language
        fb.models.save_settings()
        success_container.success("设置保存成功！")
