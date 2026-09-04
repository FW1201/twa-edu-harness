#!/usr/bin/env python3
"""從 skills/ 產生 README 的 Skills 表格，寫入 GENERATED 標記區塊。

    python scripts/gen_skill_index.py            # 寫入 README.md
    python scripts/gen_skill_index.py --check    # 只比對，不一致則 exit 1

舊 repo 的 README 手寫「19 個 Skills」，實際 21 支，還列了不存在的項目。
只要清單是手寫的，它遲早會偏離現實。這支腳本讓數量不可能對不上。
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

import yaml

BEGIN = "<!-- BEGIN GENERATED skill-index (scripts/gen_skill_index.py) -->"
END = "<!-- END GENERATED skill-index -->"

# 分類順序即表格呈現順序
CATEGORIES = [
    ("課程設計", ["lesson-plan-108", "curriculum-mapper", "differentiated",
                  "interdisciplinary", "pbl-designer"]),
    ("評量命題", ["exam-generator", "rubric-designer", "formative-assessment",
                  "anti-ai-assessment"]),
    ("教材資源", ["worksheet-creator", "slides-creator", "mini-app"]),
    ("學生表現", ["feedback-writer", "learning-portfolio"]),
    ("班級行政", ["classroom-culture", "parent-communication",
                  "school-document", "meeting-facilitator"]),
    ("學術支援", ["citation-checker", "research-viz"]),
    ("套組設定", ["synchronizer"]),
]


def load(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm = yaml.safe_load(text.split("---", 2)[1]) or {}
    desc = " ".join(str(fm.get("description", "")).split())
    # 取第一句作為表格摘要，觸發詞留給 SKILL.md 自己
    summary = re.split(r"(?<=[。．])", desc)[0].strip() or desc[:60]
    return {
        "name": skill_dir.name,
        "version": str(fm.get("version", "—")),
        "summary": summary,
    }


def build_table(skills: dict[str, dict]) -> str:
    seen: set[str] = set()
    lines = [f"**共 {len(skills)} 支 Skills**", ""]
    for cat, members in CATEGORIES:
        rows = [skills[f"tw-edu-{m}"] for m in members if f"tw-edu-{m}" in skills]
        if not rows:
            continue
        lines += [f"#### {cat}", "", "| Skill | 版本 | 說明 |", "|---|---|---|"]
        for r in rows:
            seen.add(r["name"])
            lines.append(f"| `{r['name']}` | {r['version']} | {r['summary']} |")
        lines.append("")
    leftover = sorted(set(skills) - seen)
    if leftover:
        lines += ["#### 未分類", "", "| Skill | 版本 | 說明 |", "|---|---|---|"]
        lines += [f"| `{skills[n]['name']}` | {skills[n]['version']} | {skills[n]['summary']} |"
                  for n in leftover]
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    skills = {d.name: load(d) for d in sorted(Path("skills").iterdir())
              if (d / "SKILL.md").is_file()}
    block = f"{BEGIN}\n{build_table(skills)}\n{END}"

    readme = Path("README.md")
    text = readme.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print(f"❌ README.md 找不到 GENERATED 標記區塊")
        return 1

    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block,
                 text, flags=re.S)
    # badge 也一起同步，數量只有一個真源
    new = re.sub(r"Skills-\d+-", f"Skills-{len(skills)}-", new)

    if args.check:
        if new != text:
            print("❌ README 的 Skills 清單與 skills/ 不一致，"
                  "請執行 python scripts/gen_skill_index.py")
            return 1
        print(f"✅ README 與 {len(skills)} 支 Skills 一致")
        return 0

    readme.write_text(new, encoding="utf-8")
    print(f"✅ 已產生 {len(skills)} 支 Skills 的索引表格")
    return 0


if __name__ == "__main__":
    sys.exit(main())
