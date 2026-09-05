---
name: twa-release-check
description: >
  twa-edu-harness 發版前載入。涵蓋閘門執行順序、CHANGELOG 撰寫、
  版本號決定、獨立版建置、tag 與 release 流程，以及發版後的驗證。
version: 1.0.0
author: 奇老師・數位敘事力社群
license: MIT
---

# 發版檢查

## 1. 閘門（全綠才繼續）

```bash
python scripts/verify_skill_frontmatter.py
python scripts/verify_skill_links.py
python scripts/verify_core_api.py
python scripts/verify_no_vendored_utils.py
python scripts/verify_agent_deps.py
python scripts/verify_agent_notes.py
python scripts/gen_skill_index.py --check
python scripts/smoke_test_scripts.py
```

## 2. 獨立版建置與驗證

```bash
python scripts/build_standalone_skills.py --out dist/skills
python scripts/verify_skill_links.py --root dist/skills --standalone
```

再實測一次真正的單支安裝：把 `dist/skills/tw-edu-lesson-plan-108/`
複製到一個乾淨目錄，確認四份共用協議都在檔案裡、腳本跑得動。

## 3. 版本號

| 改動 | 版本 |
|---|---|
| 修 bug、補文件 | patch |
| 新增技能、新增 frontmatter 欄位 | minor |
| 技能改名、移除欄位、目錄結構變動 | major |

每一個版本號都要有 `CHANGELOG.md` 條目——`verify_skill_frontmatter.py`
會檢查技能的 `version` 有對應紀錄。

## 4. CHANGELOG

寫「修好了什麼」與「為什麼那是問題」，不要只寫「更新了某某檔案」。
未來的讀者需要判斷這個版本值不值得升。

必寫的三個區塊：
- **Fixed** — 使用者會有感的修復
- **暫不隨附** — 刻意排除的東西（例如尚未完成的技能）
- **已知待辦** — 這一版沒做完的事

## 5. Tag 與 Release

```bash
git tag -a v<版本> -m "<一句話摘要>"
git push origin v<版本>
```

## 6. 發版後驗證

```bash
npx skills add FW1201/twa-edu-harness --all -a claude-code
```

安裝後檢查：技能數量正確、`/tw-edu-lesson-plan-108` 叫得起來、
產得出 .docx。

### 尚未能驗證的項目

Bundle / Preset 層的實機安裝**目前無法驗證**——本機沒有 ref-harness runtime。
取得環境後要補做：

- [ ] bundle 被 runtime 正確發現，21 支技能出現在模型的 catalog
- [ ] preset 載入後，工具清單只有 `capabilities.allow` 列的項目
- [ ] `capabilities.deny` 的項目確認**不在** catalog 中

在那之前，P2 / P3 的驗收只到「schema 合規 + generator 產出正確 + 文件齊全」。
不要在 README 或 CHANGELOG 宣稱實機測試過。
