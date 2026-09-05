# CHANGELOG

本專案遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

---

## [4.0.0] — 2026-09-05

Preset 層。完整的 Agent 人格與能力邊界。

### Added

- **`presets/twa-teacher/`** — K-12 教師模式。全部 21 支技能；persona 要求
  108 課綱脈絡、繁體中文、**不要一次問超過三個問題**、執行技能前先完成概念對齊、
  **不確定的指標代碼就不要寫**。
- **`presets/twa-researcher/`** — 研究者模式。文獻查核 / 研究視覺化 / 學習歷程。
- **`DENIED.md`** — 每個 preset 逐項寫明為何否決某項能力、什麼情況下可重新考慮。
  `verify_bundle_schema.py` 強制檢查 `deny` 的每一項都要有交代，否則 CI 紅。
- **`docs/teacher-walkthrough.md`** — 一次完整備課的實際產出與量測數字。

### Preset 的設計原則：限制跟能力一樣重要

`twa-teacher` 禁用 `runtime-self-modify`（等同 shell 存取，教師無法評估風險）、
`subagent`（教案生成無可平行化的部分，且成本對教師不透明）、
`persistent-terminal`、`plan-mode`、`lsp`。

`twa-researcher` **開放** `subagent`——引用批次查核天生可平行，而使用者對成本有預期。
這個差異是刻意的，兩邊的 `DENIED.md` 都有記錄，避免未來被當成不一致而「修正」。

### 已知限制：Preset 層尚未實機驗證

開發機沒有 harness runtime，persona 與能力邊界**無法實測**。
本版驗證的是技能層——教師在 Claude Code 實際會遇到的流程
（見 `docs/teacher-walkthrough.md`：四份文件、45/39/39/39 KB、12/6/3/2 個表格）。

### ⚠️ 課綱代碼目前無法驗證真偽

教案產出的 `語-J-B1`、`5-Ⅳ-2` 等代碼來自技能 `references/` 的 markdown，
是模型讀進 context 再寫出來的。**沒有任何閘門能檢查代碼是否真的存在於領綱。**
模型幻覺一個格式正確但不存在的代碼，產出看起來完全一樣，而教師會把教案送交課發會。

`persona.md` 要求「不確定的指標代碼就不要寫」，但那是靠指示，不是靠機制。
這正是 P4 課綱 Capability Seam 要解決的問題。

---

## [4.0.0-rc.1] — 2026-09-05

Bundle 層。以自訂的中性 schema 宣告本 repo 對外提供什麼，不綁定任何特定 runtime。

### Added

- **`harness/bundle.yml`** — 貢獻的 skill / shared / agent / python 目錄宣告；
  **`harness/capabilities.yml`** — 中性能力詞彙（`file-read` / `shell` /
  `web-search`…），與任何 runtime 的插件名脫鉤；兩者各有 JSON Schema。
- **`harness/adapters/ref-harness.yml`** — 中性能力 → runtime 插件名的對應表。
- **`scripts/gen_harness_adapter.py`** — 依對應表產生 runtime 設定，輸出到
  `dist/`（不納入版控）。對應表未填寫時，產物明確標示為未驗證草稿。
- **`scripts/verify_bundle_schema.py`** — schema 合規、宣告的路徑真的存在、
  preset 的能力名稱在詞彙表內、`deny` 的每一項在 `DENIED.md` 都有交代。
- **`scripts/verify_no_vendor_names.py`** — 掃描全 repo 禁止出現受限的上游名稱。
  受限字串以 base64 存放，讓 gate 本身不含明文。
- `package.json`（中性 keywords，`files` 白名單）、`docs/harness-install.md`、
  `docs/MIGRATION-v3-to-v4.md`。
- CI 的結構驗證 job 擴為 **9 道 gate**。

### 目前狀態：Bundle 層尚未實機驗證

`harness/adapters/ref-harness.yml` 的 `status` 是 `unmapped`。開發機沒有該
runtime 環境，**無法確認插件的實際識別名**，因此對應表刻意留空而非憑印象填寫——
填錯的後果是安裝後靜默失效，比留白更糟。

