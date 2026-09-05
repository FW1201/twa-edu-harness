# AGENTS.md

`twa-edu-harness` 是臺灣 K-12 教育 Agent Harness。**本文是這個 repo 規範的單一真源。**

修改 `skills/` 之前先讀本文。`CLAUDE.md` 是本檔的 symlink——要改請改 `AGENTS.md`。

---

## 1. Repo 定位

承載 `tw-edu-*` 教學技能的基座：提供 skill 契約、驗證閘門、共用協議與共用程式碼，並在 P4 之後提供 108 課綱查詢 service。

### 與其他專案的邊界

| Repo | 定位 | 關係 |
|---|---|---|
| **twa-edu-harness**（本 repo） | 教學技能的基座與發佈載體 | 上游，提供能力 |
| `confucius`（private） | 校園職務入口的講座 demo，伏羲思維層 × tw-edu 任務層 | **下游消費者**。應引用本 repo 的 skills，不自建第二份 |
| `fuxi-education-skills`（private） | 伏羲思維層技能 | 內容不公開，**不得**併入本 public repo |
| `tw-stu-skills` / `tw-research-skills` | 學生 / 研究者技能 | 未來才整併為 preset，現階段不動 |

---

## 2. 三層架構

```
Preset 層   presets/twa-teacher/       完整 Agent：persona + 能力 + 邊界（P3）
Bundle 層   harness/bundle.yml         中性封裝，可被 harness runtime 安裝（P2）
Skill 層    skills/tw-edu-*/SKILL.md   模型按需載入的任務指令
            shared/                    跨 skill 共用協議
            python/twa_edu_core/       共用程式碼
            agents/                    技能召喚的 subagent 定義
```

> ⚠️ 參考架構一律稱 `ref-harness`。**本 repo 與所有對外文件不得出現該上游專案的
> 名稱或套件名**，Bundle / Preset 使用自訂的中性 schema。理由見
> `.agents/notes/implemented/architecture/2026-09-05-runtime-neutral-bundle.md`。

### 責任邊界

Skill 層**該**放：教學法知識、引導式對話流程、輸出格式規範。
Skill 層**不該**放：大量結構化資料（→ 課綱 service）、可執行邏輯的重複實作（→ `twa_edu_core`）。

---

## 3. 命名

| 層級 | 前綴 | 說明 |
|---|---|---|
| 產品層（harness / bundle / preset / service） | `twa-*` | Taiwan Agent 品牌層 |
| 技能層（教師實際呼叫的東西） | `tw-edu-*` | **不改名** |

**為什麼 skill 不改名**：skill `name` 是註冊表的唯一鍵，沒有 alias 或轉址機制。改名等於讓所有既有呼叫、教學講義與工作坊教材同時失效。詳見 `.agents/notes/implemented/architecture/`。

---

## 4. Skill 開發規範

每支 skill 的結構：

```
skills/<name>/
├── SKILL.md          # 必要。frontmatter 契約見下
├── references/       # progressive disclosure：模型需要時才讀
└── scripts/          # 生成腳本，須有 smoke.yml
```

### Frontmatter 契約

`name` 必須是 kebab-case 且**等於目錄名**。`description` ≤ 300 字元（含觸發詞）。
`version` 必須符合 SemVer 且在 `CHANGELOG.md` 有對應條目。`author` / `license` 必填。

塞不進 `description` 的路由細節寫 `whenToUse`——`description` 負責召回，`whenToUse` 負責精確度（「什麼時候**不要**用我」）。

`allowed-tools` 只能是合法工具名或 `mcp__*` 前綴。

### 共用協議引用

引用 `shared/` 一律寫 `../../shared/<name>.md`，並在 `metadata.shared` 宣告。

⚠️ 單支安裝時 `shared/` 不存在。發版時由 `scripts/build_standalone_skills.py` 把協議內容內聯進 `dist/skills/`。**開發時引用 `shared/`，發佈時交給建置期處理。**

### 依賴 subagent 的 skill

若 skill 會召喚 subagent（例如 `tw-edu-citation-checker` 的批次模式召喚 `citation-checker-worker`），該 agent 定義**必須放在本 repo 的 `agents/`**。放在 `~/.claude/agents/` 的定義不會隨 `npx skills add` 安裝，使用者端會直接失效。

---

## 5. 輸出規範

| 項目 | 值 |
|---|---|
| matplotlib 中文字型 | `Noto Sans CJK JP` |
| ReportLab PDF 字型 | `STSong-Light` |
| 主要輸出格式 | `.docx` / `.pptx` / `.xlsx` / `.pdf` |
| 語言 | 繁體中文（台灣用語），技術術語用英文 |

共用實作一律 `from twa_edu_core import *`，**不得**在 `skills/*/scripts/` 內複製工具檔
或重新實作 `set_cell_bg()` 這類函式。

用 matplotlib 產圖時，繪圖前先呼叫 `register_cjk_fonts()`，且不要在 `ax.text()`
指定 `fontfamily`——指定拉丁字型會讓所有中文變成空白方框。

---

## 6. Gates

CI 的每一道 gate 都可在本機單獨執行：

```bash
python scripts/verify_skill_frontmatter.py   # frontmatter 契約 v1（預設嚴格）
python scripts/verify_skill_links.py         # 相對連結不斷鏈、不逸出 repo 根
python scripts/verify_core_api.py            # twa_edu_core 對舊介面的相容性
python scripts/verify_no_vendored_utils.py   # 禁止重複的共用程式碼
python scripts/verify_agent_deps.py          # SKILL.md 召喚的 subagent 要隨附
python scripts/verify_agent_notes.py         # 決策紀錄的路徑與 Status 一致
python scripts/gen_skill_index.py --check    # README 清單與實際目錄一致
python scripts/smoke_test_scripts.py         # 動態列舉並實際產出文件
python scripts/verify_bundle_schema.py       # bundle / preset schema 與路徑存在
python scripts/verify_no_vendor_names.py     # 受限的上游名稱
python scripts/build_standalone_skills.py    # 內聯版建置
python scripts/gen_harness_adapter.py        # runtime 設定產生（輸出到 dist/）
```

`npm run gates` 可一次跑完所有驗證。

**核心原則：所有檢查一律動態列舉檔案系統，禁止硬編碼清單。**
舊 repo 的 CI 把腳本路徑與 skill 數量寫死，腳本被刪除後 CI 永遠是紅的，於是沒人看 CI，於是問題持續累積。這是本 repo 存在的直接原因。

---

## 7. Agent Notes

改動了結構、契約、流程，或做了一個未來的你可能會質疑的取捨時，寫一篇：

```
.agents/notes/{proposed|implemented|rejected}/{architecture|feature|process}/YYYY-MM-DD-topic.md
```

純內容修正（改錯字、補教學說明）不需要。

---

## 8. 編輯本文件

`CLAUDE.md` 是 `AGENTS.md` 的 symlink。**改真檔 `AGENTS.md`。**
