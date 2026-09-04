#!/usr/bin/env python3
"""驗證 SKILL.md 內的相對連結都指向存在的檔案，且不逸出 repo 根。

這道 gate 存在的原因：舊 repo 有 19 支 SKILL.md 寫著 `../../tw_edu_*.md`，
從 skill 目錄往上兩層落在 repo 之外。這些檔案被 19 支宣告為「必要前置步驟」，
但在使用者機器上一份都不存在——沒有任何檢查擋得住，因為根本沒有檢查。
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

PATTERNS = [
    re.compile(r"\[[^\]]*\]\((\.{1,2}/[^)\s]+)\)"),                       # markdown 連結
    re.compile(r"`(\.{1,2}/[^`\s]+\.(?:md|py|json|ya?ml|txt|tsx|mjs))`"),  # 反引號路徑
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="skills", help="要掃描的根目錄")
    ap.add_argument("--standalone", action="store_true",
                    help="內聯版檢查：完全不允許連結離開 skill 自身目錄")
    args = ap.parse_args()

    repo_root = Path.cwd().resolve()
    scan_root = Path(args.root)
    errors: list[str] = []
    checked = 0

    for md in sorted(scan_root.glob("*/SKILL.md")):
        text = md.read_text(encoding="utf-8")
        targets = {t for pat in PATTERNS for t in pat.findall(text)}
        for target in sorted(targets):
            checked += 1
            resolved = (md.parent / target).resolve()
            rel = md.relative_to(repo_root) if md.is_absolute() else md

            if not resolved.exists():
                errors.append(f"{rel}: `{target}` 指向不存在的檔案")
                continue

            boundary = md.parent.resolve() if args.standalone else repo_root
            if boundary not in resolved.parents:
                where = "skill 目錄" if args.standalone else "repo 根"
                errors.append(f"{rel}: `{target}` 逸出 {where}（→ {resolved}）")

    if errors:
        print(f"❌ {len(errors)} 個連結問題：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✅ {args.root} 底下 {checked} 條相對連結全部有效"
          + ("（內聯版：無外部依賴）" if args.standalone else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
