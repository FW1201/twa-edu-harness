# twa-edu-harness

> 臺灣 K-12 教育 Agent Harness — 108 課綱教學技能三層架構

[![Skills](https://img.shields.io/badge/Skills-21-green)](#skills-清單)
[![Version](https://img.shields.io/badge/Version-4.0.0--alpha.1-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

給臺灣現場教師的 AI 備課工具組。依 108 課綱設計素養導向教案、素養命題、評量規準、
學習單與教學簡報，輸出 `.docx` / `.pptx` / `.xlsx` 教學文件。

**本 repo 是 [`FW1201/tw-edu-skills`](https://github.com/FW1201/tw-edu-skills) 的後繼者。**
Skill 名稱維持 `tw-edu-*` 不變，既有的呼叫方式與教學講義完全沿用。

---

## 安裝

### 方式一：Claude Code（推薦，也是目前唯一經過實測的方式）

```bash
npx skills add FW1201/twa-edu-harness --all -a claude-code
pip install -r requirements.txt
```

**強烈建議一併掛上課綱查詢 MCP**，讓模型能查證課綱代碼而不是憑印象寫：

```bash
pip install -e ./python[mcp]
# 在 MCP 設定中加入：python -m twa_curriculum_mcp.server
```

沒有它時，技能會在產出中標注「課綱代碼未經查核」。
原因見 [`docs/teacher-walkthrough.md`](docs/teacher-walkthrough.md)——
修正前抽驗 10 筆課綱對應，**全部有誤**。

單獨安裝一支：

```bash
npx skills add FW1201/twa-edu-harness/skills/tw-edu-lesson-plan-108 -a claude-code
```

### 方式二：Bundle（掛載到 harness runtime）

`harness/bundle.yml` 以中性 schema 宣告本 repo 貢獻的目錄，
由 `scripts/gen_harness_adapter.py` 產生特定 runtime 的設定。

⚠️ **對應表尚未填寫，尚未實機驗證。** 詳見
[`docs/harness-install.md`](docs/harness-install.md)。

### 方式三：Preset（完整的 Agent 人格與能力邊界）

| Preset | 給誰 | 技能 | 特點 |
|---|---|---|---|
| `twa-teacher` | K-12 教師 | 全部 21 支 | 關閉自我修改、子代理、持久終端機 |
| `twa-researcher` | 研究者 | 查核 / 視覺化 / 學習歷程 | 開放子代理以支援批次查核 |

每個 preset 的 `DENIED.md` 逐項寫明**為什麼**否決某項能力——
限制跟能力一樣是設計的一部分。

⚠️ 同樣尚未實機驗證（需要 harness runtime）。

---

## 三分鐘上手

在 Claude Code 裡直接說出你要做的事即可，不必記指令：

> 「幫我寫一份國中八年級國語文〈背影〉的素養導向教案」

技能會先跑**概念對齊**（確認年級、節數、教學目標），再產出符合 108 課綱格式的 `.docx`。

想先調成自己的教學情境（學校、年段、班級人數、慣用格式），跑一次：

```
/tw-edu-synchronizer
```

它會產生 `teacher-profile.md`，之後所有技能都會讀它自動客製化。

---

## Skills 清單

<!-- BEGIN GENERATED skill-index (scripts/gen_skill_index.py) -->
**共 21 支 Skills**

#### 課程設計

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-lesson-plan-108` | 2.1.0 | 依據臺灣108課綱設計素養導向教案，產出格式完整的 .docx 教案文件。 |
| `tw-edu-curriculum-mapper` | 1.0.0 | 輸入學習主題或課程單元，自動對應108課綱各領域學習表現、學習內容代碼， 並生成課程地圖視覺化表格（.xlsx）。 |
| `tw-edu-differentiated` | 1.0.0 | 為同一節課設計差異化教學方案，提供基礎/標準/進階三層次學習任務， 整合通用設計學習（UDL）框架，支援融合教育與特殊需求情境。 |
| `tw-edu-interdisciplinary` | 1.0.0 | 設計跨領域/跨科課程，整合108課綱彈性學習課程與校本課程框架。 |
| `tw-edu-pbl-designer` | 1.0.0 | 設計專題式學習（PBL）方案，從驅動問題設計到最終成品發表全程引導。 |

#### 評量命題

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-exam-generator` | 2.1.0 | 依臺灣108課綱素養情境命題原則出題，支援各科試卷生成，含情境題、 閱讀理解、非連續文本、生活情境應用等素養題型，並自動依年級調整難度。 |
| `tw-edu-rubric-designer` | 1.0.0 | 依據學習目標設計完整評量規準（Rubric），支援整體式與分析式兩種格式。 |
| `tw-edu-formative-assessment` | 1.0.0 | 設計課堂形成性評量工具，包含出口票、KWL表、概念圖提示、診斷測驗等。 |
| `tw-edu-anti-ai-assessment` | 1.1.0 | 分析教師上傳或輸入的評量內容，識別哪些題目學生能輕易用 AI 完成， 在保持相同學習目標的前提下，提供具體的矯正修改方案，使評量真正 能測量學生的思考與能力，而非測量學生使用 AI 的能力。 |

#### 教材資源

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-worksheet-creator` | 1.0.0 | 依課文、主題、年級生成素養導向學習單，整合提問鷹架與圖表填寫。 |
| `tw-edu-slides-creator` | 4.0.0 | 台灣 K-12 教育簡報生成器。 |
| `tw-edu-mini-app` | 1.0.0 | 開發互動式教學小程式（測驗/遊戲/計時器/隨機分組等）， 並自動部署到 Vercel 或 GitHub Pages，生成可分享的永久連結。 |

#### 學生表現

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-feedback-writer` | 1.0.0 | 為學生作業、作文、口頭報告、學習歷程撰寫專業回饋評語， 依評量規準生成正向具體的書面評語，支援批量處理。 |
| `tw-edu-learning-portfolio` | 1.0.0 | 引導學生整理學習歷程檔案（108課綱大學申請入學用）， 包含課程學習成果說明、多元表現敘述、自我評述框架。 |

#### 班級行政

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-classroom-culture` | 1.0.0 | 提供班級經營策略，包含班規設計、積極行為支持(PBS)方案、 導師週記、班級氣氛建立活動。 |
| `tw-edu-parent-communication` | 1.0.0 | 撰寫親師溝通文件，包含班訊、聯絡簿訊息、關懷信函、行為記錄函。 |
| `tw-edu-school-document` | 1.0.0 | 協助撰寫校園行政公文與教育文書，包含簽呈、計畫書、成果報告、 研習申請、課程計畫，符合教育部公文格式。 |
| `tw-edu-meeting-facilitator` | 2.1.0 | 為教師專業學習社群(PLC)、課發會、行政會議、共同備課設計議程與記錄模板， 並透過 Google Calendar MCP 建立會議提醒、Google Drive MCP 儲存紀錄、 Gmail MCP 發送摘要給與會者。 |

#### 學術支援

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-citation-checker` | 1.0.0 | 嚴格查核學術文獻的準確性與引用格式，透過 WebSearch、Consensus MCP 進行 多源交叉驗證，逐一確認作者/年份/標題/期刊/頁碼，並驗證目標引用格式 (APA 7th / MLA 9th / 臺灣學位論文 / Chicago) 是否正確。 |
| `tw-edu-research-viz` | 1.0.0 | 將學術研究資料（文獻關係、研究架構、概念框架、資料流程、統計結果） 視覺化為精確的學術圖表，優先調用 Excalidraw MCP 生成手繪風格圖， 或生成可嵌入論文的 SVG/PNG 圖表。 |

#### 套組設定

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-synchronizer` | 1.0.0 | K-12 教學套組客製化工具，幫助教師根據個人情境調整所有 tw-edu-* Skills 的預設行為。 |
<!-- END GENERATED skill-index -->

> 這份表格由 `scripts/gen_skill_index.py` 從 `skills/` 產生，CI 會檢查一致性。
> 不要手動編輯——改了會被下次產生覆蓋，而且 CI 會擋。

---

## 架構

```
skills/tw-edu-*/       21 支教學技能（模型按需載入）
shared/                跨技能共用協議（概念對齊、學段適配、引導式收集、MCP 策略）
python/twa_edu_core/   共用程式碼（Word 版面、色票、CJK 字型）
python/twa_curriculum/ 108 課綱查詢 + MCP server
agents/                技能召喚的 subagent 定義
data/curriculum/       108 課綱權威資料（由領綱 PDF 抽取）
harness/               Bundle 層宣告（中性 schema）
presets/               Agent Preset：persona + 能力邊界
scripts/               驗證閘門（gates）
.agents/notes/         決策紀錄
```

- Bundle / Preset 的安裝方式與目前狀態：[`docs/harness-install.md`](docs/harness-install.md)
- 從 v3.x 遷移：[`docs/MIGRATION-v3-to-v4.md`](docs/MIGRATION-v3-to-v4.md)
- 一次完整備課的實際產出：[`docs/teacher-walkthrough.md`](docs/teacher-walkthrough.md)

規範與開發約定見 [`AGENTS.md`](AGENTS.md)。

### 單支安裝的處理

四份共用協議在 repo 內是單一真源（`shared/`），但 `npx skills add` 單獨安裝一支技能時
不會把它們帶過去。發版時由 `scripts/build_standalone_skills.py` 把協議內聯進
`dist/skills/` 的 SKILL.md，因此單支安裝也能完整運作。

---

## 貢獻

送 PR 前先在本機跑過閘門：

```bash
python scripts/verify_skill_frontmatter.py   # frontmatter 契約 v1
python scripts/verify_skill_links.py         # 相對連結不斷鏈
python scripts/verify_core_api.py            # twa_edu_core API 相容性
python scripts/verify_no_vendored_utils.py   # 禁止重複共用程式碼
python scripts/verify_agent_deps.py          # subagent 依賴隨附
python scripts/verify_agent_notes.py         # 決策紀錄格式
python scripts/verify_bundle_schema.py       # bundle / preset schema
python scripts/verify_no_vendor_names.py     # 受限的上游名稱
python scripts/gen_skill_index.py --check    # README 清單一致性
python scripts/smoke_test_scripts.py         # 實際跑出文件
```

或一次跑完：`npm run gates && npm run smoke`

新增技能的規格見 [`AGENTS.md`](AGENTS.md) 與 `.agents/skills/twa-skill-author/`。

---

## 授權

MIT — 見 [LICENSE](LICENSE)。教學現場可自由使用、修改與再散布。

課綱內容版權屬教育部；本專案僅提供教學設計輔助，不代表官方立場。
