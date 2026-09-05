"""課綱資料的載入與查詢。"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "curriculum"

# PDF 與使用者輸入都可能混用拉丁字母與 Unicode 羅馬數字。
# 查詢時一律正規化，讓 `5-IV-2` 與 `5-Ⅳ-2` 指向同一筆。
_ROMAN = {"I": "Ⅰ", "II": "Ⅱ", "III": "Ⅲ", "IV": "Ⅳ", "V": "Ⅴ"}
_CODE_RE = re.compile(r"^(.+?)-([ⅠⅡⅢⅣⅤIVX]+)-(\d+)$")

LEVELS = ("E", "J", "U")


def normalize_code(code: str) -> str:
    """把代碼中的羅馬數字統一為 Unicode 形式，並去除空白。"""
    code = unicodedata.normalize("NFKC", code).strip().replace(" ", "")
    m = _CODE_RE.match(code)
    if not m:
        return code
    head, roman, num = m.groups()
    return f"{head}-{_ROMAN.get(roman.upper(), roman)}-{num}"


@dataclass(frozen=True)
class Indicator:
    code: str
    kind: str            # competency | performance | content
    domain: str
    description: str
    level: str = ""
    stage: str = ""
    stage_label: str = ""
    category: str = ""
    elective: bool = False
    extra: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_raw(cls, raw: dict) -> "Indicator":
        known = {"code", "kind", "domain", "description", "level", "stage",
                 "stageLabel", "category", "elective"}
        return cls(
            code=raw["code"], kind=raw["kind"], domain=raw["domain"],
            description=raw.get("description", ""),
            level=raw.get("level", ""), stage=raw.get("stage", ""),
            stage_label=raw.get("stageLabel", ""),
            category=raw.get("category", ""),
            elective=bool(raw.get("elective", False)),
            extra={k: v for k, v in raw.items() if k not in known},
        )

    def as_dict(self) -> dict:
        d = {"code": self.code, "kind": self.kind, "domain": self.domain,
             "description": self.description}
        for key, val in (("level", self.level), ("stage", self.stage),
                         ("stageLabel", self.stage_label),
                         ("category", self.category)):
            if val:
                d[key] = val
        if self.elective:
            d["elective"] = True
        d.update(self.extra)
        return d


class CurriculumStore:
    """載入 data/curriculum/*.json 並提供查詢。"""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = Path(data_dir or DATA_DIR)
        self._by_code: dict[str, Indicator] = {}
        self._domains: dict[str, str] = {}   # 領域名 → 前綴
        self._load()

    def _load(self) -> None:
        if not self.data_dir.is_dir():
            return
        for path in sorted(self.data_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self._domains[payload["domain"]] = payload["prefix"]
            for bucket in ("competencies", "performance", "content"):
                for raw in (payload.get(bucket) or {}).values():
                    ind = Indicator.from_raw(raw)
                    self._by_code[normalize_code(ind.code)] = ind

    # ── 查詢 ────────────────────────────────────────────
    @property
    def domains(self) -> list[str]:
        return sorted(self._domains)

    def __len__(self) -> int:
        return len(self._by_code)

    def get(self, code: str) -> Indicator | None:
        """依代碼取得單一指標。查不到回 None——不猜測、不生成。"""
        return self._by_code.get(normalize_code(code))

    def all(self) -> Iterable[Indicator]:
        return self._by_code.values()

    def search(self, domain: str | None = None, level: str | None = None,
               kind: str | None = None, keyword: str | None = None,
               limit: int = 20) -> list[Indicator]:
        """依領域、教育階段、類型與關鍵詞查詢。"""
        results = []
        for ind in self._by_code.values():
            if domain and ind.domain != domain:
                continue
            if level and ind.level != level.upper():
                continue
            if kind and ind.kind != kind:
                continue
            if keyword and keyword not in ind.description:
                continue
            results.append(ind)
        results.sort(key=lambda i: (i.kind, i.code))
        return results[:limit]

    def competencies(self, domain: str | None = None,
                     level: str | None = None) -> list[Indicator]:
        return self.search(domain=domain, level=level,
                           kind="competency", limit=1000)

    def verify(self, codes: Iterable[str]) -> dict[str, dict]:
        """批次查核。回傳每個代碼的存在與否與官方敘述。

        給技能在產出前自我檢查用——寫進教案的每一個代碼都應該先過這一關。
        """
        out: dict[str, dict] = {}
        for code in codes:
            ind = self.get(code)
            out[code] = ({"exists": False, "description": None,
                          "hint": "此代碼不存在於已載入的領綱資料中"}
                         if ind is None else
                         {"exists": True, "description": ind.description,
                          "domain": ind.domain, "kind": ind.kind,
                          "level": ind.level})
        return out


@lru_cache(maxsize=1)
def default_store() -> CurriculumStore:
    return CurriculumStore()


def lookup(domain: str | None = None, level: str | None = None,
           kind: str | None = None, keyword: str | None = None,
           limit: int = 20) -> list[Indicator]:
    return default_store().search(domain, level, kind, keyword, limit)


def get_by_code(code: str) -> Indicator | None:
    return default_store().get(code)


def list_competencies(domain: str | None = None,
                      level: str | None = None) -> list[Indicator]:
    return default_store().competencies(domain, level)


def verify_codes(codes: Iterable[str]) -> dict[str, dict]:
    return default_store().verify(codes)
