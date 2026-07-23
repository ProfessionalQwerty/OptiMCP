"""In-process MCP round-trip through the FastMCP server."""

import asyncio
import json

from optimcp.server import mcp

CHECK_DOC = {
    "invoice": {"subtotal": 320, "tax": 25.6, "total": 345.6},
    "line_items": [{"amount": 100}, {"amount": 120}, {"amount": 110}],
}
CHECK_RULES = [
    {
        "id": "subtotal_matches_items",
        "lhs": {"kind": "ref", "path": "invoice.subtotal"},
        "op": "==",
        "rhs": {"kind": "agg", "fn": "sum", "path": "line_items[*].amount"},
    },
    {
        "id": "total_ok",
        "lhs": {"kind": "ref", "path": "invoice.total"},
        "op": "==",
        "rhs": {
            "kind": "calc",
            "fn": "add",
            "args": [
                {"kind": "ref", "path": "invoice.subtotal"},
                {"kind": "ref", "path": "invoice.tax"},
            ],
        },
    },
]


def _structured(raw):
    """Normalize FastMCP.call_tool output to the structured dict result."""
    if isinstance(raw, tuple):
        raw = raw[1]
    if isinstance(raw, dict):
        return raw.get("result", raw)
    return json.loads(raw[0].text)


def test_list_tools_exposes_verification_tools():
    async def go():
        return await mcp.list_tools()

    names = {t.name for t in asyncio.run(go())}
    assert {
        "verify_against_ruleset",
        "list_rulesets",
        "check_consistency",
        "capabilities",
    } == names


def test_list_rulesets_tool():
    async def go():
        return await mcp.call_tool("list_rulesets", {})

    out = _structured(asyncio.run(go()))
    assert "rulesets" in out
    assert isinstance(out["rulesets"], list)


def test_check_consistency_tool_round_trip():
    async def go():
        return await mcp.call_tool(
            "check_consistency", {"document": CHECK_DOC, "rules": CHECK_RULES}
        )

    report = _structured(asyncio.run(go()))
    assert report["consistent"] is False
    assert "subtotal_matches_items" in report["broken_rules"]


def test_capabilities_tool():
    async def go():
        return await mcp.call_tool("capabilities", {})

    caps = _structured(asyncio.run(go()))
    assert caps["primary_tool"] == "verify_against_ruleset"
    assert "verification_layer" in caps
    assert caps["verification_layer"]["daemon"]["token_env"] == "OPTIMCP_DAEMON_TOKEN"
    assert "optional_solver" not in caps
    cc = caps["check_consistency"]
    assert set(cc["expression_kinds"]) == {"lit", "ref", "agg", "calc"}
    assert "sum" in cc["aggregations"]
    assert "pct_change" in cc["arithmetic"]
