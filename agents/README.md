# agents/

本 repo 隨附的 subagent 定義。

## 為什麼要放在這裡

`tw-edu-citation-checker` 在批次模式（3 筆以上引用）會召喚
`citation-checker-worker` 並行查核。這個 agent 的定義原本只存在於
`~/.claude/agents/`，**不會隨 `npx skills add` 一起安裝** ——
使用者裝好技能後，批次模式會在執行期直接失效。

這和「共用協議路徑指到 repo 外面」是同一類問題：技能宣告了一項依賴，
但那項依賴不在可安裝的範圍內。`scripts/verify_agent_deps.py` 會掃描
SKILL.md 中提到的 agent 名稱，確保每一個都能在本目錄找到定義。

## 安裝

`npx skills add` 只處理 `skills/`，不會安裝 agents。要啟用批次模式，
把定義複製到 agent 目錄：

```bash
cp agents/citation-checker-worker.md ~/.claude/agents/
```

## 清單

| Agent | 被誰使用 | 用途 |
|---|---|---|
| `citation-checker-worker` | `tw-edu-citation-checker` | 並行驗證單筆學術引用，只輸出 JSON 裁決 |
