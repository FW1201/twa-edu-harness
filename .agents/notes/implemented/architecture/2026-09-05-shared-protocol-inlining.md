# Agent Note: 共用協議採「開發時引用、發版時內聯」

Status: implemented

## Problem

四份共用協議被 19 支技能宣告為「必要前置步驟」。它們必須有單一真源
（否則會像 `tw_edu_doc_utils.py` 那樣分裂成 15 份複本），但單支安裝時
`npx skills add` 只複製該技能自己的目錄，`shared/` 不會跟著過去。

v3.x 的做法是寫 `../../tw_edu_*.md`，從技能目錄往上兩層——在 repo 內指到 repo 之外，
安裝後指到使用者家目錄。**四份協議在使用者機器上一份都不存在，且沒有任何檢查擋得住。**

## Decision

兩種形態並存：

- `skills/` — 開發用，引用 `../../shared/<name>.md`，單一真源
- `dist/skills/` — 發版用，由 `scripts/build_standalone_skills.py` 把
  `metadata.shared` 宣告的協議展開成 SKILL.md 的附錄，內文引用改寫為「本檔附錄的…」

`verify_skill_links.py --standalone` 驗證內聯版沒有任何逸出技能集合的相對連結。

## Alternatives considered

- **每支技能各放一份協議**：回到 `doc_utils` 的老路，改一次要改 19 次。
- **要求使用者手動安裝 shared/**：多一個步驟就等於多一個失敗點，
  而且失敗時是靜默的——技能會照跑，只是跳過了「必要前置步驟」。

## Consequences

發版流程多一個建置步驟。內聯版的 SKILL.md 會變長（教案技能從 332 行變成 950 行），
但那是模型讀的內容，長度換來的是「安裝後真的能用」。
