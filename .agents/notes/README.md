# Agent Notes

決策紀錄。**目的是讓三個月後的你知道當初為什麼這樣選**，而不是留下完整的稽核軌跡。

## 路徑

```
.agents/notes/{proposed|implemented|rejected}/{architecture|feature|process}/YYYY-MM-DD-topic.md
```

- `proposed` — 想做但還沒做
- `implemented` — 已落地
- `rejected` — 考慮過並否決（**這類最有價值**，它擋住未來的重複討論）

## 什麼時候要寫

改動了結構、契約、流程，或做了一個未來的你可能會質疑的取捨時，寫一篇。
純內容修正（改錯字、補一段教學說明）不需要。

## 格式

```markdown
# Agent Note: <一句話標題>

Status: implemented

## Problem
## Decision
## Alternatives considered
## Consequences
```

`Status` 必須與所在資料夾一致，`scripts/verify_agent_notes.py` 會檢查。
