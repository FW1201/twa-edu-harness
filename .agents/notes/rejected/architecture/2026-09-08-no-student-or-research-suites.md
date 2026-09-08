# Agent Note: 不整併學生與學術研究技能套組

Status: rejected

## Problem

`FW1201/tw-stu-skills`（學生自學，10 支）與 `FW1201/tw-research-skills`
（學術研究，25 支）是同一位作者維護的平行 repo。

原本的升級計畫把它們列為 Phase 5：整併進本 repo 成為
`twa-student` / `twa-researcher` preset，形成完整的四角色 harness。
理由是三組技能共用同一套 frontmatter 契約、閘門與共用協議，
維護一套基座比維護三套省事。

## Decision

**不整併。本專案只做教師端。**（2026-09-08 擁有者明確界定）

服務對象是現場教師：備課、命題、評量、班級經營、親師溝通、校內行政，
以及教師自己的專業發展（行動研究、研習教材、投稿）。

學生自學工具與學術研究工具留在各自的 repo。

## 為什麼「共用基座」不足以構成整併的理由

技術上共用是真的，但 **preset 的價值在於限制**，而限制是隨服務對象而定的。

`twa-teacher` 關掉 `subagent`，理由是「教案生成是線性工作流，
且 token 成本對教師不透明」。這個判斷對研究者不成立——
批次文獻查核天生可平行，研究者也對成本有預期。

一個 repo 裡放三種互相矛盾的邊界設定，等於沒有邊界設定。
真正共用的是 frontmatter 契約與閘門腳本，那些可以獨立抽成套件再共用，
不需要把技能也搬進來。

## Consequences

- 已移除本 repo 內的 `presets/twa-researcher/`（內容保留在 git 歷史，
  必要時可還原）。
- 三支原本標為 `researcher` / `student` 的技能**保留**，
  但改標 `role: teacher` 並重寫 `whenToUse` 為教師情境：
  - `tw-edu-learning-portfolio` — 高中導師指導學生製作學習歷程檔案
  - `tw-edu-citation-checker` — 教師檢核研習教材與投稿的引用
  - `tw-edu-research-viz` — 教師行動研究的流程圖與架構圖
- 新增技能的判準：**想不出教師端的使用情境，就不屬於這個 repo。**
  `metadata.role` 一律為 `teacher`，`verify_skill_frontmatter.py` 會檢查。
