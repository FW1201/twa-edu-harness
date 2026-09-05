#!/usr/bin/env python3
"""把中性的 bundle / preset 宣告，轉為特定 harness runtime 的設定檔。

產物一律輸出到 dist/（gitignored）。**repo 內不 commit 任何 runtime 專屬設定，
也不出現任何上游專案的名稱或套件名** —— 理由見
.agents/notes/implemented/architecture/2026-09-05-runtime-neutral-bundle.md

對應表在 harness/adapters/<target>.yml。若對應表尚未填寫（status: unmapped），
產物會標示為未驗證草稿，且不會假裝那是可用的設定。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
HARNESS = REPO / "harness"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build(bundle: dict, presets: list[dict], mapping: dict) -> dict:
    cap_map = mapping.get("capabilityMap") or {}
    provider = mapping.get("skillProvider") or {}
    unmapped: list[str] = []

    def plugin_for(cap: str) -> str | None:
        name = (cap_map.get(cap) or {}).get("pluginName")
        if not name:
            unmapped.append(cap)
        return name

    out = {
        "_generated_by": "scripts/gen_harness_adapter.py",
        "_source": "harness/bundle.yml",
        "_target": mapping.get("target"),
        "_status": mapping.get("status", "unmapped"),
        "bundle": {
            "id": bundle["id"],
            "providerName": bundle["providerName"],
            "skillProvider": {
                "pluginName": provider.get("pluginName"),
                "config": {
                    (provider.get("configKeys") or {}).get("providerName")
                    or "providerName": bundle["providerName"],
                    (provider.get("configKeys") or {}).get("skillDirs")
                    or "skillDirs": bundle["contributes"]["skillDirs"],
                },
            },
        },
        "presets": [],
    }
    if not provider.get("pluginName"):
        unmapped.append("skillProvider")

    for p in presets:
        caps = p["capabilities"]
        out["presets"].append({
            "name": p["name"],
            "displayName": p["displayName"],
            "persona": p["persona"],
            "plugins": [plugin_for(c) for c in caps["allow"]],
            "disabledPlugins": [plugin_for(c) for c in caps["deny"]],
            "skills": p.get("skills", {}),
            "context": p.get("context", {}),
        })

    out["_unmapped"] = sorted(set(unmapped))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="ref-harness")
    ap.add_argument("--out", default="dist/adapters")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    mapping_path = HARNESS / "adapters" / f"{args.target}.yml"
    if not mapping_path.exists():
        print(f"❌ 找不到對應表 {mapping_path.relative_to(REPO)}")
        return 1

    bundle = load(HARNESS / "bundle.yml")
    mapping = load(mapping_path)
    presets = [load(p) for p in sorted(REPO.glob("presets/*/preset.yml"))]

    result = build(bundle, presets, mapping)
    unmapped = result["_unmapped"]

    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        out_dir = REPO / args.out / args.target
        out_dir.mkdir(parents=True, exist_ok=True)
        target_file = out_dir / "config.json"
        target_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(f"已輸出 {target_file.relative_to(REPO)}")

    print(f"  bundle: {result['bundle']['id']}"
          f"（provider: {result['bundle']['providerName']}）")
    print(f"  preset: {len(result['presets'])} 個")

    if unmapped:
        print(f"\n⚠️  對應表尚未填寫 {len(unmapped)} 項："
              f"{', '.join(unmapped)}")
        print("    產物為未驗證草稿，不可直接使用。"
              f"填寫方式見 harness/adapters/{args.target}.yml 的註解。")
    else:
        print("\n✅ 對應表完整")
    return 0


if __name__ == "__main__":
    sys.exit(main())
