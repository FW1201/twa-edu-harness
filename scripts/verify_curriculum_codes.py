#!/usr/bin/env python3
"""驗證 repo 內出現的課綱代碼與敘述，與官方領綱資料一致。

2026-09-05 實測 `tw-edu-lesson-plan-108` 產出的教案，抽驗 10 筆課綱對應：
4 筆代碼根本不存在（前綴寫成 `語-`，正確是 `國-`）、6 筆代碼存在但敘述是編的，
**零筆正確**。而教師會把教案送交課發會。

這道 gate 讓那個狀態無法再出現：只要是已載入領域的代碼，
出現在 repo 任何地方都必須真實存在，附帶的敘述也必須與領綱相符。
尚未載入的領域會列為待查核，不擋 CI（但會提醒）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "python"))

# 素養碼 `國-J-B1` / `國S-U-B1`；學習表現 `5-Ⅳ-2`；學習內容 `Ab-Ⅳ-1`
COMPETENCY_RE = re.compile(r"([一-鿿]{1,3})(S)?-([EJU])-([A-C]\d)")
PERFORMANCE_RE = re.compile(r"(?<![\w-])(\d)-([ⅠⅡⅢⅣⅤ])-(\d+)")
CONTENT_RE = re.compile(r"(?<![\w-])([A-Z][a-z])-([ⅠⅡⅢⅣⅤ])-(\d+)")
# 代碼後接「：敘述」時一併比對
DESC_RE = "：([^」』\"'\\n|]{6,})"

SCAN_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json"}
SKIP = {".git", "dist", ".venv", "node_modules", "__pycache__", "data", "python"}

# 已知會寫錯的科目縮寫。這類錯誤特別危險——正因為前綴是錯的，
# 代碼查不到，反而躲過了「代碼是否存在」的檢查。
KNOWN_WRONG_PREFIX = {"語": "國"}

# 學習表現（`5-Ⅳ-2`）與學習內容（`Ab-Ⅳ-1`）的代碼**不帶領域前綴**，
# 跨領域會撞號——`3-Ⅲ-1` 在國語文不存在，在別的領域可能合法。
# 因此只在明確宣告領域的檔案內比對，其餘只檢查帶前綴的素養碼。
DOMAIN_MARKER = re.compile(r"<!--\s*curriculum-domain:\s*(\S+?)\s*-->")
# 刻意引用錯誤範例的文件（例如記錄實測發現）用這個標記豁免。
# 比對子字串，讓標記後面可以接說明文字。
IGNORE_MARKER = "curriculum-check: ignore"


def scan_files() -> list[Path]:
    return [p for p in REPO.rglob("*")
            if p.is_file() and p.suffix in SCAN_SUFFIXES
            and not any(d in p.parts for d in SKIP)
            and p.name != Path(__file__).name]


def main() -> int:
    try:
        from twa_curriculum import default_store
    except ImportError as exc:
        print(f"❌ 無法匯入 twa_curriculum：{exc}")
        return 1

    store = default_store()
    if not store.domains:
        print("⚠️  data/curriculum/ 沒有資料，略過驗證")
        return 0

    prefixes = {}
    for ind in store.all():
        if ind.kind == "competency":
            prefixes[ind.code.split("-")[0].rstrip("S")] = ind.domain

    errors: list[str] = []
    pending: set[str] = set()
    checked = 0

    for path in sorted(scan_files()):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(REPO)
        if IGNORE_MARKER in text:
            continue
        marked_domain = DOMAIN_MARKER.search(text)

        for m in COMPETENCY_RE.finditer(text):
            head, s_flag, level, item = m.groups()
            if head in KNOWN_WRONG_PREFIX:
                line = text[:m.start()].count("\n") + 1
                right = KNOWN_WRONG_PREFIX[head]
                errors.append(
                    f"{rel}:{line} 科目縮寫錯誤 `{head}-` 應為 `{right}-`"
                    f"（{head}文是領域名，代碼用科目名）")
                continue
            if head not in prefixes:
                pending.add(head)
                continue
            code = f"{head}{'S' if s_flag else ''}-{level}-{item}"
            checked += 1
            if store.get(code) is None:
                line = text[:m.start()].count("\n") + 1
                errors.append(f"{rel}:{line} 代碼 `{code}` 不存在於領綱")

        if not marked_domain:
            continue          # 無領域宣告 → 不比對無前綴的代碼

        for regex, kind in ((PERFORMANCE_RE, "學習表現"), (CONTENT_RE, "學習內容")):
            for m in regex.finditer(text):
                code = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                checked += 1
                if store.get(code) is None:
                    line = text[:m.start()].count("\n") + 1
                    errors.append(f"{rel}:{line} {kind}代碼 `{code}` 不存在於領綱")
                    continue
                # 代碼後緊接敘述時，敘述必須與領綱一致
                tail = re.match(DESC_RE, text[m.end():])
                if tail:
                    claimed = tail.group(1).strip().rstrip("。|").strip()
                    official = store.get(code).description.rstrip("。")
                    if claimed and claimed != official:
                        line = text[:m.start()].count("\n") + 1
                        errors.append(
                            f"{rel}:{line} `{code}` 的敘述與領綱不符\n"
                            f"        寫的是：{claimed[:46]}…\n"
                            f"        領綱是：{official[:46]}…")

    if errors:
        print(f"❌ {len(errors)} 項課綱代碼問題：")
        for e in errors[:25]:
            print(f"  - {e}")
        if len(errors) > 25:
            print(f"  …另有 {len(errors) - 25} 項")
        return 1

    print(f"✅ 已比對 {checked} 處課綱代碼，"
          f"全部與領綱一致（已載入：{', '.join(store.domains)}）")
    if pending:
        print(f"   ⏳ 尚未載入資料、無法查核的領域前綴：{', '.join(sorted(pending))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
