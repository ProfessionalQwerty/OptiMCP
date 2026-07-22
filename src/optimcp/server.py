"""OptiMCP MCP server.

Exposes tools over MCP (stdio by default; optional HTTP):

* ``verify_against_ruleset`` - check a document against a *named* ruleset (daemon/store).
* ``list_rulesets``          - list registered rulesets.
* ``check_consistency``      - ad-hoc document + inline rules.
* ``capabilities``           - shapes/limits.

Optional constraint solving (``solve_decision``, repair) is in
:mod:`optimcp.solver` — install with ``pip install optimcp[solver]``.

Run with the ``optimcp`` console script or ``python -m optimcp.server``.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from optimcp.check import check_consistency as _check_consistency
from optimcp.check.rules import AGG_FNS, CALC_FNS, MAX_RULES, Rule
from optimcp.middleware.client import DaemonClientError, verify_local_or_remote
from optimcp.middleware.policy import result_as_tool_error
from optimcp.monitor.service import MonitorService, RulesetNotFound
from optimcp.monitor.store import MonitorStore

mcp = FastMCP(
    "optimcp",
    instructions=(
        "OptiMCP is the verification layer over whatever you write or fetch from "
        "systems of record. Prefer verify_against_ruleset with a registered "
        "ruleset_id for always-on checking (observe or refuse policy). Use "
        "check_consistency for one-shot ad-hoc rules. Every check recomputes "
        "numbers independently (no LLM, exact decimal arithmetic) and reports "
        "PROVABLY which rule broke."
    ),
)


@mcp.tool()
def verify_against_ruleset(
    ruleset_id: str,
    document: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Verify ``document`` against a named ruleset registered with the daemon/store.

    Talks to the local OptiMCP daemon when available (OPTIMCP_DAEMON_URL +
    OPTIMCP_DAEMON_TOKEN), otherwise uses the on-disk MonitorStore under
    OPTIMCP_HOME. When the ruleset policy is ``refuse`` and the document is
    inconsistent, ``refused`` is true and the agent must not treat the document
    as accepted.
    """
    try:
        result = verify_local_or_remote(
            ruleset_id,
            document,
            correlation_id=correlation_id,
            prefer_remote=True,
            source="mcp",
        )
    except DaemonClientError as exc:
        return {"ok": False, "error": str(exc), "status": getattr(exc, "status", None)}
    except RulesetNotFound as exc:
        return {"ok": False, "error": f"ruleset not found: {exc}"}
    payload = result.model_dump_report()
    payload["ok"] = not result.refused
    if result.refused:
        payload["agent_error"] = result_as_tool_error(result)
    return payload


@mcp.tool()
def list_rulesets() -> Dict[str, Any]:
    """List named rulesets registered in the local MonitorStore (OPTIMCP_HOME)."""
    rows = MonitorService(store=MonitorStore()).list_rulesets()
    return {
        "rulesets": [
            {
                "id": r.id,
                "version": r.version,
                "policy": r.policy,
                "source": r.source,
                "rule_count": len(r.rules),
                "description": r.description,
            }
            for r in rows
        ]
    }


@mcp.tool()
def check_consistency(
    document: Dict[str, Any], rules: List[Rule]
) -> Dict[str, Any]:
    """Check whether a JSON ``document`` obeys its declared numeric/logical ``rules``.

    Ad-hoc one-shot check (inline rules). For always-on monitoring prefer
    ``verify_against_ruleset`` with a registered ``ruleset_id``.
    """
    return _check_consistency(document, rules).model_dump()


@mcp.tool()
def capabilities() -> Dict[str, Any]:
    """Describe what this server can check and its limits."""
    return {
        "primary_tool": "verify_against_ruleset",
        "verification_layer": {
            "purpose": (
                "Always-on verification over agent structured emissions and "
                "systems-of-record documents via named rulesets."
            ),
            "tools": ["verify_against_ruleset", "list_rulesets", "check_consistency"],
            "daemon": {
                "url_env": "OPTIMCP_DAEMON_URL",
                "token_env": "OPTIMCP_DAEMON_TOKEN",
                "default_url": "http://127.0.0.1:8787",
                "auth": (
                    "Bearer token required on /v1/* unless loopback bind with "
                    "explicit --allow-unauthenticated-localhost"
                ),
            },
            "policies": ["observe", "refuse"],
        },
        "check_consistency": {
            "purpose": (
                "Ad-hoc: deterministically verify a JSON document against inline "
                "rules and report exactly which rule broke."
            ),
            "expression_kinds": ["lit", "ref", "agg", "calc"],
            "aggregations": sorted(AGG_FNS),
            "arithmetic": sorted(CALC_FNS),
            "operators": ["<=", ">=", "==", "!=", "<", ">"],
            "path_syntax": "dot paths with [i] indexing and [*] wildcards, e.g. line_items[*].amount",
            "tolerance": "per-rule abs_tol + rel_tol*|rhs|; comparisons run in exact Decimal arithmetic",
            "max_rules": MAX_RULES,
            "guarantee": (
                "No LLM is used; every number is recomputed independently. A "
                "rule that cannot be evaluated (missing/non-numeric field) is "
                "reported as failed, never silently skipped."
            ),
        },
        "optional_solver": {
            "install": "pip install optimcp[solver]",
            "module": "optimcp.solver",
            "tools": ["solve_decision", "verify_solution", "try_repair"],
        },
        "notes": [
            "Prefer named rulesets + daemon for production monitoring.",
            "Field/variable names are case-sensitive; unknown or missing names "
            "are reported, never silently ignored.",
        ],
    }


def main() -> None:
    """Console entry point for the ``optimcp`` script."""
    parser = argparse.ArgumentParser(description="OptiMCP MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="MCP transport (default: stdio, for Claude Desktop / Cursor / local agents).",
    )
    args = parser.parse_args()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
