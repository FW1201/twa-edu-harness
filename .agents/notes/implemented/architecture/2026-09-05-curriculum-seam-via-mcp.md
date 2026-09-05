# Agent Note: 課綱查詢用 MCP，不用 runtime 專屬插件

Status: implemented

## Problem

課綱代碼原本寫在技能的 `references/` markdown，由模型讀進 context 再寫出來。
沒有任何方式能驗證。

2026-09-05 實測 `tw-edu-lesson-plan-108` 產出的教案，抽驗 10 筆課綱對應：
**4 筆代碼根本不存在**（前綴寫成 `語-`，正確是 `國-`）、
**6 筆代碼存在但敘述是編的**、**完全正確 0 筆**。

教案會被送交課發會。一個看起來正確但不存在的代碼，會讓教師在會議上出糗。

## Decision

三層：資料（`data/curriculum/*.json`）、查詢層（`python/twa_curriculum/`）、
面向模型的工具（`python/twa_curriculum_mcp/`，MCP）。

**選 MCP 而非 runtime 專屬插件**，三個理由：

1. 不引入 TypeScript build——保住「安裝不需額外建置授權」這個優勢
2. MCP 是中性標準，不受 `ref-harness` 的命名限制影響
3. **Claude Code 現在就能用**，不必等到有 runtime 環境

## 資料來源與可信度

資料由 `scripts/build_curriculum_data.py` 從教育部領綱 PDF 抽取，
**不是人工輸入，也不是模型生成**。更新時重跑腳本，不手改 JSON。

抽取過程遇到的三個實際問題都處理了：PDF 本身混用 Unicode 羅馬數字與拉丁字母
（國語文領綱有 37 處）、分散對齊在中文字之間插入空白、長敘述跨行。

## 為什麼先只做國語文

課綱資料的正確性是最大的不確定因素。先做一個領域把架構跑通、
把抽取的邊界情況找出來，再擴充其餘領域。每個領域一個 PR。

`verify_curriculum_codes.py` 對尚未載入的領域只提示不擋，
所以擴充是漸進的，不會因為資料不全而卡住整個 repo。

## 光有 tool 還不夠：也要有 gate

工具讓模型「可以」查證，但不保證它「會」查證。因此另加
`scripts/verify_curriculum_codes.py`：只要是已載入領域的代碼，
出現在 repo 任何地方都必須存在，附帶敘述也必須與領綱相符。

這道 gate 一上線就抓到 30 處問題，包括兩份參考檔的大量捏造內容
（自創序號、把兩個類別誤併為一類）。已用權威資料重建。

**已知錯誤前綴要單獨處理**：`語-` 這類錯誤特別危險——正因為前綴是錯的，
代碼查不到，反而躲過了「代碼是否存在」的檢查。因此 gate 維護一份
`KNOWN_WRONG_PREFIX` 明確攔截。

## Consequences

無領域前綴的代碼（`5-Ⅳ-2`、`Ab-Ⅳ-1`）會跨領域撞號，因此只在標有
`<!-- curriculum-domain: X -->` 的檔案內比對。刻意引用錯誤範例的文件
（例如記錄這次發現的 walkthrough）用 `<!-- curriculum-check: ignore -->` 豁免。

修正後重新產出教案，10 個課綱代碼全部通過查核（修正前 0 個）。
