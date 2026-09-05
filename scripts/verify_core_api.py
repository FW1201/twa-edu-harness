#!/usr/bin/env python3
"""驗證 twa_edu_core 對舊 tw_edu_doc_utils 的 API 相容性。

15 支生成腳本原本寫 `from tw_edu_doc_utils import *`，遷移後改成
`from twa_edu_core import *`。星號匯入會連帶帶出 Document / Pt / date 等名稱，
少掉任何一個都會讓腳本在執行期才炸——而且是在教師要產出教案的時候。

因此把舊版的公開介面凍結在下方，任何縮減都要 CI 紅。
新增名稱是允許的（不會破壞既有呼叫）。
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

# 舊 tw_edu_doc_utils.py 的 star-import 輸出（v3.x，md5 bd9f208e…），30 個名稱
LEGACY_SURFACE = {
    # python-docx 轉出
    "Document", "Pt", "Cm", "RGBColor",
    "WD_ALIGN_PARAGRAPH", "WD_TABLE_ALIGNMENT", "qn", "OxmlElement", "date",
    # 色票
    "BLUE_DEEP", "BLUE_MID", "BLUE_LIGHT", "WHITE", "GRAY_LIGHT",
    "DARK_TEXT", "GREEN", "GOLD", "ORANGE", "RED_SOFT", "rgb_hex",
    # 版面元件
    "set_cell_bg", "set_cell_border", "set_east_asia_font", "cell_write",
    "header_cell", "data_cell", "section_heading", "cover_page",
    "new_doc_a4", "add_header_footer",
}

# 函式的 (參數名, 預設值) — 型別註解不比對，只比對呼叫相容性
LEGACY_SIGNATURES = {
    "rgb_hex": [("c", inspect.Parameter.empty)],
    "set_cell_bg": [("cell", inspect.Parameter.empty), ("color", inspect.Parameter.empty)],
    "set_cell_border": [("cell", inspect.Parameter.empty), ("color", "2471A3"), ("size", "4")],
    "set_east_asia_font": [("run", inspect.Parameter.empty), ("font", "標楷體")],
    "cell_write": [("cell", inspect.Parameter.empty), ("text", inspect.Parameter.empty),
                   ("bold", False), ("size", 11), ("color", ...), ("center", False),
                   ("font", "標楷體")],
    "header_cell": [("cell", inspect.Parameter.empty), ("text", inspect.Parameter.empty),
                    ("bg", ...), ("size", 11)],
    "data_cell": [("cell", inspect.Parameter.empty), ("text", inspect.Parameter.empty),
                  ("row_idx", 0), ("center", False)],
    "section_heading": [("doc", inspect.Parameter.empty), ("text", inspect.Parameter.empty),
                        ("level", 1)],
    "cover_page": [("doc", inspect.Parameter.empty), ("title", inspect.Parameter.empty),
                   ("subtitle", inspect.Parameter.empty),
                   ("info_pairs", inspect.Parameter.empty), ("accent_color", ...)],
    "new_doc_a4": [("default_font", "標楷體")],
    "add_header_footer": [("doc", inspect.Parameter.empty),
                          ("header_text", inspect.Parameter.empty), ("show_page", True)],
}


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
    try:
        import twa_edu_core as core
    except ImportError as exc:
        print(f"❌ 無法匯入 twa_edu_core：{exc}")
        return 1

    errors: list[str] = []

    exported = set(core.__all__)
    for name in sorted(LEGACY_SURFACE - exported):
        errors.append(f"__all__ 缺少舊介面名稱 `{name}`（星號匯入的腳本會壞）")
    for name in sorted(LEGACY_SURFACE & exported):
        if not hasattr(core, name):
            errors.append(f"`{name}` 列在 __all__ 但實際不存在")

    for fn_name, expected in LEGACY_SIGNATURES.items():
        fn = getattr(core, fn_name, None)
        if fn is None:
            continue  # 上面已回報
        params = list(inspect.signature(fn).parameters.values())
        if len(params) != len(expected):
            errors.append(
                f"`{fn_name}` 參數數量 {len(params)}，舊版為 {len(expected)}")
            continue
        for got, (exp_name, exp_default) in zip(params, expected):
            if got.name != exp_name:
                errors.append(
                    f"`{fn_name}` 參數名 `{got.name}` 與舊版 `{exp_name}` 不符")
            if exp_default is ...:
                continue  # 色票物件，只確認「有預設值」
            if got.default != exp_default:
                errors.append(
                    f"`{fn_name}` 參數 `{exp_name}` 預設值 {got.default!r}，"
                    f"舊版為 {exp_default!r}")

    if errors:
        print(f"❌ {len(errors)} 項 API 相容性問題：")
        for e in errors:
            print(f"  - {e}")
        return 1

    extra = sorted(exported - LEGACY_SURFACE)
    print(f"✅ twa_edu_core 完整涵蓋舊版 {len(LEGACY_SURFACE)} 個公開名稱"
          + (f"，另新增 {len(extra)} 個：{', '.join(extra)}" if extra else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
