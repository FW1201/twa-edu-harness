# Agent Note: 收斂 lesson-plan-108 與 differentiated 的行內 docx 輔助函式

Status: proposed

## Problem

`twa_edu_core` 收掉了 15 份完全相同的 `tw_edu_doc_utils.py`，但重複還有第三種形態：
`tw-edu-lesson-plan-108` 與 `tw-edu-differentiated` 在自己的生成腳本裡**行內重新實作**
了同一組邏輯，函式名還不一樣（`set_cell_bg` vs `set_bg`、`add_cell_text` vs `cell_text`）。

檔名層級的 gate 抓不到這種重複，因為它不是複製檔案。

## Decision（尚未執行）

暫時列為 `verify_no_vendored_utils.py` 的既存例外（`GRANDFATHERED`）。

不立刻改的理由：這兩支的行內版本與共用版**參數與預設值不完全相同**，
直接替換會改變既有教案與學習單的版面。教師手上已經有用這些技能產出的檔案，
版面突然變動是實際損害，不值得為了程式碼整潔去冒。

## 收斂的前置條件

1. 先為這兩支寫版面回歸測試（產出 .docx → 比對表格數、儲存格底色、字型）
2. 逐一比對行內版與共用版的行為差異，確認可以無損替換
3. 替換後把它們從 `GRANDFATHERED` 移除

## Consequences

在收斂之前，改 `twa_edu_core` 的版面邏輯**不會**影響這兩支。
這既是保護，也是陷阱——改共用版時要記得它們沒跟上。
