import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

# 从任何调用它的位置加载环境变量
load_dotenv()

# 项目结构
# -----------------
APP_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = APP_DIR.parent.absolute()
TEMP_DIR = Path(tempfile.gettempdir())

# 可以使用环境变量设置整个站点的配置
DEV = os.getenv("FROGBASE_DEV", False)
VERBOSE = os.getenv("FROGBASE_VERBOSE", False)
DATADIR = os.getenv("FROGBASE_DATADIR", APP_DIR / "data")
LIBRARY = os.getenv("FROGBASE_LIBRARY", "default")
PERSIST = os.getenv("FROGBASE_PERSIST", True)
OPENAI_KEY = os.getenv("OPENAI_KEY", None)

# 通用页面配置
# --------------------------
ABOUT = """
### 轻松发现、转录和搜索媒体。
从YouTube、TikTok等热门平台下载，上传您自己的内容，并享受方便的问答界面。

"""


def get_page_config(page_title_prefix="", layout="wide"):
    return {
        "page_title": f"{page_title_prefix}Yif UI",
        "page_icon": "🐸",
        "layout": layout,
        "initial_sidebar_state": "expanded",
        "menu_items": {
            "Get Help": "https://twitter.com/hayabhay",
            "Report a bug": "https://github.com/hayabhay/frogbase/issues",
            "About": ABOUT,
        },
    }


def init_session(session_state, library: str = LIBRARY, reset: bool = False):
    """站点范围的函数，用于初始化会话状态变量（如果它们不存在）"""
    # 在开发模式下运行意味着使用本地的frogbase模块，而不是pip安装版本
    # if DEV:
    if True:  # TODO: 在软件包稳定后删除此行
        # 将项目目录插入系统路径的开头，以覆盖从pip安装的frogbase
        sys.path.insert(0, str(PROJECT_DIR))

    # 现在导入frogbase
    from frogbase import FrogBase

    # 会话状态
    # --------------------------------
    # 创建一个frogbase实例
    if "fb" not in session_state or reset:
        session_state.library = library
        session_state.fb = FrogBase(datadir=DATADIR, library=library, verbose=VERBOSE, dev=DEV, persist=PERSIST)

    # 将会话状态设置为切换列表和详细视图
    if "listview" not in session_state or reset:
        session_state.listview = True
        session_state.selected = None
        session_state.selected_media_offset = 0
