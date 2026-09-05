"""中日韓字型設定。

Word 走 `set_east_asia_font()`；圖表走 `register_cjk_fonts()`。
兩者都必須明確設定，否則中文在 matplotlib 會渲染成空白方框（tofu）。
"""
from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DEFAULT_CJK_FONT = "標楷體"
DEFAULT_LATIN_FONT = "Arial"

# 依偏好順序嘗試，取第一個系統實際安裝的
MATPLOTLIB_CJK_CANDIDATES = (
    "Noto Sans CJK JP",
    "Noto Sans CJK TC",
    "PingFang TC",
    "Heiti TC",
    "Microsoft JhengHei",
)
REPORTLAB_CJK_FONT = "STSong-Light"


def set_east_asia_font(run, font: str = DEFAULT_CJK_FONT) -> None:
    """為 python-docx 的 run 指定東亞字型。

    python-docx 的 `run.font.name` 只設 ascii 字型，中文字仍會落到 Word 預設字型。
    必須另外寫入 `w:eastAsia` 才會生效。
    """
    rPr = run._r.get_or_add_rPr()
    rF = OxmlElement("w:rFonts")
    rF.set(qn("w:eastAsia"), font)
    rF.set(qn("w:ascii"), DEFAULT_LATIN_FONT)
    rPr.insert(0, rF)


def register_cjk_fonts() -> str | None:
    """設定 matplotlib 的中文字型，回傳實際採用的字型名（找不到則 None）。

    產圖腳本在 `import matplotlib.pyplot` 之後、繪圖之前呼叫一次即可。
    """
    try:
        import matplotlib
        from matplotlib import font_manager
    except ImportError:
        return None

    available = {f.name for f in font_manager.fontManager.ttflist}
    for candidate in MATPLOTLIB_CJK_CANDIDATES:
        if candidate in available:
            matplotlib.rcParams["font.family"] = candidate
            matplotlib.rcParams["axes.unicode_minus"] = False
            return candidate
    return None


def register_reportlab_cjk() -> str | None:
    """向 ReportLab 註冊中文字型，回傳字型名（不可用則 None）。"""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    except ImportError:
        return None

    try:
        pdfmetrics.registerFont(UnicodeCIDFont(REPORTLAB_CJK_FONT))
    except Exception:
        return None
    return REPORTLAB_CJK_FONT
