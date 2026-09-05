"""108 課綱指標查詢。

存在的理由：課綱代碼原本寫在技能的 references/ markdown，由模型讀進 context
再寫出來，沒有任何方式能驗證。實測發現產出的教案裡 10 筆課綱對應**全部有誤**
（4 筆代碼不存在、6 筆敘述與領綱不符）。

這個模組查表回傳，代碼保證存在、敘述保證是領綱原文。
查不到就回 None——**絕不猜測，絕不生成**。
"""
from __future__ import annotations

from .store import (
    CurriculumStore,
    Indicator,
    default_store,
    get_by_code,
    list_competencies,
    lookup,
    verify_codes,
)

__version__ = "1.0.0"
__all__ = [
    "CurriculumStore", "Indicator", "default_store",
    "lookup", "get_by_code", "list_competencies", "verify_codes",
]
