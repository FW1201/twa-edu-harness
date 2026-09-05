#!/usr/bin/env python3
"""產生可獨立安裝的技能版本：把 shared/ 協議內聯進 SKILL.md。

`npx skills add <repo>/skills/<name>` 只會複製該技能自己的目錄。
安裝後 `../../shared/` 不存在，而 19 支技能把那四份協議宣告為
「必要前置步驟」——這正是 v3.x 那個 100% 失效的 bug。

開發時引用 shared/（單一真源），發版時由這支腳本展開成自足的副本。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SHARED = REPO / "shared"
REF_RE = re.compile(r"`\.\./\.\./shared/([a-z-]+)\.md`")

TITLES = {
    "concept-alignment": "概念對齊協議",
    "grade-adapter": "學段適配協議",
    "guided-collection": "引導式資訊收集協議",
    "mcp-strategy": "MCP 使用策略",
}


def inline(skill_dir: Path, out_root: Path) -> tuple[str, int]:
    md = skill_dir / "SKILL.md"
    text = md.read_text(encoding="utf-8")
    fm = yaml.safe_load(text.split("---", 2)[1]) or {}
    declared = list((fm.get("metadata") or {}).get("shared", []) or [])

    dest = out_root / skill_dir.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skill_dir, dest,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    if not declared:
        return skill_dir.name, 0

    # 內文引用改指向本檔內的附錄
    body = REF_RE.sub(
        lambda m: f"本檔附錄的「{TITLES.get(m.group(1), m.group(1))}」",
        (dest / "SKILL.md").read_text(encoding="utf-8"))

    parts = ["", "---", "", "## 附錄：共用協議",
             "",
             "> 以下內容由 `scripts/build_standalone_skills.py` 在發版時自動內聯，",
             "> 使本技能單獨安裝後仍可獨立運作。真源為 repo 的 `shared/`，",
             "> 請勿直接編輯此附錄。", ""]
    for name in declared:
        src = SHARED / f"{name}.md"
        if not src.exists():
            raise SystemExit(f"❌ {skill_dir.name}: shared/{name}.md 不存在")
        content = src.read_text(encoding="utf-8")
        # 協議自身的標題降一級，避免與 SKILL.md 的層級打架
        content = re.sub(r"^(#{1,5}) ", r"#\1 ", content, flags=re.M)
        parts += [f"### {TITLES.get(name, name)}", "", content.strip(), ""]

    (dest / "SKILL.md").write_text(body.rstrip() + "\n" + "\n".join(parts) + "\n",
                                   encoding="utf-8")
    return skill_dir.name, len(declared)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist/skills")
    args = ap.parse_args()

    out_root = REPO / args.out
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    total = 0
    for skill_dir in sorted(REPO.glob("skills/*/")):
        if not (skill_dir / "SKILL.md").is_file():
            continue
        name, n = inline(skill_dir, out_root)
        total += 1
        print(f"  {name:<34} 內聯 {n} 份協議")

    print(f"\n✅ {total} 支獨立版技能已輸出至 {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
