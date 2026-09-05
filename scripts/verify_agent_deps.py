#!/usr/bin/env python3
"""驗證 SKILL.md 提到的 subagent 都能在 agents/ 找到定義。

技能可以召喚 subagent，但 subagent 的定義住在 agent 目錄、
不會隨 `npx skills add` 一起安裝。若定義不在本 repo 內，
使用者安裝後該功能會在執行期靜默失效。

（tw-edu-citation-checker 的批次並行模式就發生過這件事：
功能 2026-05-07 做好，agent 定義卻只存在於作者本機。）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO / "agents"

# 反引號包住、且緊鄰 subagent / agent 字樣的名稱
PATTERN = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`\s*subagent")


def available_agents() -> set[str]:
    if not AGENTS_DIR.exists():
        return set()
    return {p.stem for p in AGENTS_DIR.glob("*.md") if p.stem != "README"}


def main() -> int:
    have = available_agents()
    errors: list[str] = []
    found = 0

    for md in sorted(REPO.glob("skills/*/SKILL.md")):
        for name in sorted(set(PATTERN.findall(md.read_text(encoding="utf-8")))):
            found += 1
            if name not in have:
                errors.append(
                    f"{md.relative_to(REPO)}: 召喚 `{name}` subagent，"
                    f"但 agents/{name}.md 不存在"
                    f"（使用者安裝後此功能會失效）")

    if errors:
        print(f"❌ {len(errors)} 項 agent 依賴缺失：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✅ SKILL.md 引用的 {found} 個 subagent 依賴全部隨附於 agents/"
          f"（共 {len(have)} 個定義）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
