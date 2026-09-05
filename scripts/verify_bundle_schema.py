#!/usr/bin/env python3
"""驗證 harness/bundle.yml 與 presets/*/preset.yml 合乎 schema，且宣告的路徑真的存在。

schema 合規還不夠——宣告了一個不存在的目錄，安裝時才會發現，
而且失敗訊息通常指不到問題點。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO / "harness" / "schema"


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def validate(instance, schema, errors: list[str], label: str) -> None:
    try:
        import jsonschema
    except ImportError:
        # 沒有 jsonschema 時退回必填欄位檢查，仍比完全不檢查好
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{label}: 缺少必填欄位 `{field}`")
        return
    validator = jsonschema.Draft202012Validator(schema)
    for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        loc = "/".join(str(x) for x in e.path) or "(根)"
        errors.append(f"{label}: {loc} — {e.message}")


def main() -> int:
    errors: list[str] = []

    bundle_path = REPO / "harness" / "bundle.yml"
    if not bundle_path.exists():
        print("❌ 找不到 harness/bundle.yml")
        return 1
    bundle = load_yaml(bundle_path)
    validate(bundle, json.loads((SCHEMA_DIR / "bundle.schema.json").read_text()),
             errors, "harness/bundle.yml")

    # 宣告的每一個目錄都必須存在
    for key, paths in (bundle.get("contributes") or {}).items():
        for rel in paths:
            if not (REPO / rel).is_dir():
                errors.append(f"harness/bundle.yml: contributes.{key} "
                              f"宣告的 `{rel}` 不存在")

    cap_path = REPO / "harness" / "capabilities.yml"
    known_caps = set((load_yaml(cap_path).get("capabilities") or {}))

    preset_schema = json.loads((SCHEMA_DIR / "preset.schema.json").read_text())
    presets = sorted(REPO.glob("presets/*/preset.yml"))
    skills = {p.name for p in REPO.glob("skills/*") if (p / "SKILL.md").is_file()}

    for path in presets:
        label = str(path.relative_to(REPO))
        preset = load_yaml(path)
        validate(preset, preset_schema, errors, label)
        if not isinstance(preset, dict):
            continue

        if preset.get("name") and preset["name"] != path.parent.name:
            errors.append(f"{label}: name `{preset['name']}` 與目錄名不一致")

        persona = preset.get("persona")
        if persona and not (path.parent / persona).is_file():
            errors.append(f"{label}: persona `{persona}` 不存在")

        caps = preset.get("capabilities") or {}
        allow, deny = set(caps.get("allow") or []), set(caps.get("deny") or [])
        for c in sorted((allow | deny) - known_caps):
            errors.append(f"{label}: 未知的能力名稱 `{c}`"
                          f"（須列於 harness/capabilities.yml）")
        for c in sorted(allow & deny):
            errors.append(f"{label}: `{c}` 同時出現在 allow 與 deny")

        # deny 的每一項都要在 DENIED.md 有交代，否則否決的理由會隨時間流失
        denied_md = path.parent / "DENIED.md"
        if deny:
            if not denied_md.is_file():
                errors.append(f"{label}: 有 deny 項目但缺少 DENIED.md")
            else:
                text = denied_md.read_text(encoding="utf-8")
                for c in sorted(deny):
                    if c not in text:
                        errors.append(
                            f"{label}: DENIED.md 未說明為何否決 `{c}`")

        for pattern in (preset.get("skills") or {}).get("include", []):
            import fnmatch
            if not any(fnmatch.fnmatch(s, pattern) for s in skills):
                errors.append(f"{label}: skills.include 的 `{pattern}` 沒有命中任何技能")

    if errors:
        print(f"❌ {len(errors)} 項 schema 問題：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✅ bundle.yml 與 {len(presets)} 個 preset 合乎 schema，"
          f"宣告的路徑全部存在")
    return 0


if __name__ == "__main__":
    sys.exit(main())
