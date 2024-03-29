from datetime import datetime
from pathlib import Path

import humanize


def get_formatted_date(date_str: str) -> str:
    """将 ISO 格式的日期字符串转换为人类可读的格式。

    Args:
        date_str: ISO 格式的日期字符串。
    """
    # 首先转换为 datetime 对象
    datetime_obj = datetime.fromisoformat(date_str)

    # 然后转换为人类可读的格式
    date = datetime_obj.strftime("%d %b %Y")
    time = datetime_obj.strftime("%I:%M%p")

    # 返回格式化后的日期
    return f"{date} {time}"

def get_formatted_media_info(media_obj, details: bool = False) -> str:
    """获取媒体对象的人类可读字符串。"""
    # 获取上传者字符串
    uploaded_by = media_obj.uploader_name if media_obj.uploader_name else media_obj.uploader_id
    if media_obj.uploader_url:
        uploaded_by_str = f'<a href="{media_obj.uploader_url}">{uploaded_by}</a>'
    else:
        uploaded_by_str = f"`{uploaded_by}`"

    # 获取上传日期字符串
    uploaded_datestr = datetime.strptime(media_obj.upload_date, "%Y%m%d").strftime("%Y年%m月%d日")

    # 获取原始来源字符串
    if media_obj.src.startswith("http"):
        original_str = f"<a href='{media_obj.src}'>{media_obj.src_name}</a>"
    else:
        original_str = media_obj.src_name

    infostr = ""
    if details:
        infostr += f""" <i>标题</i>: `{media_obj.title}`<br/>"""

    infostr += f"""
        <i>来源</i>: <b>{uploaded_by_str}</b> 来自 <b>{original_str} `[{uploaded_datestr}]`</b><br/>
        <i>添加时间</i>: <b>`{get_formatted_date(media_obj.created)}`</b><br/>
        <i>时长</i>: <b>`{int(float(media_obj.duration))}秒`</b>; &nbsp; <i>大小</i>: <b>`{humanize.naturalsize(media_obj.filesize)}`</b><br/>
    """

    if details:
        infostr += f"""<i>位置</i>: `{media_obj.loc}`<br/>"""
        if media_obj.tags:
            infostr += f"""<i>标签</i>: `{", ".join(media_obj.tags)}`<br/>"""
        if media_obj.description:
            infostr += f"""<hr/><b>描述</b>: {media_obj.description}<br/>"""

    return infostr
