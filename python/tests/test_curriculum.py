"""課綱查詢的正確性測試。

重點不只是「查得到」，更是「查不到的時候會誠實說查不到」。
一個看起來正確但不存在的代碼會被寫進教案送交課發會——
那比一句「查無此代碼」有害得多。
"""
from __future__ import annotations

import pytest

from twa_curriculum import (
    default_store,
    get_by_code,
    list_competencies,
    lookup,
    verify_codes,
)
from twa_curriculum.store import normalize_code


# ── 核心素養：三面九項 × 三教育階段 ─────────────────────
@pytest.mark.parametrize("code", [
    "國-E-A1", "國-E-A2", "國-E-A3", "國-E-B1", "國-E-B2", "國-E-B3",
    "國-E-C1", "國-E-C2", "國-E-C3",
    "國-J-A1", "國-J-A2", "國-J-A3", "國-J-B1", "國-J-B2", "國-J-B3",
    "國-J-C1", "國-J-C2", "國-J-C3",
    "國S-U-A1", "國S-U-B1", "國S-U-C1",
])
def test_competency_exists(code):
    ind = get_by_code(code)
    assert ind is not None, f"{code} 應存在於國語文領綱"
    assert ind.kind == "competency"
    assert ind.domain == "國語文"
    assert len(ind.description) > 10


# ── 學習表現：六大類別 × 五學習階段 ─────────────────────
@pytest.mark.parametrize("code", [
    "1-Ⅰ-1", "1-Ⅱ-1", "1-Ⅲ-1", "1-Ⅳ-1", "1-Ⅴ-1",   # 聆聽
    "2-Ⅰ-1", "2-Ⅳ-1", "2-Ⅴ-1",                      # 口語表達
    "3-Ⅰ-1", "3-Ⅱ-1",                                # 標音符號
    "4-Ⅰ-1", "4-Ⅱ-1", "4-Ⅳ-1",                      # 識字與寫字
    "5-Ⅰ-1", "5-Ⅳ-2", "5-Ⅴ-1",                      # 閱讀
    "6-Ⅰ-1", "6-Ⅳ-2", "6-Ⅴ-1",                      # 寫作
])
def test_performance_exists(code):
    ind = get_by_code(code)
    assert ind is not None, f"{code} 應存在"
    assert ind.kind == "performance"
    assert ind.description


# ── 學習內容：文字篇章 / 文本表述 / 文化內涵 ─────────────
@pytest.mark.parametrize("code", [
    "Aa-Ⅰ-1", "Ab-Ⅱ-1", "Ab-Ⅳ-1", "Ac-Ⅰ-1", "Ad-Ⅰ-1",
    "Ba-Ⅰ-1", "Bb-Ⅰ-1", "Bc-Ⅱ-1", "Bd-Ⅲ-1", "Be-Ⅰ-1",
    "Ca-Ⅰ-1", "Cb-Ⅰ-1", "Cc-Ⅱ-1",
])
def test_content_exists(code):
    ind = get_by_code(code)
    assert ind is not None, f"{code} 應存在"
    assert ind.kind == "content"
    assert ind.description


# ── 反例：不存在的代碼必須回 None，絕不猜測 ──────────────
@pytest.mark.parametrize("code", [
    "語-J-B1",    # 前綴錯誤：國語文是「國」不是「語」（實際發生過的錯誤）
    "語-J-A2",
    "語-E-B1",
    "Da-Ⅳ-1",     # 類別 Da 不存在於國語文
    "國-J-D1",    # 素養項目只有 A/B/C
    "國-K-A1",    # 教育階段只有 E/J/U
    "7-Ⅳ-1",      # 學習表現只有 1–6 類
    "1-Ⅵ-1",      # 學習階段只有 Ⅰ–Ⅴ
    "1-Ⅳ-999",    # 序號不存在
    "數-J-A1",    # 其他領域尚未載入
    "",
    "亂寫",
])
def test_nonexistent_returns_none(code):
    assert get_by_code(code) is None, f"{code} 不該被查到"


