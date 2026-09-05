#!/usr/bin/env python3
"""掃描全 repo，確保不出現受限的上游專案名稱與其套件前綴。

本 repo 的架構參考自某個上游 harness 專案，但擁有者明確要求：
**repo 內與所有對外文件都不得出現該專案的名稱或套件名**，一律以
`ref-harness` 指稱。理由見
.agents/notes/implemented/architecture/2026-09-05-runtime-neutral-bundle.md

人會忘記，所以交給 CI 記住。

實作細節：受限字串以 base64 存放，**讓這支 gate 本身不含明文**——
否則掃描器會掃到自己，或反過來成為那些字串進入 repo 的破口。
"""
from __future__ import annotations

import base64
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SELF = Path(__file__).name

# base64 編碼的受限字串（小寫比對）
_ENCODED = [
    "ZGVlcHNlZWs=",
    "ZHNoLXBsdWdpbg==",
    "ZHNoLXNraWxs",
    "ZHNoLXRvb2w=",
    "Y29yZGlz",
]
TERMS = [base64.b64decode(e).decode() for e in _ENCODED]

# 只掃版控中的文字檔
TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".toml", ".txt",
                 ".sh", ".mjs", ".js", ".ts", ".html", ".css", ""}
SKIP_DIRS = {".git", "dist", ".venv", "node_modules", "__pycache__"}


def tracked_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout
        return [REPO / line for line in out.splitlines() if line]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [p for p in REPO.rglob("*")
                if p.is_file() and not any(d in p.parts for d in SKIP_DIRS)]


def main() -> int:
    hits: list[str] = []
    scanned = 0

    for path in tracked_files():
        if not path.is_file() or path.name == SELF:
            continue
        if any(d in path.parts for d in SKIP_DIRS):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        lower = text.lower()
        for term in TERMS:
            if term in lower:
                for i, line in enumerate(text.splitlines(), 1):
                    if term in line.lower():
                        rel = path.relative_to(REPO)
                        # 不把命中的字串印出來，只指出位置
                        hits.append(f"{rel}:{i} 出現受限名稱"
                                    f"（第 {TERMS.index(term) + 1} 項）")

    if hits:
        print(f"❌ {len(hits)} 處出現受限的上游名稱：")
        for h in hits:
            print(f"  - {h}")
        print("\n  一律改用 `ref-harness` 指稱。"
              "runtime 專屬設定請由 gen_harness_adapter.py 產到 dist/。")
        return 1

    print(f"✅ 已掃描 {scanned} 個版控中的文字檔，未出現受限名稱")
    return 0


if __name__ == "__main__":
    sys.exit(main())
