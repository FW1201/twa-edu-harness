#!/usr/bin/env python3
"""動態列舉所有生成腳本並實際執行，驗證真的產得出文件。

**必須動態列舉，不可硬編碼清單。**
舊 repo 的 CI 把腳本路徑寫死，其中一支在 2026-05-11 被刪除後，
CI 就永遠是紅的，於是沒人看 CI，於是問題不斷累積。這道 gate 的存在
是為了讓那件事在結構上不可能重演：腳本從檔案系統列舉，測試參數
由各 skill 自己的 scripts/smoke.yml 提供，兩者缺一都會紅。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def load_cases(scripts_dir: Path) -> list[dict]:
    f = scripts_dir / "smoke.yml"
    if not f.exists():
        return []
    return yaml.safe_load(f.read_text(encoding="utf-8")) or []


def count_tables(path: Path) -> int | None:
    if path.suffix != ".docx":
        return None
    try:
        from docx import Document
    except ImportError:
        return None
    return len(Document(str(path)).tables)


def run_case(script: Path, case: dict, out_dir: Path,
             python: str) -> list[str]:
    errors: list[str] = []
    ext = case.get("output_ext", "docx")
    out = out_dir / f"{script.parent.parent.name}.{ext}"
    args = [str(a) for a in case.get("args", [])] + ["--output", str(out)]

    proc = subprocess.run([python, str(script), *args],
                          capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
        errors.append(f"{script.relative_to(REPO)}: 執行失敗\n      "
                      + "\n      ".join(tail))
        return errors

    if not out.exists():
        errors.append(f"{script.relative_to(REPO)}: 未產生 {out.name}")
        return errors

    size = out.stat().st_size
    min_bytes = case.get("min_bytes", 0)
    if size < min_bytes:
        errors.append(f"{script.relative_to(REPO)}: 產出 {size} bytes，"
                      f"低於門檻 {min_bytes}")

    min_tables = case.get("min_tables")
    if min_tables is not None:
        tables = count_tables(out)
        if tables is not None and tables < min_tables:
            errors.append(f"{script.relative_to(REPO)}: 產出 {tables} 個表格，"
                          f"低於門檻 {min_tables}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", default=sys.executable,
                    help="執行腳本用的直譯器")
    ap.add_argument("--keep", action="store_true", help="保留產出供檢視")
    args = ap.parse_args()

    scripts = sorted(REPO.glob("skills/*/scripts/generate_*.py"))
    if not scripts:
        print("❌ 找不到任何 generate_*.py")
        return 1

    errors: list[str] = []
    ran = 0
    out_dir = Path(tempfile.mkdtemp(prefix="twa-smoke-"))

    for script in scripts:
        cases = load_cases(script.parent)
        mine = [c for c in cases if c.get("script") == script.name]
        if not mine:
            errors.append(
                f"{script.relative_to(REPO)}: scripts/smoke.yml 沒有對應條目"
                "（新增腳本時必須一併補上）")
            continue
        for case in mine:
            errors.extend(run_case(script, case, out_dir, args.python))
            ran += 1

    if args.keep:
        print(f"產出保留於 {out_dir}")
    else:
        shutil.rmtree(out_dir, ignore_errors=True)

    if errors:
        print(f"❌ {len(errors)} 項 smoke test 失敗：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✅ {len(scripts)} 支生成腳本、{ran} 個測試案例全部產出成功")
    return 0


if __name__ == "__main__":
    sys.exit(main())
