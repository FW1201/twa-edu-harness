# Agent Note: disable-model-invocation 分批移除（A/B 觀察）

Status: implemented

## Problem

21 支中 20 支設了 `disable-model-invocation: true`，代表模型永遠不會自動叫它們，
只有使用者手動打 `/name` 才會觸發。

但每一支的 `description` 都寫成自動路由用的觸發詞清單（「當使用者提及『教案』
『108課綱』…時觸發」）。**寫了觸發詞，卻同時關掉了觸發。**

## Decision

先改三支觀察兩週：`tw-edu-lesson-plan-108`、`tw-edu-exam-generator`、
`tw-edu-worksheet-creator`。這三支的觸發詞最明確、誤觸發的代價最低。

確認沒有誤觸發後，再套用到其餘 16 支。

**`tw-edu-synchronizer` 永遠保留 `true`** —— 它是改設定檔的工具，
不該被模型在備課途中自作主張叫起來。這一點已寫進它的 `whenToUse`。

`tw-edu-slides-creator` 本來就沒設，維持原狀。

## Alternatives considered

- **一次全部移除**：20 支同時從「只能手動叫」變成「模型會自動叫」，
  一旦有誤觸發，很難判斷是哪一支的 description 寫太寬。
- **維持現狀**：等於接受 description 裡的觸發詞是裝飾品。

## Consequences

兩週後要回來看這則 note，決定是否推廣到其餘 16 支。
判準：有沒有出現「使用者沒要教案，模型卻叫了教案技能」這類情形。
