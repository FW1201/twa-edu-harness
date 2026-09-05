# twa_edu_core

`tw-edu-*` 教學技能的共用程式碼。取代原本散落在 15 個 skill 的
`scripts/tw_edu_doc_utils.py` 複本。

## 安裝

```bash
pip install -e ./python        # 在 repo 內開發
```

技能的生成腳本會在 import 失敗時自動把 `python/` 加進 `sys.path`，
所以未安裝時也能直接執行。

## 模組

| 模組 | 內容 |
|---|---|
| `theme` | 品牌色票與 `rgb_hex()` |
| `fonts` | Word 東亞字型、matplotlib 與 ReportLab 的 CJK 字型註冊 |
| `docx_utils` | 儲存格、表格、章節標題、封面頁、A4 版面、頁首頁尾 |

## 相容性

`from twa_edu_core import *` 的輸出集合與舊的 `from tw_edu_doc_utils import *`
完全一致，由 `scripts/verify_core_api.py` 驗證。
