# 教師流程實測

一次完整備課的實際產出。所有數字都是實跑後量到的，不是預期值。

## 情境

國中八年級國語文，翰林版〈背影〉，3 節課。

## 產出

| # | 技能 | 檔案 | 大小 | 表格 |
|---|---|---|---|---|
| 1 | `tw-edu-lesson-plan-108` | 教案 .docx | 45 KB | 12 |
| 2 | `tw-edu-worksheet-creator` | 學習單 .docx | 39 KB | 6 |
| 3 | `tw-edu-rubric-designer` | 評量規準 .docx | 39 KB | 3 |
| 4 | `tw-edu-exam-generator` | 段考試卷 .docx | 39 KB | 2 |

## 教案的課綱對應（實際內容）

**核心素養**
- 語-J-B1：運用國語文表情達意，增進閱讀理解，提升欣賞及評析能力
- 語-J-A2：透過欣賞文學作品，培養思辨能力，建構正向價值觀
- 語-J-C1：透過文學作品認識倫理課題，以適切態度與人互動

**學習表現**
- 5-Ⅳ-2：能理解並分析文本中的語句、段落、篇章結構及寫作手法
- 5-Ⅳ-5：能閱讀不同時代的文學作品，感受其文化意涵
- 6-Ⅳ-2：能運用修辭策略，增強表達效果

**學習內容**
- Ab-Ⅳ-1、Ac-Ⅳ-3、Ca-Ⅳ-1、Da-Ⅳ-1

Bloom 分層（記憶 / 理解 / 分析）有寫進教學活動。

## ⚠️ 這裡有一個目前無法解決的問題

**上面那些代碼的真偽，今天沒有辦法用程式驗證。**

它們來自技能 `references/` 底下的 markdown，是模型讀進 context 再寫出來的。
沒有任何閘門能檢查 `5-Ⅳ-2` 這個代碼是否真的存在於國語文領綱、
或者它的敘述是否被改寫過。

模型幻覺一個格式正確但不存在的代碼，產出看起來會**完全一樣**。
而教師會把這份教案送交課發會。

這正是 P4（課綱 Capability Seam）要解決的事：把課綱從「模型讀的 markdown」
變成「模型呼叫的 tool」，查表回傳，代碼保證存在，而且可以寫測試驗證。

在 P4 完成之前，`persona.md` 要求模型「不確定的指標代碼就不要寫」——
但那是靠指示，不是靠機制。

## 重現方式

```bash
python skills/tw-edu-lesson-plan-108/scripts/generate_lesson_plan.py \
  --subject 國語文 --title 背影 --grade 國中八年級 --publisher 翰林 \
  --periods 3 --teacher 吳老師 --school 桃園市立範例國中 \
  --output 教案-背影.docx
```

其餘三支見 `scripts/smoke.yml` 的參數。

## Preset 層尚未實測

本文測的是**技能層**——教師在 Claude Code 裡實際會遇到的流程。

`presets/twa-teacher/` 的 persona 與能力邊界**還沒有實機驗證**，
因為開發機上沒有 harness runtime。待驗收項目見
`.agents/skills/twa-release-check/`。
