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


def parse_from_split_cells(tables, pattern: re.Pattern, kind: str,
                           domain: str, allow_short: set[str] | None = None) -> dict:
    """表格抽取 + 儲存格內依代碼切分。

    這些領域的指標表是「依學習階段並排」的多欄表，有兩種儲存格形態：

    A. **一格多筆**（社會、自然科學、英語文）：代碼與敘述在同一格，
       多筆指標接連排列。整格當一筆會得到合併亂碼，逐行則被欄位交錯打散。
       做法是依代碼出現位置切段。
    B. **代碼獨立一格**（健康與體育的第五學習階段）：整格只有代碼，
       敘述在同一列的後續儲存格。
    """
    out: dict[str, dict] = {}

    def record(m, desc: str, prefix_text: str) -> None:
        stage = norm_roman(m.group(2))
        if stage is None:
            return
        code = f"{m.group(1).replace(' ', '')}-{stage}-{m.group(3)}"
        # 短片段通常是雜訊，但跨頁截斷的前半段也會很短——
        # 已在 profile 宣告續接的代碼豁免此門檻。
        min_len = 1 if (allow_short and code in allow_short) else 4
        if code in out or len(desc) < min_len:
            return
        out[code] = {
            "code": code, "kind": kind, "domain": domain,
            "stage": stage, "stageLabel": STAGE_LABEL[stage],
            "level": STAGE_TO_LEVEL[stage],
            "category": m.group(1), "description": desc,
            "elective": "◎" in prefix_text or "*" in prefix_text,
        }

    for table in tables:
        for row in table:
            cells = [c or "" for c in row]
            for ci, cell in enumerate(cells):
                matches = list(pattern.finditer(cell)) if cell else []
                if not matches:
                    continue
                only_code = clean(pattern.sub("", cell)) == ""

                for i, m in enumerate(matches):
                    prefix_text = cell[max(0, m.start() - 2):m.start()]
                    if only_code:
                        # 形態 B：往同列後方找第一個有內容且不是代碼的儲存格
                        desc = ""
                        for later in cells[ci + 1:]:
                            candidate = clean(later)
                            if candidate and not pattern.fullmatch(candidate):
                                desc = candidate
                                break
                        record(m, desc, prefix_text)
                    else:
                        # 形態 A：切到下一個代碼為止
                        stop = (matches[i + 1].start()
                                if i + 1 < len(matches) else len(cell))
                        record(m, clean(cell[m.end():stop]), prefix_text)
    return out