在對應表填妥並實機驗證之前，不宣稱本 repo 可在該 runtime 安裝。
驗收清單見 `.agents/skills/twa-release-check/`。

---

## [4.0.0-beta.1] — 2026-09-05

結構重整。建立可擴充的基座與七道驗證閘門。

### Added

- **`python/twa_edu_core/`** — 取代 15 份內容完全相同的 `tw_edu_doc_utils.py`。
  拆為 `theme`（色票）、`fonts`（Word 東亞字型 + matplotlib/ReportLab 的 CJK 註冊）、
  `docx_utils`（儲存格、表格、章節標題、封面頁、A4 版面、頁首頁尾）。
  `from twa_edu_core import *` 的輸出集合與舊 `tw_edu_doc_utils` **完全一致**，
  由 `verify_core_api.py` 凍結驗證。
- **`agents/`** — 隨附技能召喚的 subagent 定義。`tw-edu-citation-checker` 的批次
  並行模式依賴 `citation-checker-worker`，而該定義原本只存在於作者本機的
  `~/.claude/agents/`，不會隨 `npx skills add` 安裝，使用者端會靜默失效。
- **七道閘門**：frontmatter 契約、相對連結、core API 相容性、禁止重複共用碼、
  subagent 依賴、Agent Note 格式、README 清單一致性。
- **`smoke_test_scripts.py`** — 動態列舉 `skills/*/scripts/generate_*.py`，
  依各自的 `smoke.yml` 實際執行並驗證產出大小與表格數。18 支腳本全部涵蓋。
- **`build_standalone_skills.py`** — 發版時把 `shared/` 協議內聯進 SKILL.md，
  輸出 `dist/skills/`，使單支 `npx skills add` 也能完整運作。內聯版經
  `verify_skill_links.py --standalone` 驗證為零外部相對依賴。
- **`.agents/notes/`** — 6 篇決策紀錄；`.agents/skills/` — 兩支維護用 meta-skill。
- CI 擴充為 4 個 job，新增「twa_edu_core 兩種安裝模式」驗證
  （`pip install -e` 與純 `sys.path` fallback 都要能跑）。

### Changed

- 21 支 SKILL.md 補齊 **frontmatter 契約 v1**：`license`、`whenToUse`、`metadata`
  （21 支原本全缺）、`author`（原本缺 12 支）。`description` 負責召回，
  `whenToUse` 負責精確度——寫明「什麼時候不要用我、該用哪一支」。
- `verify_skill_frontmatter.py` 預設改為嚴格模式（`--lenient` 保留給遷移中的分支）。
- **`disable-model-invocation` 分批移除**：`lesson-plan-108`、`exam-generator`、
  `worksheet-creator` 三支先移除，觀察兩週確認無誤觸發後再推廣。
  `tw-edu-synchronizer` 永遠保留 `true`——設定工具不該被模型在備課途中自作主張叫起來。
- `tw-edu-synchronizer` 的 Step 0 改為動態列舉同層 `tw-edu-*/SKILL.md`，
  移除寫死的三條路徑與過期的「16 個核心教學 Skills」。

### Fixed

- **`tw-edu-research-viz` 的 PRISMA 圖中文全部渲染成空白方框**。根因有二：
  腳本完全沒有設定 matplotlib 的 CJK 字型，且在 `ax.text()` 硬寫
  `fontfamily='DejaVu Sans'`（純拉丁字型）覆蓋掉一切。已接上
  `register_cjk_fonts()` 並移除硬寫字型，中文正常顯示。
- 移除 `generate_prisma.py` 會污染 `sys.path` 的 `sys.path.insert(0, '.')`。
- 刪除 `tw-edu-citation-checker` 的孤兒 `tw_edu_doc_utils.py`（無任何腳本使用）。

### 已知待辦（P2）

`tw-edu-lesson-plan-108` 與 `tw-edu-differentiated` 在腳本內**行內重新實作**了
`twa_edu_core` 已提供的邏輯（函式名與參數皆不同）。直接替換會改變既有教案的版面，
暫列為 `verify_no_vendored_utils.py` 的既存例外，收斂條件見
`.agents/notes/proposed/architecture/2026-09-05-inline-docx-helpers.md`。

---

