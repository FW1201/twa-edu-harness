# 安裝到 harness runtime

> 本文說明 Bundle 層。只想在 Claude Code 使用技能的話，看 [README](../README.md) 就夠了。

## 三層的差別

| 層 | 是什麼 | 現況 |
|---|---|---|
| **Skill** | 21 支教學技能，模型按需載入 | ✅ 可用 |
| **Bundle** | 讓 harness runtime 發現並掛載這些技能的封裝 | ⚠️ 見下方「目前狀態」 |
| **Preset** | 完整的「教師 Agent」：人格 + 能力 + 邊界 | 🚧 P3 |

## 中性 schema

本 repo **不 commit 任何特定 runtime 的設定檔**，也不依賴其套件名。
真源是自訂的中性宣告：

```
harness/bundle.yml          貢獻哪些 skill / shared / agent / python 目錄
harness/capabilities.yml    中性能力詞彙（file-read / shell / web-search…）
harness/schema/*.json       上述兩者的 JSON Schema
harness/adapters/<target>.yml   中性能力 → 特定 runtime 插件名的對應表
```

要接上某個 runtime 時，由 generator 產出該 runtime 的設定，輸出到 `dist/`（不納入版控）：

```bash
python scripts/gen_harness_adapter.py --target ref-harness
```

這樣做的三個好處：repo 公開內容與任何 runtime 解耦；runtime 的 API 破壞相容時
只需改對應表一個檔案；中性能力詞彙可同時映射到多個 runtime。

## 目前狀態：對應表尚未填寫

`harness/adapters/ref-harness.yml` 的 `status` 是 **`unmapped`**。

開發機上沒有該 runtime 環境，**無法驗證插件的實際識別名**，因此對應表刻意留空
而不是憑印象填——填錯的後果是安裝後靜默失效，比留白更糟。

在填寫完成之前：

- generator 仍會執行，但產物標示為未驗證草稿，並列出缺少哪些對應
- 不要宣稱本 repo 已可在該 runtime 安裝

### 取得環境後的步驟

1. 查閱該 runtime 的插件清單，找出對應每項能力的插件識別名
2. 填進 `harness/adapters/ref-harness.yml` 的 `pluginName`
3. 把 `status` 改為 `draft`
4. `python scripts/gen_harness_adapter.py --target ref-harness`
5. 實機安裝驗證：技能出現在模型的 catalog、數量正確、叫得起來
6. 通過後把 `status` 改為 `verified`，並寫一篇 Agent Note 記錄對應關係

驗收清單見 `.agents/skills/twa-release-check/`。

## 命名約定

參考架構一律稱 **`ref-harness`**。repo 內不得出現該上游專案的名稱或套件前綴，
`scripts/verify_no_vendor_names.py` 會在 CI 強制掃描。

理由見 `.agents/notes/implemented/architecture/2026-09-05-runtime-neutral-bundle.md`。
