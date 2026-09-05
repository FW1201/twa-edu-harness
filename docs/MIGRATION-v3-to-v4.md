# 從 tw-edu-skills v3.x 遷移到 twa-edu-harness v4

## 結論先講

**技能名稱沒有改。** `tw-edu-lesson-plan-108` 還是 `tw-edu-lesson-plan-108`，
觸發詞沒變，教學講義與工作坊教材不用改。

要改的只有安裝來源：

```bash
# 舊
npx skills add FW1201/tw-edu-skills --all -a claude-code

# 新
npx skills add FW1201/twa-edu-harness --all -a claude-code
```

## 為什麼要換 repo

v3.x 有三類結構性問題，在原地修的成本高於重建：

1. **共用協議在使用者機器上是失效的。** 19 支技能把四份協議宣告為
   「必要前置步驟」，路徑卻寫成 `../../tw_edu_*.md` —— 安裝後指到家目錄，
   四份一份都不存在。技能會照跑，只是靜默跳過那個步驟。
2. **CI 永遠是紅的。** 它引用一支 2026-05-11 就被刪除的腳本。
   紅燈沒人看，於是後續問題全部無人攔截。
3. **數量有六個互相矛盾的說法**（24 / 19 / 18 / 16 / 20，實際 21），
   而且 README 列了三個根本不存在的技能。

v4 的做法是讓這些狀態在結構上不可能出現：清單由腳本產生、
所有檢查動態列舉檔案系統、每一項約定都有對應的閘門。

## 使用者會感覺到的差異

| 項目 | v3.x | v4 |
|---|---|---|
| 技能數量 | 文件說 19 / 18 / 16，實際 21 | **21**，由閘門保證一致 |
| 共用協議 | 安裝後失效 | 單支安裝時自動內聯進 SKILL.md |
| 自動觸發 | 20 支關閉（但 description 寫滿觸發詞） | 三支先開放觀察，其餘維持手動 |
| `tw-edu-research-viz` | 產圖的中文全是空白方框 | 已修 |
| `tw-edu-citation-checker` | 批次並行模式在使用者端失效 | 隨附 subagent 定義（需另行安裝，見 `agents/README.md`） |

## 舊 repo 怎麼辦

`FW1201/tw-edu-skills` 保留 `v3.1-final` tag，既有安裝不會壞，
但不再更新。README 會置頂指向本 repo。

## 需要手動處理的一件事

若你使用 `tw-edu-citation-checker` 的**批次查核**（3 筆以上引用），
把 subagent 定義複製到 agent 目錄：

```bash
cp agents/citation-checker-worker.md ~/.claude/agents/
```

`npx skills add` 只處理 `skills/`，不會安裝 agents。
