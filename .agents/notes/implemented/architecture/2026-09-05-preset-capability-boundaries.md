# Agent Note: Preset 的能力邊界以「禁用」為設計核心

Status: implemented

## Problem

Preset 跟 Bundle 的差別是什麼？如果 preset 只是「把技能包起來」，
那它相對於 Bundle 沒有增加任何東西。

## Decision

Preset 的價值在**限制**，不在能力。

`twa-teacher` 禁用五項：`runtime-self-modify`、`subagent`、`persistent-terminal`、
`plan-mode`、`lsp`。每一項在 `DENIED.md` 都要寫明為什麼否決、什麼情況下可以重新考慮。

`verify_bundle_schema.py` 強制檢查：`deny` 列的每一項在 `DENIED.md` 都要出現，
否則 CI 紅。理由是否決的理由會隨時間流失——三個月後有人覺得「這個開著比較方便」
就打開了，而當初的考量已經沒人記得。

## 兩個 preset 的差異是刻意的

`twa-researcher` **開放** `subagent`，`twa-teacher` 禁用。

教案生成是線性工作流，沒有可平行化的部分，而 token 成本對教師不透明——
他們不會預期「幫我寫個教案」會同時跑起五個代理。

引用批次查核天生可平行（每筆引用彼此獨立），而使用者是研究者，
對成本與並行有預期。

這個差異寫進了兩邊的 `DENIED.md`，避免未來被當成不一致而「修正」。

## Consequences

新增 preset 時，`DENIED.md` 是必寫的，不是選配。

能力詞彙（`harness/capabilities.yml`）目前有 14 項，每項帶 `risk` 與 `note`。
`shell` 標為 high risk 但註明「技能的生成腳本靠這項執行」——
讓未來要收緊權限的人知道哪些動不得。
