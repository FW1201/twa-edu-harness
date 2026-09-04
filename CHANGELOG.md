# CHANGELOG

本專案遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

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
