# Agent Note: Skill 名稱維持 tw-edu-* 前綴

Status: implemented

## Problem

repo 從 `tw-edu-skills` 改為 `twa-edu-harness` 後，21 支技能是否應一併改名為 `twa-edu-*`？
產品層與技能層前綴不一致，看起來像是沒改乾淨。

## Decision

不改。分層命名：`twa-*` 是產品層（harness / bundle / preset），`tw-edu-*` 是技能層。

技能的 `name` 是註冊表的唯一鍵，沒有 alias 或轉址機制。改名等於讓所有既有的
`/tw-edu-lesson-plan-108` 呼叫、所有教學講義、所有工作坊教材同時失效。
觸發詞已經被使用者記住，那是這 21 支技能最有價值的資產。

## Alternatives considered

- **全面改名 + MIGRATION.md 對照表**：成本是 21 支 × (改 frontmatter + 改 README +
  改所有外部引用)，還要至少半年的過渡公告。只有在同時收編 `tw-stu-*` 與
  `tw-research-*`、需要統一命名空間時才值得。
- **雙名並存（建 shim）**：會讓模型的 catalog 出現兩個入口做同一件事，
  違反「一個能力一個入口」。

## Consequences

README 必須明講兩層命名的關係，否則使用者會以為 repo 改名沒改完。
未來若真要統一命名空間，這個決策要重新檢視。
