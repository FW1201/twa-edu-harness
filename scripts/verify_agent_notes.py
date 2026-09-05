#!/usr/bin/env python3
"""驗證 Agent Note 的路徑分類、Status 與標題格式。

Note 的價值在於三個月後找得到、讀得懂。若 Status 與所在資料夾對不上，
「這個決策到底做了沒」就要靠讀內文猜——那就失去意義了。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOTES = REPO / ".agents" / "notes"

STATUSES = {"proposed", "implemented", "rejected"}
CLASSES = {"architecture", "feature", "process"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
TITLE_RE = re.compile(r"^# Agent Note: .+")
STATUS_RE = re.compile(r"^Status:\s*(\w+)\s*$", re.M)

REQUIRED_SECTIONS = ("## Problem", "## Decision", "## Consequences")


def main() -> int:
    if not NOTES.exists():
        print("❌ 找不到 .agents/notes/")
        return 1

    errors: list[str] = []
    count = 0

    for path in sorted(NOTES.rglob("*.md")):
        rel = path.relative_to(REPO)
        if path.name == "README.md":
            continue
        parts = path.relative_to(NOTES).parts
        if len(parts) != 3:
            errors.append(f"{rel}: 路徑應為 <status>/<class>/<檔名>")
            continue
        status_dir, class_dir, filename = parts
        count += 1

        if status_dir not in STATUSES:
            errors.append(f"{rel}: 未知的 status 資料夾 `{status_dir}`")
        if class_dir not in CLASSES:
            errors.append(f"{rel}: 未知的 class 資料夾 `{class_dir}`")
        if not DATE_RE.match(filename):
            errors.append(f"{rel}: 檔名應為 YYYY-MM-DD-topic.md（小寫 kebab-case）")

        text = path.read_text(encoding="utf-8")
        if not TITLE_RE.match(text.splitlines()[0] if text else ""):
            errors.append(f"{rel}: 首行應為 `# Agent Note: <標題>`")

        m = STATUS_RE.search(text)
        if not m:
            errors.append(f"{rel}: 缺少 `Status: <status>` 行")
        elif m.group(1) != status_dir:
            errors.append(
                f"{rel}: Status 標為 `{m.group(1)}`，但放在 `{status_dir}/` 底下")

        for section in REQUIRED_SECTIONS:
            if section not in text:
                errors.append(f"{rel}: 缺少 `{section}` 段落")

    if errors:
        print(f"❌ {len(errors)} 項 Agent Note 格式問題：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✅ {count} 篇 Agent Note 格式正確")
    return 0


if __name__ == "__main__":
    sys.exit(main())
