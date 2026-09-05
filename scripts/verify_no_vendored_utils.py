#!/usr/bin/env python3
"""禁止在 skills/*/scripts/ 內複製 twa_edu_core 已提供的共用程式碼。

v3.x 時 tw_edu_doc_utils.py 有 15 份內容完全相同的複本散在各 skill 底下。
改個中文字型要改 15 次，漏改一次就產出外觀不一致的 .docx。
這道 gate 讓那個狀態無法再度出現。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# 曾經被複製、現已由 twa_edu_core 提供的檔名
BANNED_FILENAMES = {
    "tw_edu_doc_utils.py",
    "twa_edu_core.py",
    "doc_utils.py",
}

# twa_edu_core 已提供、不該在 skill 腳本內重新實作的函式
BANNED_DEFINITIONS = {
    "set_cell_bg", "set_cell_border", "cell_write",
    "header_cell", "data_cell", "cover_page", "new_doc_a4",
    "add_header_footer", "set_east_asia_font",
}

# 例外：這兩支在 v3.x 就以行內實作寫成，函式名與參數都和共用版不同，
# 貿然換掉會改變既有教案 / 學習單的版面。收斂計畫見
# .agents/notes/proposed/architecture/2026-09-05-inline-docx-helpers.md
GRANDFATHERED = {
    "tw-edu-lesson-plan-108",
    "tw-edu-differentiated",
}


def main() -> int:
    errors: list[str] = []

    for path in sorted(REPO.glob("skills/*/scripts/*.py")):
        if path.name in BANNED_FILENAMES:
            errors.append(
                f"{path.relative_to(REPO)}: 重複的共用工具檔，"
                f"請改 `from twa_edu_core import *`")

    for path in sorted(REPO.glob("skills/*/scripts/*.py")):
        skill = path.parts[-3]
        if skill in GRANDFATHERED:
            continue
        text = path.read_text(encoding="utf-8")
        for fn in sorted(BANNED_DEFINITIONS):
            if f"def {fn}(" in text:
                errors.append(
                    f"{path.relative_to(REPO)}: 重新實作了 `{fn}()`，"
                    f"twa_edu_core 已提供")

    if errors:
        print(f"❌ {len(errors)} 項重複實作：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✅ skills/*/scripts/ 無重複的共用工具"
          f"（{len(GRANDFATHERED)} 支行內實作已列為既存例外）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
