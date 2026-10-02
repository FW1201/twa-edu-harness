# twa-edu-harness

> 臺灣 K-12 教育 Agent Harness — 108 課綱教學技能三層架構

[![Skills](https://img.shields.io/badge/Skills-23-green)](#skills-清單)
[![Version](https://img.shields.io/badge/Version-4.0.0--alpha.1-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**給臺灣現場教師的 AI 備課工具組。** 依 108 課綱設計素養導向教案、素養命題、
評量規準、學習單與教學簡報，輸出 `.docx` / `.pptx` / `.xlsx` 教學文件。

服務對象是**教師**：備課、命題、評量、班級經營、親師溝通、校內行政，
以及教師自己的專業發展（行動研究、研習教材）。
學生自學工具與學術研究工具**不在本專案範圍內**。

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

`twa-teacher` 是本專案**唯一**的 preset：臺灣 K-12 教師的備課夥伴，
掛載全部 21 支技能，關閉自我修改、子代理、持久終端機等對教師不必要的能力。

`DENIED.md` 逐項寫明**為什麼**否決某項能力——限制跟能力一樣是設計的一部分。

⚠️ 尚未實機驗證（需要 harness runtime）。

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
**共 23 支 Skills**

#### 課程設計

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-lesson-plan-108` | 4.1.1 | 依課程目標安排活動、時間與評量。 |
| `tw-edu-curriculum-mapper` | 4.1.0 | 跨單元安排學期目標、進度與課綱對應。 |
| `tw-edu-differentiated` | 4.1.0 | 依學習證據調整任務與支持。 |
| `tw-edu-interdisciplinary` | 4.1.0 | 整合不同學科的概念與探究任務。 |
| `tw-edu-pbl-designer` | 4.1.0 | 設計驅動問題、探究歷程與真實成果。 |

#### 評量命題

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-exam-generator` | 4.1.0 | 製作有答案、解析與配分的評量。 |
| `tw-edu-rubric-designer` | 4.1.0 | 建立任務專屬的表現描述與評分方式。 |
| `tw-edu-formative-assessment` | 4.1.0 | 收集課中證據並決定教學調整。 |
| `tw-edu-anti-ai-assessment` | 4.1.0 | 檢視評量證據與改善任務設計。 |

#### 教材資源

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-worksheet-creator` | 4.1.0 | 編排學生可完成的練習與思考任務。 |
| `tw-edu-slides-creator` | 5.1.0 | 製作可編輯投影片與教師講稿。 |
| `tw-edu-mini-app` | 4.1.0 | 產出可本機開啟的互動教學網頁。 |

#### 學生表現

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-feedback-writer` | 4.1.0 | 根據作品證據撰寫具體可行的回饋。 |
| `tw-edu-learning-portfolio` | 4.1.0 | 協助整理學習證據、反思與成果。 |

#### 班級行政

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-classroom-culture` | 4.1.0 | 設計共同規範、班級活動與支持策略。 |
| `tw-edu-parent-communication` | 4.1.0 | 撰寫清楚、有同理心的親師草稿。 |
| `tw-edu-school-document` | 4.1.0 | 整理計畫、會議與行政文稿。 |
| `tw-edu-meeting-facilitator` | 4.1.0 | 建立議程、紀錄與可追蹤行動事項。 |

#### 教師專業

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-citation-checker` | 2.1.0 | 核實文獻存在性與引用資訊。 |
| `tw-edu-research-viz` | 4.1.0 | 以真實數據製作研究圖表。 |

#### 套組設定

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-synchronizer` | 2.1.0 | 建立與更新可供技能讀取的教師偏好。 |

#### 未分類

| Skill | 版本 | 說明 |
|---|---|---|
| `tw-edu-learning-evidence-analyzer` | 1.0.0 | 以匿名實際作答與作品判讀班級學習證據，區分缺答、題目疑義與待驗證錯因。 |
| `tw-edu-material-reviewer` | 1.0.0 | 檢查既有教材、試卷或簡報的可定位缺陷，提出局部修正並複查；生成器負責編排審查報告。 |
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
data/curriculum/       108 課綱權威資料（九大領域 3460 筆，由領綱 PDF 抽取）
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

## 獨立套組同步

教師核心以 FW1201/tw-edu-skills 為真源，固定23個自足套件與commit/hash，本repo提供選用課綱服務與adapter。見 independent-skills-lock.json；使用Skill不需要Harness。
