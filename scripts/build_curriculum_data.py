#!/usr/bin/env python3
# <!-- curriculum-check: ignore：docstring 記錄的是修正前的錯誤範例 -->
"""從教育部領綱 PDF 建立結構化的 108 課綱指標資料。

為什麼要做這件事：技能原本把課綱代碼放在 references/ 的 markdown 裡，
由模型讀進 context 再寫出來。沒有任何方式能驗證代碼是否真的存在——
而實測發現，`tw-edu-lesson-plan-108` 產出的教案寫著 `語-J-B1`、`語-J-A2`，
**這些代碼在領綱中根本不存在**（正確前綴是 `國-`）。
教師會把這份教案送交課發會。

用法：
    python scripts/build_curriculum_data.py \\
        --pdf <path> --profile data/curriculum/profiles/國.yml

每個領域的代碼格式與 PDF 版面都不同，因此抽取設定放在 profile 檔案裡，
不寫死在腳本中。國語文可逐行抽取；數學的學習內容是五欄表格且代碼垂直置中，
逐行會截斷 40% 的敘述，必須走表格。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# PDF 中羅馬數字混用：Ⅰ(U+2160) 與拉丁 I、Ⅴ 與 V、Ⅳ 與 IV 都出現過。
# 統一正規化為 Unicode 羅馬數字。
ROMAN_NORMALIZE = {
    "III": "Ⅲ", "IV": "Ⅳ", "II": "Ⅱ", "I": "Ⅰ", "V": "Ⅴ",
    "Ⅰ": "Ⅰ", "Ⅱ": "Ⅱ", "Ⅲ": "Ⅲ", "Ⅳ": "Ⅳ", "Ⅴ": "Ⅴ",
}
# 學習階段 → 教育階段代碼
STAGE_TO_LEVEL = {"Ⅰ": "E", "Ⅱ": "E", "Ⅲ": "E", "Ⅳ": "J", "Ⅴ": "U"}
STAGE_LABEL = {
    "Ⅰ": "第一學習階段（國小 1–2 年級）",
    "Ⅱ": "第二學習階段（國小 3–4 年級）",
    "Ⅲ": "第三學習階段（國小 5–6 年級）",
    "Ⅳ": "第四學習階段（國中 7–9 年級）",
    "Ⅴ": "第五學習階段（高中 10–12 年級）",
}

# 年級數字 → 教育階段（數學的學習內容用年級而非學習階段）
GRADE_TO_LEVEL = {**{g: "E" for g in range(1, 7)},
                  **{g: "J" for g in range(7, 10)},
                  **{g: "U" for g in range(10, 13)}}
GRADE_LABEL = {g: f"{g} 年級" for g in range(1, 13)}

PERFORMANCE_RE = re.compile(r"^(?:◎)?(\d+)-([ⅠⅡⅢⅣⅤIV]+)-(\d+)\s*(.*)$")
CONTENT_RE = re.compile(r"^(?:◎)?([A-Z][a-z]?)-([ⅠⅡⅢⅣⅤIV]+)-(\d+)\s*(.*)$")
# 兩種寫法都要吃：`國-E-A1`（國中小）與 `國 S-U-A1`（高中，PDF 版面會插入空白）
COMPETENCY_RE = re.compile(r"^([一-鿿]+)\s*(S)?-([EJU])-([A-C]\d)\s*(.*)$", re.S)
STAGE_LABEL_RE = re.compile(r"^第[一二三四五]學習階段\s*")
PAGE_NUM_RE = re.compile(r"^\d{1,3}$")


def norm_roman(s: str) -> str | None:
    return ROMAN_NORMALIZE.get(s.upper()) or ROMAN_NORMALIZE.get(s)


# PDF 的分散對齊會在中文字之間插入空白（「從 中 培 養 道 德觀」）。
# 兩側都是 CJK 時的空白一律移除；中英之間的空白保留。
_CJK_SPACE_RE = re.compile(r"(?<=[\u3000-\u9fff\uff00-\uffef])\s+(?=[\u3000-\u9fff\uff00-\uffef])")


def clean(text: str) -> str:
    text = " ".join(text.replace("\n", "").split())
    prev = None
    while prev != text:                 # 連續空白需要多次收斂
        prev, text = text, _CJK_SPACE_RE.sub("", text)
    return text


def parse_indicators(pages: list[str], pattern: re.Pattern,
                     kind: str, domain: str, prefix: str) -> dict:
    """逐行解析指標。描述會跨行，因此以「下一行是否為新代碼」判斷段落結束。"""
    out: dict[str, dict] = {}
    current: str | None = None

    for text in pages:
        for raw in text.split("\n"):
            line = STAGE_LABEL_RE.sub("", raw.strip())
            if not line or PAGE_NUM_RE.match(line):
                continue

            m = pattern.match(line)
            if m:
                head, roman, num, desc = m.groups()
                stage = norm_roman(roman)
                if stage is None:
                    continue
                code = f"{head}-{stage}-{num}"
                if code in out:          # 目次或附錄的重複出現
                    current = code if not out[code]["description"] else None
                    continue
                out[code] = {
                    "code": code,
                    "kind": kind,
                    "domain": domain,
                    "stage": stage,
                    "stageLabel": STAGE_LABEL[stage],
                    "level": STAGE_TO_LEVEL[stage],
                    "category": head,
                    "description": desc.strip(),
                    "elective": raw.strip().startswith("◎"),
                }
                current = code
            elif current and out[current]["description"] and not out[current]["description"].endswith("。"):
                # 續行：只有在前一段尚未以句號結束時才接續，避免吃到表頭
                if not any(k in line for k in ("學習階段", "學習表現", "學習內容")):
                    out[current]["description"] += line
            else:
                current = None

    for v in out.values():
        v["description"] = clean(v["description"])
    return out


def parse_from_tables(tables, pattern: re.Pattern, kind: str,
                      domain: str) -> dict:
    """從多欄表格抽取指標。

    數學的學習內容是五欄表（編碼／條目說明／備註／參考教具／對應學習表現），
    代碼儲存格垂直置中。逐行文字抽取會把 40% 的敘述截斷成半句——
    實測 `n-II-6` 只會抓到「義，並應用於…」這樣的後半句。
    """
    out: dict[str, dict] = {}
    for table in tables:
        for row in table:
            cells = [(c or "").strip() for c in row]
            if len(cells) < 2:
                continue
            raw_code = cells[0].replace("\n", "").strip()
            m = pattern.match(raw_code.lstrip("◎"))
            if not m:
                continue
            head, mid, num = m.group(1), m.group(2), m.group(3)
            stage = norm_roman(mid)
            if stage:
                level, label = STAGE_TO_LEVEL[stage], STAGE_LABEL[stage]
            elif mid.isdigit() and int(mid) in GRADE_TO_LEVEL:
                stage, level = mid, GRADE_TO_LEVEL[int(mid)]
                label = GRADE_LABEL[int(mid)]
            else:
                continue
            code = f"{head}-{stage}-{num}"
            desc = clean(cells[1])
            if not desc or code in out:
                continue
            out[code] = {
                "code": code, "kind": kind, "domain": domain,
                "stage": stage, "stageLabel": label, "level": level,
                "category": head, "description": desc,
                "elective": raw_code.startswith("◎"),
            }
    return out


def parse_competencies(tables: list[list[list[str]]], domain: str,
                       prefix: str) -> dict:
    """核心素養在 PDF 中是多欄表格，用表格抽取比純文字可靠。"""
    out: dict[str, dict] = {}
    for table in tables:
        for row in table:
            cells = [c or "" for c in row]
            if len(cells) < 6:
                continue
            item = clean(cells[1])          # 例如「A1 身心素質與自我精進」
            general = clean(cells[2])       # 總綱項目說明
            for cell in cells[3:6]:
                text = (cell or "").strip()
                m = COMPETENCY_RE.match(text)
                if not m:
                    continue
                head, s_flag, level, item_code, desc = m.groups()
                code = (f"{head}{'S' if s_flag else ''}-{level}-{item_code}"
                        if s_flag else f"{head}-{level}-{item_code}")
                if code in out:
                    continue
                out[code] = {
                    "code": code,
                    "kind": "competency",
                    "domain": domain,
                    "level": level,
                    "item": item_code,
                    "itemLabel": item,
                    "generalDescription": general,
                    "description": clean(desc),
                }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--profile", required=True,
                    help="data/curriculum/profiles/<prefix>.yml")
    ap.add_argument("--out", default="data/curriculum")
    args = ap.parse_args()

    import yaml
    profile = yaml.safe_load(Path(args.profile).read_text(encoding="utf-8"))
    domain, prefix = profile["domain"], profile["prefix"]
    strategy = profile.get("strategy", "lines")
    perf_re = re.compile(profile["patterns"]["performance"])
    cont_re = re.compile(profile["patterns"]["content"])

    try:
        import pdfplumber
    except ImportError:
        print("❌ 需要 pdfplumber：pip install pdfplumber")
        return 1

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"❌ 找不到 {pdf_path}")
        return 1

    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
        tables = [t for p in pdf.pages for t in p.extract_tables()]

    if strategy == "tables":
        perf = parse_from_tables(tables, perf_re, "performance", domain)
        cont = parse_from_tables(tables, cont_re, "content", domain)
    else:
        perf = parse_indicators(pages, perf_re, "performance", domain, prefix)
        cont = parse_indicators(pages, cont_re, "content", domain, prefix)
        # 逐行模式下，學習內容代碼不該以數字開頭（那是學習表現）
        cont = {k: v for k, v in cont.items() if not k[0].isdigit()}
    comp = parse_competencies(tables, domain, prefix)

    out_dir = REPO / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "domain": domain,
        "prefix": prefix,
        "source": pdf_path.name,
        "competencies": dict(sorted(comp.items())),
        "performance": dict(sorted(perf.items())),
        "content": dict(sorted(cont.items())),
    }
    target = out_dir / f"{prefix}.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")

    print(f"✅ {target.relative_to(REPO)}")
    print(f"   核心素養 {len(comp):3d} 條")
    print(f"   學習表現 {len(perf):3d} 條")
    print(f"   學習內容 {len(cont):3d} 條")

    # ── 完整性檢查 ───────────────────────────────────
    # 抽取「成功但不完整」是最危險的結果：資料看起來正常，實際少了一半，
    # 而使用者無從察覺。英語文就是這樣——學習表現漏了 42/282、
    # 學習內容的四欄並排表只抓到 28%，因此未納入。
    full_text = "\n".join(pages)
    problems = []
    for label, regex, got in (("學習表現", perf_re, perf), ("學習內容", cont_re, cont)):
        loose = re.compile(regex.pattern.lstrip("^").replace("\\s*(.*)$", "")
                           .replace("$", ""))
        in_pdf = set()
        for m in loose.finditer(full_text):
            stage = norm_roman(m.group(2)) or m.group(2)
            in_pdf.add(f"{m.group(1)}-{stage}-{m.group(3)}")
        missing = in_pdf - set(got)
        if missing:
            problems.append(
                f"{label}：PDF 中有 {len(in_pdf)} 個代碼，只抽出 {len(got)}，"
                f"漏 {len(missing)} 個（例如 {sorted(missing)[:4]}）")

    if problems:
        print("\n❌ 抽取不完整，**不要使用這份資料**：")
        for prob in problems:
            print(f"   - {prob}")
        print("   請調整 profile 的抽取策略（lines / tables）或代碼樣式後重跑。")
        target.unlink(missing_ok=True)
        return 1

    print("   ✅ 完整性檢查通過：PDF 中的代碼全部抽出")
    return 0


if __name__ == "__main__":
    sys.exit(main())
