"""twa_edu_core — tw-edu-* 教學技能的共用程式碼。

`from twa_edu_core import *` 的輸出集合刻意與舊的
`from tw_edu_doc_utils import *` **完全一致**（含 Document / Pt / date 等
當初由星號匯入連帶帶出的名稱），因此既有生成腳本改一行 import 即可，
不需要調整任何呼叫。這個相容性由 scripts/verify_core_api.py 驗證。
"""
from __future__ import annotations

from datetime import date

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from .docx_utils import (
    add_header_footer,
    cell_write,
    cover_page,
    data_cell,
    header_cell,
    new_doc_a4,
    section_heading,
    set_cell_bg,
    set_cell_border,
)
from .fonts import (
    DEFAULT_CJK_FONT,
    register_cjk_fonts,
    register_reportlab_cjk,
    set_east_asia_font,
)
from .theme import (
    BLUE_DEEP,
    BLUE_LIGHT,
    BLUE_MID,
    DARK_TEXT,
    GOLD,
    GRAY_LIGHT,
    GREEN,
    MUTED_TEXT,
    ORANGE,
    RED_SOFT,
    WHITE,
    rgb_hex,
)

__version__ = "1.0.0"

__all__ = [
    # 由 python-docx 轉出（舊 star-import 的相容性）
    "Document", "Pt", "Cm", "RGBColor",
    "WD_ALIGN_PARAGRAPH", "WD_TABLE_ALIGNMENT", "qn", "OxmlElement", "date",
    # 色票
    "BLUE_DEEP", "BLUE_MID", "BLUE_LIGHT", "WHITE", "GRAY_LIGHT",
    "DARK_TEXT", "GREEN", "GOLD", "ORANGE", "RED_SOFT", "MUTED_TEXT",
    "rgb_hex",
    # Word 版面元件
    "set_cell_bg", "set_cell_border", "cell_write", "header_cell",
    "data_cell", "section_heading", "cover_page", "new_doc_a4",
    "add_header_footer",
    # 字型
    "set_east_asia_font", "register_cjk_fonts", "register_reportlab_cjk",
    "DEFAULT_CJK_FONT",
]