def test_verify_reports_invalid():
    result = verify_codes(["國-J-B1", "語-J-B1", "5-Ⅳ-2", "Da-Ⅳ-1"])
    assert result["國-J-B1"]["exists"] is True
    assert result["5-Ⅳ-2"]["exists"] is True
    assert result["語-J-B1"]["exists"] is False
    assert result["Da-Ⅳ-1"]["exists"] is False
    assert result["語-J-B1"]["description"] is None


# ── 羅馬數字混用：兩種寫法要指向同一筆 ───────────────────
@pytest.mark.parametrize("latin,unicode_form", [
    ("5-IV-2", "5-Ⅳ-2"),
    ("1-I-1", "1-Ⅰ-1"),
    ("2-V-1", "2-Ⅴ-1"),
    ("Ab-IV-1", "Ab-Ⅳ-1"),
    ("Ac-I-1", "Ac-Ⅰ-1"),
])
def test_roman_numeral_tolerance(latin, unicode_form):
    a, b = get_by_code(latin), get_by_code(unicode_form)
    assert a is not None and b is not None
    assert a.code == b.code == unicode_form


def test_normalize_code_idempotent():
    for code in ("5-Ⅳ-2", "5-IV-2", " 5-IV-2 "):
        assert normalize_code(code) == "5-Ⅳ-2"


# ── 敘述必須是領綱原文，不能被改寫 ───────────────────────
@pytest.mark.parametrize("code,expected", [
    ("5-Ⅳ-2", "理解各類文本的句子、段落與主要概念，指出寫作的目的與觀點。"),
    ("Ab-Ⅳ-1", "4,000個常用字的字形、字音和字義。"),
    ("Ac-Ⅰ-1", "常用標點符號。"),
])
def test_description_matches_official(code, expected):
    assert get_by_code(code).description == expected


# ── 查詢 ─────────────────────────────────────────────
def test_competencies_per_level():
    for level in ("E", "J", "U"):
        items = list_competencies(domain="國語文", level=level)
        assert len(items) == 9, f"{level} 階段應有三面九項共 9 條"


def test_bd_starts_at_stage_three():
    """議論文本（Bd）在國語文領綱中從第三學習階段才出現。

    這條測試是在寫測試時假設 Bd-Ⅱ-1 存在、結果查無而發現的。
    抽取忠實反映了領綱——不是每個類別都涵蓋全部五個學習階段。
    """
    assert get_by_code("Bd-Ⅱ-1") is None
    assert get_by_code("Bd-Ⅲ-1") is not None
    stages = {i.stage for i in default_store().all()
              if i.kind == "content" and i.category == "Bd"}
    assert stages == {"Ⅲ", "Ⅳ", "Ⅴ"}


def test_elective_marker_captured():
    """領綱用 ◎ 標示的項目要保留這個標記。"""
    electives = [i for i in default_store().all() if i.elective]
    assert electives, "應有帶 ◎ 標記的指標"
    assert get_by_code("Bd-Ⅲ-1").elective is True


def test_lookup_by_keyword():
    results = lookup(domain="國語文", kind="performance", keyword="聆聽")
    assert results
    assert all("聆聽" in r.description for r in results)


def test_lookup_level_filter():
    results = lookup(domain="國語文", level="J", kind="performance", limit=1000)
    assert results
    assert all(r.level == "J" for r in results)


def test_lookup_limit():
    assert len(lookup(domain="國語文", limit=5)) == 5


def test_store_totals():
    store = default_store()
    assert store.domains == ["國語文"]
    assert len(store) > 300
    kinds = {k: 0 for k in ("competency", "performance", "content")}
    for ind in store.all():
        kinds[ind.kind] += 1
    assert kinds["competency"] == 27      # 9 項 × 3 階段
    assert kinds["performance"] > 150
    assert kinds["content"] > 150


def test_every_indicator_has_description():
    empty = [i.code for i in default_store().all() if not i.description.strip()]
    assert not empty, f"以下指標沒有敘述：{empty[:10]}"


def test_level_derived_from_stage():
    mapping = {"Ⅰ": "E", "Ⅱ": "E", "Ⅲ": "E", "Ⅳ": "J", "Ⅴ": "U"}
    for ind in default_store().all():
        if ind.stage:
            assert ind.level == mapping[ind.stage], ind.code
