#!/usr/bin/env python3
"""驗證所有 SKILL.md 的 frontmatter。

21 支技能已於 P1 全數補齊契約 v1，因此預設就是嚴格模式。
`--lenient` 只保留給遷移中的分支：把契約欄位的缺漏降為 warning。

CI 一旦長期是紅的就沒人看，沒人看就擋不住問題——這正是舊 repo 走上的路。
所以規則要嚴，但每次收緊之前要先讓現況通過。
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
LEGACY_KEYS = {"disableModelInvocation", "modelInvocable", "userInvocable"}
VALID_TOOLS = {"Bash", "Read", "Write", "Edit", "WebSearch", "WebFetch",
               "Task", "Agent", "Glob", "Grep", "NotebookEdit", "TodoWrite"}
DESC_MAX = 300
REQUIRED_NOW = ("name", "description", "version")
REQUIRED_V1 = ("author", "license", "whenToUse", "metadata")


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1]) or {}


def tool_list(value):
    """allowed-tools 可能是字串或陣列，兩種都接受。"""
    if isinstance(value, str):
        return [t.strip() for t in value.split(",") if t.strip()]
    if isinstance(value, list):
        return [str(t).strip() for t in value if str(t).strip()]
    return []


def check(skill_dir: Path, errors: list[str], warnings: list[str]) -> None:
    name_hint = skill_dir.name
    fm = parse_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    if fm is None:
        errors.append(f"{name_hint}: 缺少 YAML frontmatter")
        return

    for field in REQUIRED_NOW:
        if field not in fm:
            errors.append(f"{name_hint}: 缺少必填欄位 `{field}`")

    name = str(fm.get("name", ""))
    if name and not NAME_RE.match(name):
        errors.append(f"{name_hint}: name `{name}` 不是 kebab-case")
    if name and name != skill_dir.name:
        errors.append(f"{name_hint}: name `{name}` 與目錄名不一致")

    desc = " ".join(str(fm.get("description", "")).split())
    if len(desc) > DESC_MAX:
        warnings.append(f"{name_hint}: description {len(desc)} 字元，超過 {DESC_MAX}")

    for legacy in LEGACY_KEYS & set(fm):
        errors.append(f"{name_hint}: 禁用 camelCase 舊鍵 `{legacy}`")

    version = str(fm.get("version", ""))
    if version and not SEMVER_RE.match(version):
        errors.append(f"{name_hint}: version `{version}` 不符 SemVer")
    elif version.count(".") == 1:
        warnings.append(f"{name_hint}: version `{version}` 缺 patch 位，應為 x.y.z")

    for tool in tool_list(fm.get("allowed-tools")):
        if tool not in VALID_TOOLS and not tool.startswith("mcp__"):
            errors.append(f"{name_hint}: 非法工具名 `{tool}`（MCP 工具應為 mcp__*）")

    missing_v1 = [f for f in REQUIRED_V1 if f not in fm]
    if missing_v1:
        warnings.append(f"{name_hint}: 尚未補齊契約 v1 欄位 {missing_v1}")

    for shared in (fm.get("metadata") or {}).get("shared", []) or []:
        if not (Path("shared") / f"{shared}.md").exists():
            errors.append(f"{name_hint}: metadata.shared 指向不存在的 shared/{shared}.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lenient", action="store_true",
                    help="把契約 v1 的缺漏降為 WARNING（僅供遷移中的分支使用）")
    args = ap.parse_args()

    dirs = sorted(p for p in Path("skills").iterdir() if (p / "SKILL.md").is_file())
    if not dirs:
        print("❌ skills/ 下找不到任何 SKILL.md")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    for d in dirs:
        check(d, errors, warnings)

    if not args.lenient:
        errors.extend(warnings)
        warnings = []

    for w in warnings:
        print(f"⚠️  {w}")
    if errors:
        print(f"\n❌ {len(errors)} 項驗證失敗：")
        for e in errors:
            print(f"  - {e}")
        return 1

    tail = f"（另有 {len(warnings)} 項 warning，P1 補齊）" if warnings else ""
    print(f"\n✅ {len(dirs)} 支 SKILL.md 通過 frontmatter 驗證 {tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
