# Agent Note: 用 CI 掃描強制執行上游名稱的限制

Status: implemented

## Problem

擁有者要求本 repo 不得出現某上游 harness 專案的名稱與套件前綴（一律稱 `ref-harness`）。

這種「請記得不要寫某些字」的約定，靠人記是撐不住的——寫程式時很容易順手打出
最自然的名字，尤其是在描述架構來源的時候。而這個 repo 預計會轉為 public，
一旦寫進 git 歷史就洗不掉了。

## Decision

`scripts/verify_no_vendor_names.py` 在 CI 掃描所有版控中的文字檔。

受限字串以 **base64 存放**，讓這支 gate 本身不含明文。否則會有兩個問題：
掃描器會掃到自己（永遠紅燈），而且這支腳本本身就成了那些字串進入 repo 的破口。

輸出只指出「檔案:行號 出現受限名稱（第 N 項）」，不把命中的字串印出來——
CI log 也是會被看到的地方。

## Alternatives considered

- **只寫進 AGENTS.md 當規範**：人會忘記，而且 public repo 的 git 歷史不可逆。
- **用 pre-commit hook**：只擋本機，CI 才是最後一道。兩者可並存，但 CI 是必要的。

## Consequences

新增受限字串時改 `_ENCODED` 陣列。要注意誤判——若某個受限字串剛好是常用詞，
會擋到無辜的內容；目前的五個字串都夠特殊，暫時沒有這個問題。
