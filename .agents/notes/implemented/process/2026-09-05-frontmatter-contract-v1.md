# Agent Note: Frontmatter 契約 v1 與嚴格模式的導入順序

Status: implemented

## Problem

v3.x 的 frontmatter 沒有統一 schema：21 支全部沒有 `license` / `metadata` / `whenToUse`，
12 支沒有 `author`，`allowed-tools` 是字串型別，其中一支還宣告了非法工具名。

直覺做法是一次寫好嚴格的 gate 然後打開。但那樣新 repo 第一天 CI 就是紅的——
而長期紅燈的 CI 沒人看，沒人看就擋不住問題，這正是舊 repo 的病根。

## Decision

分兩步：

1. P0 先讓 gate 有 ERROR / WARNING 兩級。現在就必須成立的規則（`name` 是 kebab-case、
   `name` == 目錄名、無 camelCase 舊鍵、工具名合法）設為 ERROR；契約 v1 的欄位先報 warning。
2. P1 補齊 21 支之後，把預設改為嚴格，`--lenient` 只留給遷移中的分支。

**規則要嚴，但每次收緊之前要先讓現況通過。**

## Consequences

`description` 負責召回、`whenToUse` 負責精確度（「什麼時候不要用我、該用哪一支」）。
新增技能時兩者都要寫，規範見 `.agents/skills/twa-skill-author/`。
