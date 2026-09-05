---
name: twa-skill-author
description: >
  撰寫或修改 twa-edu-harness 的 tw-edu-* 技能時載入。
  涵蓋 frontmatter 契約 v1、description 與 whenToUse 的分工、
  shared/ 引用規則、scripts/smoke.yml 的必要性、references 的漸進揭露原則。
version: 1.0.0
author: 奇老師・數位敘事力社群
license: MIT
---

# 撰寫 tw-edu-* 技能

## 先跑一次現況

```bash
python scripts/verify_skill_frontmatter.py
python scripts/verify_skill_links.py
```

現況是綠的才動手。在紅燈上疊改動，會分不清是誰弄壞的。

## 目錄結構

```
skills/<name>/
├── SKILL.md          必要
├── references/       漸進揭露：模型需要時才讀，不要塞進 SKILL.md
└── scripts/
    ├── generate_*.py
    └── smoke.yml     有腳本就必須有
```

## Frontmatter 契約 v1

必填：`name`（kebab-case，**必須等於目錄名**）、`description`（≤300 字元）、
`version`（SemVer，且 CHANGELOG 要有對應條目）、`author`、`license`、
`whenToUse`、`metadata`。

### description 與 whenToUse 的分工

**`description` 負責召回（recall）** —— 寫觸發詞，讓模型在使用者提到相關字眼時找到你。

**`whenToUse` 負責精確度（precision）** —— 寫「什麼時候**不要**用我、該用哪一支」。

```yaml
whenToUse: >
  適用於單課或單一單元的教學設計。若要規劃整學期的課程地圖，
  改用 tw-edu-curriculum-mapper；若要的是專題式學習，改用 tw-edu-pbl-designer。
```

只寫「適用於 X」而不寫「不適用於 Y」，等於沒寫——那些資訊 description 已經有了。

### metadata

```yaml
metadata:
  role: teacher          # teacher | student | researcher
  category: 課程設計      # 與 README 索引的分類一致
  stage: [E, J, U]       # E 國小 / J 國中 / U 高中
  subjects: [全領域]
  outputs: [docx]        # 與 smoke.yml 的 output_ext 一致
  shared:                # 引用了哪幾份 shared/ 協議
    - concept-alignment
```

`shared` 列的每一份都必須存在於 `shared/`，gate 會檢查。

### disable-model-invocation

**預設不要設。** 設了就等於告訴註冊表「永遠不要自動叫我」，
那 description 裡的觸發詞就白寫了。

只有「改設定、不產出教學文件」的工具才該設 `true`
（目前只有 `tw-edu-synchronizer`）。

## 引用 shared/

一律寫 `../../shared/<name>.md`，並在 `metadata.shared` 宣告。

**不要**把協議內容複製進 SKILL.md —— 發版時 `build_standalone_skills.py`
會自動內聯，你手動複製只會產生第二份會過期的副本。

## 共用程式碼

Word 版面、色票、CJK 字型一律 `from twa_edu_core import *`。

**不要**在 `scripts/` 底下複製工具檔，也不要重新實作 `set_cell_bg()` 這類函式——
`verify_no_vendored_utils.py` 會擋。v3.x 曾有 15 份完全相同的 `tw_edu_doc_utils.py`。

腳本開頭用這段（讓已安裝與未安裝兩種情境都能跑）：

```python
try:
    from twa_edu_core import *
except ImportError:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "python"))
    from twa_edu_core import *
```

## 產圖要註冊中文字型

用 matplotlib 產圖時，繪圖前先呼叫 `register_cjk_fonts()`，
且**不要**在 `ax.text()` 指定 `fontfamily`——指定拉丁字型會讓中文變成空白方框。
`tw-edu-research-viz` 的 PRISMA 圖就因為硬寫 `fontfamily='DejaVu Sans'`
而長期產出滿版豆腐框。

## smoke.yml

```yaml
- script: generate_lesson_plan.py
  args: ["--subject", "國語文", "--grade", "國中八年級"]
  output_ext: docx
  min_bytes: 30000
  min_tables: 8
```

新增腳本卻沒寫這個檔，smoke gate 直接紅。這是刻意的：
v3.x 的 CI 硬編碼腳本清單，其中一支被刪除後 CI 就永遠是紅的。

## 依賴 subagent

若技能會召喚 subagent，定義必須放進本 repo 的 `agents/`。
放在 `~/.claude/agents/` 的定義不會隨 `npx skills add` 安裝，
使用者端會靜默失效。`verify_agent_deps.py` 會檢查。

## 完成前

```bash
python scripts/verify_skill_frontmatter.py
python scripts/verify_skill_links.py
python scripts/verify_no_vendored_utils.py
python scripts/verify_agent_deps.py
python scripts/smoke_test_scripts.py
python scripts/gen_skill_index.py        # 更新 README 表格
```

改動了結構或契約，寫一篇 Agent Note（見 `.agents/notes/README.md`）。
