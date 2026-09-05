# Agent Note: Bundle / Preset 使用自訂中性 schema

Status: implemented

## Problem

三層架構的 Bundle 與 Preset 層參考自某個上游 harness 專案（本 repo 一律稱其為
`ref-harness`）。最直接的做法是照抄它的設定檔格式，直接宣告它的套件名。

但擁有者明確要求：因政治因素，**本 repo 與所有對外文件都不得出現該上游專案的名稱或套件名**。

## Decision

Bundle / Preset 層使用本 repo 自訂的中性 schema：

- `harness/bundle.yml` — 宣告貢獻的 skill / shared / preset / python 目錄
- `harness/capabilities.yml` — 中性能力詞彙（`file-read`、`shell`、`web-search`…）
- `scripts/gen_harness_adapter.py` — 產生特定 runtime 的設定檔，輸出到 `dist/`（gitignored）
- `scripts/verify_no_vendor_names.py` — CI 掃描全 repo，禁止出現上游名稱

## Alternatives considered

- **直接 commit runtime 專屬設定檔**：違反擁有者的明確要求。
- **完全不做 Bundle 層**：等於放棄三層架構最實用的一層。

## Consequences

多一層間接。但這其實是更好的設計：中性能力詞彙不綁任何 runtime，
上游 API 破壞相容時只需改 generator 一個檔案，不用動 repo 結構。

同樣的理由讓 P4 的課綱查詢選擇 **MCP** 而非 runtime 專屬插件——
MCP 是中性標準，Claude Code 現在就能直接用。