## [4.0.0-alpha.1] — 2026-09-05

`FW1201/tw-edu-skills` 的後繼專案。**Skill 名稱維持 `tw-edu-*` 不變**，
既有呼叫方式、教學講義與工作坊教材完全沿用。

### 遷移

- 21 支教學技能移入 `skills/`，四份共用協議移入 `shared/` 並改為 kebab-case 檔名
- 遷入來源為本機工作區（較 GitHub `1cff78d` 新），已與已安裝副本逐份對帳

### Fixed

- **共用協議斷鏈**（19 支技能受影響）。原本寫 `../../tw_edu_*.md`，從技能目錄往上兩層落在
  repo 之外；安裝到 `~/.claude/skills/<name>/` 後，被 19 支宣告為「必要前置步驟」的四份協議
  一份都不存在。60 處引用已改為 `../../shared/<name>.md` 並由閘門驗證。
- **CI 引用已刪除的腳本**。`ci.yml` 呼叫 `tw-edu-slides-creator/scripts/generate_slides.py`，
  該檔於 2026-05-11 隨簡報工作流改版被移除，CI 自此永遠是紅的。新的 CI **動態列舉**
  檔案系統，不再硬編碼任何腳本路徑。
- **Skills 數量六個來源互相矛盾**（README 24 / GitHub README 19 / CLAUDE.md 18 /
  ci.yml 16 / repo description 20 / 實際 21）。清單改由 `scripts/gen_skill_index.py`
  產生，CI 檢查一致性，數量不可能再對不上。
- **README 列出不存在的技能**：`tw-edu-remotion-shorts`、`tw-edu-chatgpt-usecases`、
  `tw-edu-question-reviewer`。README 已重寫。
- **`tw-edu-citation-checker` 遺漏批次並行模式**。3 筆以上引用時召喚
  `citation-checker-worker` 的功能做於 2026-05-07 但從未回流 repo，本次併入。
- **`tw-edu-synchronizer` 宣告非法工具名 `Notion`**。該技能只產生本機
  `teacher-profile.md`，未使用 Notion，宣告已移除。
- **`tw-edu-anti-ai-assessment` 的垃圾目錄**：字面名為 `` `{references,scripts,assets}` ``
  的空目錄（`mkdir` brace expansion 未展開），已刪除。
- LICENSE 改用標準 MIT 全文，讓 GitHub 正確識別（原本被判定為 `NOASSERTION`，
  而 README badge 宣稱 MIT）。

### Added

- `AGENTS.md` 作為 repo 規範的單一真源，`CLAUDE.md` 為其 symlink
- 閘門 `scripts/verify_skill_frontmatter.py`、`verify_skill_links.py`、`gen_skill_index.py`
- `requirements.txt` 補齊 `reportlab`、`matplotlib`、`PyYAML`

### 暫不隨附

- **`tw-edu-remotion-shorts`** — 只有 `productions/ba-zi-ju/` 的影片產製腳本
  （Swift + Python），沒有 `SKILL.md`，不是可安裝的技能。待補完後再單獨加入。

### 已知待辦（P1）

21 支技能的 `license` / `whenToUse` / `metadata` 欄位尚未補齊，12 支缺 `author`。
`verify_skill_frontmatter.py` 目前以 warning 呈現，補齊後改用 `--strict` 升為錯誤。
`tw_edu_doc_utils.py` 仍有多份複本，待收斂為 `twa_edu_core` 套件。

---

## 前身：FW1201/tw-edu-skills

| 版本 | 日期 | 摘要 |
|---|---|---|
| v3.1 | 2026-04-27 | Codex / Antigravity 跨平台安裝說明 |
| v3.0 | 2026-04-27 | 技能套組擴充，共用協議層建立 |
| — | 2026-06-20 | `tw-edu-slides-creator` v4.0.0：改採 codex-ppt-style 圖片式簡報工作流 |
| — | 2026-05-23 | `tw-edu-slides-creator` v2.0：移轉至 open-slide（React/TSX/Tailwind） |

完整歷史見 [`FW1201/tw-edu-skills`](https://github.com/FW1201/tw-edu-skills) 的 `v3.1-final` tag。