def parse_competencies(tables: list[list[list[str]]], domain: str,
                       prefix: str) -> dict:
    """核心素養在 PDF 中是多欄表格，用表格抽取比純文字可靠。

    素養列可能被頁面切斷：前一頁只留下代碼，敘述在下一頁續表的同一欄位。
    因此先記下「有代碼但沒敘述」的位置，再從後續表格的相同欄位補上。
    """
    out: dict[str, dict] = {}
    # (欄索引) → 等待敘述的代碼清單
    pending_cols: dict[int, list[str]] = {}

    for table in tables:
        for row in table:
            cells = [c or "" for c in row]
            # 續表的資料列：無代碼但有敘述 → 補給上一頁待補的同欄位代碼
            if pending_cols and not any(COMPETENCY_RE.match(c.strip())
                                        for c in cells):
                # 續表會重複表頭兩列（「…核心素養具體內涵」「國民中學教育(J)」），
                # 那不是敘述，要跳過。
                joined = clean(" ".join(cells))
                if any(h in joined for h in
                       ("核心素養具體內涵", "教育階段", "國民小學教育",
                        "國民中學教育", "高級中等學校教育", "總綱核心素養")):
                    continue
                for col, codes in list(pending_cols.items()):
                    if col < len(cells) and clean(cells[col]):
                        for code in codes:
                            if not out[code]["description"]:
                                out[code]["description"] = clean(cells[col])
                                out[code]["note"] = "敘述跨頁，由續表同欄位補上"
                        pending_cols.pop(col, None)

        for row in table:
            cells = [c or "" for c in row]
            # 一般領域是 6 欄（面向／項目／總綱說明／E／J／S-U），
            # 但科技從國中才開始，沒有國小欄，只有 5 欄。
            if len(cells) < 5:
                continue
            item = clean(cells[1])          # 例如「A1 身心素質與自我精進」
            general = clean(cells[2])       # 總綱項目說明
            for col_offset, cell in enumerate(cells[3:]):
                text = (cell or "").strip()
                m = COMPETENCY_RE.match(text)
                if not m:
                    continue
                head, s_flag, level, item_code, desc = m.groups()
                code = (f"{head}{'S' if s_flag else ''}-{level}-{item_code}"
                        if s_flag else f"{head}-{level}-{item_code}")
                if code in out:
                    continue
                cleaned = clean(desc)
                out[code] = {
                    "code": code,
                    "kind": "competency",
                    "domain": domain,
                    "level": level,
                    "item": item_code,
                    "itemLabel": item,
                    "generalDescription": general,
                    "description": cleaned,
                }
                if not cleaned:
                    pending_cols.setdefault(3 + col_offset, []).append(code)
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
    # profile 檔名必須等於 prefix，否則產出的 <prefix>.json 會對不上設定檔，
    # 日後重建時容易拿錯 profile。
    if Path(args.profile).stem != prefix:
        print(f"❌ profile 檔名 `{Path(args.profile).stem}` 與 prefix `{prefix}` 不符")
        return 1
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

    continuations = profile.get("continuations") or {}

    if strategy == "tables":
        perf = parse_from_tables(tables, perf_re, "performance", domain)
        cont = parse_from_tables(tables, cont_re, "content", domain)
    elif strategy == "tables-split":
        short_ok = set(continuations)
        perf = parse_from_split_cells(tables, perf_re, "performance",
                                      domain, short_ok)
        cont = parse_from_split_cells(tables, cont_re, "content",
                                      domain, short_ok)
    else:
        perf = parse_indicators(pages, perf_re, "performance", domain, prefix)
        cont = parse_indicators(pages, cont_re, "content", domain, prefix)
        # 逐行模式下，學習內容代碼不該以數字開頭（那是學習表現）
        cont = {k: v for k, v in cont.items() if not k[0].isdigit()}
    # pdfplumber 的表格辨識偶爾會漏掉一小段（科技領綱有一列如此）。
    # 對這些代碼做逐行補抓，但**只接受敘述看起來完整的行**（以句號結尾），
    # 避免把跨行截斷的半句當成完整敘述。
    if profile.get("lineFallback"):
        for label, regex, bucket in (("performance", perf_re, perf),
                                     ("content", cont_re, cont)):
            line_re = re.compile(regex.pattern + r"\s*(.+)")
            for page_text in pages:
                for line in page_text.split("\n"):
                    # 代碼未必在行首（PDF 會把左側欄位文字併進同一行），
                    # 因此用 search；完整性由「敘述須以句號結尾」把關。
                    m = line_re.search(line.strip())
                    if not m:
                        continue
                    stage = norm_roman(m.group(2))
                    if stage is None:
                        continue
                    code = f"{m.group(1).replace(' ', '')}-{stage}-{m.group(3)}"
                    desc = clean(m.group(4))
                    if code in bucket or not desc.endswith("。"):
                        continue
                    bucket[code] = {
                        "code": code, "kind": label, "domain": domain,
                        "stage": stage, "stageLabel": STAGE_LABEL[stage],
                        "level": STAGE_TO_LEVEL[stage],
                        "category": m.group(1).replace(" ", ""),
                        "description": desc, "elective": False,
                        "note": "表格辨識遺漏，由逐行補抓（敘述完整、以句號結尾）",
                    }

    comp = parse_competencies(tables, domain, prefix)

    # 跨頁截斷：表格儲存格被頁面切斷時，後半段落在下一頁的續表。
    # profile 以 `continuations` 明確宣告要接上的後半段，並註明來源頁碼——
    # 這是把抽取器已經看到的兩個片段接起來，不是憑空補字。
    for code, tail in continuations.items():
        for bucket in (perf, cont):
            if code in bucket:
                bucket[code]["description"] = clean(
                    bucket[code]["description"] + tail["text"])
                bucket[code]["note"] = (
                    f"敘述跨頁（{tail['source']}），由 profile 的 continuations 接續")

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
    # 完整性檢查要與抽取器讀同一個來源：走表格的策略就掃表格儲存格，
    # 走逐行的才掃整頁文字。否則內文裡「以家 Aa-V-1 為例」這種解說會被
    # 當成漏抓的指標，而真正的遺漏反而被雜訊淹沒。
    if strategy in ("tables", "tables-split"):
        full_text = "\n".join(
            cell for tb in tables for row in tb for cell in row if cell)
    else:
        full_text = "\n".join(pages)
    problems = []
    for label, regex, got in (("學習表現", perf_re, perf), ("學習內容", cont_re, cont)):
        loose = re.compile(regex.pattern.lstrip("^").replace("\\s*(.*)$", "")
                           .replace("$", ""))
        in_pdf = set()
        for m in loose.finditer(full_text):
            stage = norm_roman(m.group(2)) or m.group(2)
            head = m.group(1).replace(" ", "")   # 「家 Aa」→「家Aa」
            in_pdf.add(f"{head}-{stage}-{m.group(3)}")
        missing = in_pdf - set(got)
        if missing:
            problems.append(
                f"{label}：PDF 中有 {len(in_pdf)} 個代碼，只抽出 {len(got)}，"
                f"漏 {len(missing)} 個（例如 {sorted(missing)[:4]}）")

    # 表格之外還看得到、但沒進最終資料的代碼——不擋，但一定要說出來，
    # 否則「檢查通過」會掩蓋真實的遺漏。
    page_text = "\n".join(pages)
    leftovers: set[str] = set()
    for regex, got in ((perf_re, perf), (cont_re, cont)):
        loose = re.compile(regex.pattern.lstrip("^").replace("\\s*(.*)$", "")
                           .replace("$", ""))
        for m in loose.finditer(page_text):
            stage = norm_roman(m.group(2)) or m.group(2)
            head = m.group(1).replace(" ", "")
            code = f"{head}-{stage}-{m.group(3)}"
            if code in got:
                continue
            # 去掉中文前綴後若代碼已存在，代表這個「前綴」其實是被欄位切斷的
            # 內文尾字（「日常生」＋「Bc-Ⅱ-1」→ 假的「生Bc-Ⅱ-1」）。
            bare = re.sub(r"^[\u4e00-\u9fff]", "", head)
            if bare != head and f"{bare}-{stage}-{m.group(3)}" in got:
                continue
            leftovers.add(code)

    if problems:
        print("\n❌ 抽取不完整，**不要使用這份資料**：")
        for prob in problems:
            print(f"   - {prob}")
        print("   請調整 profile 的抽取策略（lines / tables）或代碼樣式後重跑。")
        target.unlink(missing_ok=True)
        return 1

    print("   ✅ 完整性檢查通過：指標表中的代碼全部抽出")
    if leftovers:
        print(f"   ⚠️  另有 {len(leftovers)} 個代碼出現在頁面文字但不在最終資料中，"
              f"請人工確認是內文舉例還是漏抓：")
        for code in sorted(leftovers)[:8]:
            print(f"        {code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
