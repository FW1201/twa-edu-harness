"""課綱查詢的正確性測試。

重點不只是「查得到」，更是「查不到的時候會誠實說查不到」。
一個看起來正確但不存在的代碼會被寫進教案送交課發會——
那比一句「查無此代碼」有害得多。
"""
from __future__ import annotations

import pytest

from twa_curriculum import (
    AmbiguousCode,
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
    ind = get_by_code(code, "國語文")
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
    ind = get_by_code(code, "國語文")
    assert ind is not None, f"{code} 應存在"
    assert ind.kind == "content"
    assert ind.description


# ── 反例：不存在的代碼必須回 None，絕不猜測 ──────────────
@pytest.mark.parametrize("code", [
    # 科目縮寫寫錯——這類最危險：前綴錯了、代碼查不到，反而躲過存在性檢查
    "語-J-B1",    # 國語文是「國」不是「語」（實際發生過）
    "語-J-A2",
    "語-E-B1",
    "英-U-B1",    # 英語文高中是 英S-U-B1（含 S），實際發生過
    "自-U-A2",    # 自然科學同上
    "數-U-A3",    # 數學同上
    "國-J-D1",    # 素養項目只有 A/B/C
    "國-K-A1",    # 教育階段只有 E/J/U
    "1-Ⅵ-1",      # 學習階段只有 Ⅰ–Ⅴ
    "1-Ⅳ-999",    # 序號不存在
    "",
    "亂寫",
])
def test_nonexistent_returns_none(code):
    assert get_by_code(code) is None, f"{code} 不該被查到"


@pytest.mark.parametrize("code,absent_from,present_in", [
    ("Da-Ⅳ-1", "國語文", ["社會", "自然科學"]),
    ("7-Ⅳ-1", "國語文", ["英語文"]),
    ("Bd-Ⅱ-1", "國語文", []),
])
def test_code_absent_in_one_domain_may_exist_in_another(
        code, absent_from, present_in):
    """無前綴的代碼只在指定領域內才有意義。

    `Da-Ⅳ-1` 不存在於國語文，但在社會與自然科學都是合法代碼；
    `7-Ⅳ-1` 不存在於國語文（學習表現只有 1–6 類），但英語文有第 7 類。
    這正是查詢必須帶領域的理由。
    """
    assert get_by_code(code, absent_from) is None
    assert default_store().domains_for(code) == sorted(present_in)


def test_verify_reports_invalid():
    result = verify_codes(["國-J-B1", "語-J-B1", "5-Ⅳ-2", "Da-Ⅳ-1"], "國語文")
    assert result["國-J-B1"]["exists"] is True
    assert result["5-Ⅳ-2"]["exists"] is True
    assert result["語-J-B1"]["exists"] is False
    assert result["Da-Ⅳ-1"]["exists"] is False   # 國語文沒有 Da 類別
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
    a, b = get_by_code(latin, "國語文"), get_by_code(unicode_form, "國語文")
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
    assert get_by_code(code, "國語文").description == expected


# ── 查詢 ─────────────────────────────────────────────
@pytest.mark.parametrize("domain", ["國語文", "數學", "社會", "自然科學"])
def test_competencies_per_level(domain):
    for level in ("E", "J", "U"):
        items = list_competencies(domain=domain, level=level)
        assert len(items) == 9, f"{domain} {level} 階段應有三面九項共 9 條"


def test_bd_starts_at_stage_three():
    """議論文本（Bd）在國語文領綱中從第三學習階段才出現。

    這條測試是在寫測試時假設 Bd-Ⅱ-1 存在、結果查無而發現的。
    抽取忠實反映了領綱——不是每個類別都涵蓋全部五個學習階段。
    """
    assert get_by_code("Bd-Ⅱ-1", "國語文") is None
    assert get_by_code("Bd-Ⅲ-1", "國語文") is not None
    stages = {i.stage for i in default_store().all()
              if i.kind == "content" and i.category == "Bd"
              and i.domain == "國語文"}
    assert stages == {"Ⅲ", "Ⅳ", "Ⅴ"}


def test_elective_marker_captured():
    """領綱用 ◎ 標示的項目要保留這個標記。"""
    electives = [i for i in default_store().all() if i.elective]
    assert electives, "應有帶 ◎ 標記的指標"
    assert get_by_code("Bd-Ⅲ-1", "國語文").elective is True


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
    assert store.domains == ["國語文", "數學", "社會", "自然科學", "英語文"]
    assert len(store) > 2000
    kinds = {k: 0 for k in ("competency", "performance", "content")}
    for ind in store.all():
        kinds[ind.kind] += 1
    # 英語文只有 22 條（部分素養項目在該領域不適用），其餘四領域各 27 條
    assert kinds["competency"] == 130
    assert kinds["performance"] > 700
    assert kinds["content"] > 1300


# ── 數學：代碼格式與國語文完全不同 ──────────────────────
@pytest.mark.parametrize("code,kind", [
    ("數-E-A1", "competency"), ("數-J-A2", "competency"),
    ("數S-U-A1", "competency"),
    ("n-Ⅰ-1", "performance"), ("n-Ⅳ-1", "performance"),
    ("s-Ⅰ-1", "performance"), ("a-Ⅳ-1", "performance"),
    ("N-1-1", "content"), ("A-7-1", "content"), ("S-9-1", "content"),
])
def test_math_indicators(code, kind):
    ind = get_by_code(code)
    assert ind is not None, f"{code} 應存在於數學領綱"
    assert ind.kind == kind
    assert ind.domain == "數學"


def test_math_content_uses_grade_not_stage():
    """數學的學習內容用年級數字（N-1-1 是 1 年級），不是學習階段羅馬數字。"""
    ind = get_by_code("N-1-1", "數學")
    assert ind.stage == "1"
    assert ind.level == "E"
    assert get_by_code("A-10-1", "數學").level == "U"


def test_math_performance_roman_tolerance():
    """數學領綱的羅馬數字全用拉丁字母（n-IV-1），儲存時正規化。"""
    assert get_by_code("n-IV-1", "數學") is get_by_code("n-Ⅳ-1", "數學")


# ── 跨領域撞號：最危險的一種錯誤 ──────────────────────────
def test_same_code_different_meaning_across_domains():
    """學習表現與學習內容的代碼不帶領域前綴，跨領域必然撞號。

    `1-Ⅱ-1` 在國語文是「聆聽時能讓對方充分表達意見」、
    在英語文是「能聽辨 26 個字母」。5 個領域中有 268 個代碼重複。
    靜默選一個是最糟的處理——回傳的敘述看起來完全正常，卻屬於另一個領域。
    """
    zh = get_by_code("1-Ⅱ-1", "國語文")
    en = get_by_code("1-Ⅱ-1", "英語文")
    assert zh.description != en.description
    assert "聆聽" in zh.description and "字母" in en.description


def test_ambiguous_code_raises_not_guesses():
    with pytest.raises(AmbiguousCode) as exc:
        get_by_code("1-Ⅱ-1")
    assert set(exc.value.domains) >= {"國語文", "英語文"}


def test_verify_reports_ambiguous_not_silently_picks():
    result = verify_codes(["1-Ⅱ-1"])
    assert result["1-Ⅱ-1"]["ambiguous"] is True
    assert result["1-Ⅱ-1"]["description"] is None
    assert verify_codes(["1-Ⅱ-1"], "英語文")["1-Ⅱ-1"]["exists"] is True


def test_unique_code_still_works_without_domain():
    """只在一個領域出現的代碼，不指定 domain 也查得到。"""
    assert get_by_code("N-1-1").domain == "數學"


@pytest.mark.parametrize("domain,code,kind", [
    ("社會", "社-J-A1", "competency"), ("社會", "Aa-Ⅱ-1", "content"),
    ("自然科學", "自-J-A1", "competency"), ("自然科學", "ah-Ⅱ-1", "performance"),
    ("英語文", "英-J-A1", "competency"), ("英語文", "D-Ⅲ-3", "content"),
])
def test_other_domains(domain, code, kind):
    ind = get_by_code(code, domain)
    assert ind is not None, f"{domain} 的 {code} 應存在"
    assert ind.kind == kind and ind.domain == domain


def test_cross_page_continuation_joined():
    """跨頁截斷的敘述要被接回完整。"""
    ind = get_by_code("D-Ⅲ-3", "英語文")
    assert ind.description == "依綜合資訊作簡易猜測。"


def test_domains_are_isolated():
    """不同領域的代碼不該互相汙染。"""
    assert get_by_code("國-J-B1").domain == "國語文"
    assert get_by_code("數-J-B1").domain == "數學"
    assert get_by_code("N-1-1").domain == "數學"


def test_every_indicator_has_description():
    empty = [i.code for i in default_store().all() if not i.description.strip()]
    assert not empty, f"以下指標沒有敘述：{empty[:10]}"


def test_level_derived_from_stage():
    """階段 → 教育階段的推導要一致。

    兩種階段表示法並存：國語文用學習階段羅馬數字，
    數學的學習內容用年級數字（1–12）。
    """
    roman = {"Ⅰ": "E", "Ⅱ": "E", "Ⅲ": "E", "Ⅳ": "J", "Ⅴ": "U"}
    grade = {**{str(g): "E" for g in range(1, 7)},
             **{str(g): "J" for g in range(7, 10)},
             **{str(g): "U" for g in range(10, 13)}}
    for ind in default_store().all():
        if not ind.stage:
            continue
        expected = roman.get(ind.stage) or grade.get(ind.stage)
        assert expected is not None, f"{ind.code} 的階段 `{ind.stage}` 無法對應"
        assert ind.level == expected, ind.code
