"""面向模型的 108 課綱查詢工具（MCP）。

選 MCP 而非特定 harness runtime 的插件 API，有三個理由：
不引入 TypeScript build、是中性標準、Claude Code 現在就能直接用。

工具刻意設計成「查不到就明說查不到」。課綱代碼會被寫進教案送交課發會，
一個看起來正確但不存在的代碼，比一句「查無此代碼」有害得多。
"""
from __future__ import annotations

import json
import sys
from typing import Any

from twa_curriculum import default_store

TOOLS: list[dict[str, Any]] = [
    {
        "name": "curriculum_get",
        "description": (
            "依代碼取得單一 108 課綱指標的法定敘述。"
            "代碼不存在時回傳 exists=false——此時**不要**自行編造敘述，"
            "改用 curriculum_lookup 以關鍵詞尋找正確的代碼。"
        ),
        "inputSchema": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {
                    "type": "string",
                    "description": "指標代碼，如 國-J-B1、5-Ⅳ-2、Ab-Ⅳ-1。"
                                   "羅馬數字可用 Ⅳ 或 IV。",
                }
            },
        },
    },
    {
        "name": "curriculum_lookup",
        "description": (
            "依領域、教育階段、類型與關鍵詞查詢指標。"
            "用於「這個教學目標對應哪一條學習表現」這類問題。"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "領域/科目，如 國語文"},
                "level": {"type": "string", "enum": ["E", "J", "U"],
                          "description": "E 國小 / J 國中 / U 高中"},
                "kind": {"type": "string",
                         "enum": ["competency", "performance", "content"],
                         "description": "核心素養 / 學習表現 / 學習內容"},
                "keyword": {"type": "string", "description": "敘述中的關鍵詞"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "curriculum_verify",
        "description": (
            "批次查核一組代碼是否存在並取得官方敘述。"
            "**產出教案、試卷或課程計畫前，把要寫進去的每一個代碼都先送這裡查核。**"
            "實測顯示未經查核的產出，課綱對應有極高比例是錯的。"
        ),
        "inputSchema": {
            "type": "object",
            "required": ["codes"],
            "properties": {
                "codes": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
]


def handle(name: str, args: dict[str, Any]) -> dict[str, Any]:
    store = default_store()

    if name == "curriculum_get":
        ind = store.get(args["code"])
        if ind is None:
            return {
                "exists": False,
                "code": args["code"],
                "message": "此代碼不存在於已載入的領綱資料中。"
                           "不要自行編造敘述——改用 curriculum_lookup 找正確代碼。",
                "loadedDomains": store.domains,
            }
        return {"exists": True, **ind.as_dict()}

    if name == "curriculum_lookup":
        results = store.search(
            domain=args.get("domain"), level=args.get("level"),
            kind=args.get("kind"), keyword=args.get("keyword"),
            limit=int(args.get("limit", 20)))
        return {"count": len(results),
                "results": [i.as_dict() for i in results],
                "loadedDomains": store.domains}

    if name == "curriculum_verify":
        result = store.verify(args["codes"])
        bad = [c for c, v in result.items() if not v["exists"]]
        return {"results": result, "invalidCodes": bad,
                "allValid": not bad,
                "loadedDomains": store.domains}

    raise ValueError(f"未知的工具：{name}")


def build_server():
    """建立 MCP server（需要 `pip install mcp`）。"""
    from mcp.server import Server
    from mcp.types import TextContent, Tool

    server = Server("twa-curriculum")

    @server.list_tools()
    async def _list() -> list[Tool]:
        return [Tool(name=t["name"], description=t["description"],
                     inputSchema=t["inputSchema"]) for t in TOOLS]

    @server.call_tool()
    async def _call(name: str, arguments: dict) -> list[TextContent]:
        payload = handle(name, arguments or {})
        return [TextContent(
            type="text",
            text=json.dumps(payload, ensure_ascii=False, indent=1))]

    return server


def selftest() -> int:
    """不需要 mcp 套件也能驗證工具邏輯。"""
    store = default_store()
    print(f"已載入 {len(store)} 筆指標，領域：{', '.join(store.domains)}")
    print(f"提供 {len(TOOLS)} 個工具：{', '.join(t['name'] for t in TOOLS)}\n")

    checks = [
        ("curriculum_get", {"code": "國-J-B1"}, lambda r: r["exists"]),
        ("curriculum_get", {"code": "5-IV-2"}, lambda r: r["exists"]),
        ("curriculum_get", {"code": "語-J-B1"}, lambda r: not r["exists"]),
        ("curriculum_lookup", {"domain": "國語文", "level": "J",
                               "kind": "competency"},
         lambda r: r["count"] == 9),
        ("curriculum_verify", {"codes": ["國-J-B1", "語-J-B1"]},
         lambda r: r["invalidCodes"] == ["語-J-B1"]),
    ]
    failed = 0
    for name, args, ok in checks:
        try:
            result = handle(name, args)
            status = "✅" if ok(result) else "❌"
            failed += 0 if ok(result) else 1
        except Exception as exc:                     # noqa: BLE001
            status, failed = f"❌ {exc}", failed + 1
        print(f"  {status} {name}({json.dumps(args, ensure_ascii=False)})")

    print(f"\n{'✅ selftest 全過' if not failed else f'❌ {failed} 項失敗'}")
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    import asyncio
    from mcp.server.stdio import stdio_server

    async def _main():
        server = build_server()
        async with stdio_server() as (r, w):
            await server.run(r, w, server.create_initialization_options())

    asyncio.run(_main())
