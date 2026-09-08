# Agent Note: 收斂 lesson-plan-108 與 differentiated 的行內 docx 輔助函式

Status: implemented

## Problem

`twa_edu_core` 收掉了 15 份完全相同的 `tw_edu_doc_utils.py`，但重複還有第三種形態：
`tw-edu-lesson-plan-108` 與 `tw-edu-differentiated` 在自己的生成腳本裡**行內重新實作**
了同一組邏輯，函式名還不一樣（`set_cell_bg` vs `set_bg`、`add_cell_text` vs `cell_text`）。

檔名層級的 gate 抓不到這種重複，因為它不是複製檔案。

當初列為既存例外的理由是：兩支的參數與預設值與共用版**不完全相同**，
直接替換會改變既有教案與學習單的版面。教師手上已經有用這些技能產出的檔案。

## Decision

先建立可證明的版面基準，再替換。

### 1. 版面指紋工具（`scripts/docx_fingerprint.py`）

逐儲存格擷取底色、框線（顏色與粗細）、字型（含 `w:eastAsia` 與 `w:ascii`）、
粗體、字級、對齊、段落底線、頁面尺寸與邊界。

**工具本身第一版是壞的**：`set_cell_bg()` 是 append 而非取代，重複套用會留下
多個 `w:shd`，而我只讀第一個——結果改了底色卻回報「完全相同」。
一個偵測不到目標變更的工具毫無用處，因此改為讀取**所有** `w:shd` 與 `w:tcBorders`。

### 2. 逐項比對差異，用參數表達而非另寫實作

| 差異 | 處理 |
|---|---|
| 兩支的章節標題與儲存格文字**只設 `w:eastAsia`、不設 `w:ascii`**，共用版會設 `ascii='Arial'` | `set_east_asia_font` / `cell_write` / `section_heading` / `header_cell` / `data_cell` 新增 `latin` 參數，傳 `None` 表示不動拉丁字型 |
| differentiated 的表頭框線是中藍細框（`2471A3` / sz 4），共用版是深藍粗框（`1A5276` / sz 6） | `header_cell` 開放 `border_color` / `border_size` |
| lesson-plan 的章節標題一律用 `▌`，共用版 level 2 是 `▸` | `section_heading` 開放 `prefix` |
| differentiated 的章節標題是 `■` + 13pt + **無底線** | **維持行內**。這是不同的視覺樣式，用參數硬湊只會讓共用版變成什麼都能做的萬用函式 |

`verify_core_api.py` 原本擋下了這些新參數（參數數量變了）。已放寬為
「舊參數必須在前且不變，可往後追加**有預設值**的選用參數」，
並反向測試確認新增無預設值的參數仍會被擋。

### 3. 薄封裝不算收斂

第一版做法是保留舊函式名當作對 core 的薄封裝。`verify_no_vendored_utils` 把它們
照樣判為重複——**這是對的**。真正的收斂是移除封裝、改呼叫端：

- lesson-plan 直接使用 `set_cell_bg` / `set_cell_border`
- differentiated 的 `data_cell` 封裝改名 `row_cell`（它多帶 `latin=None`，
  是本技能專屬的呼叫方式，名稱刻意與共用版區隔）

## 驗證

四份產出（兩支技能 × 兩組參數）的版面指紋與替換前**逐儲存格完全相同**。

版面基準已納入 smoke test：兩支技能各有 `scripts/layout-baseline.json`，
`smoke.yml` 以 `layout_baseline` 登記。反向測試確認改動框線顏色會被擋下，
並指出確切的儲存格位置。

## Consequences

`verify_no_vendored_utils.py` 的 `GRANDFATHERED` 已清空——**不再有既存例外**。

`twa_edu_core` 的樣式參數（`latin` / `border_color` / `prefix`）是為了表達
既有的兩種樣式而加，不是猜測未來需求。再有新樣式時，先問「這是同一個元件的
變體，還是不同的元件」——differentiated 的章節標題就是後者，所以沒有硬塞進去。
