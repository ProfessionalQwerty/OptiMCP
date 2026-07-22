"""Function-calling tool schemas for non-MCP agents.

Exports JSON schemas for ``check_consistency`` in the shapes OpenAI and Anthropic
expect. Optional solver schemas live in :mod:`optimcp.solver.schemas`.
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field

from optimcp.check.rules import Rule

TOOL_NAME = "check_consistency"
TOOL_DESCRIPTION = (
    "Verify that a JSON document obeys its declared numeric/logical rules, and "
    "report PROVABLY which rule broke (computed value vs expected value, with the "
    "delta). Rules are pure data checked with exact arithmetic and no LLM. Each "
    "rule is lhs <op> rhs, where an expression is a literal ({'kind':'lit',"
    "'value':N}), a field ref ({'kind':'ref','path':'invoice.total'}), an "
    "aggregation over a wildcard path ({'kind':'agg','fn':'sum','path':"
    "'line_items[*].amount'}), or arithmetic ({'kind':'calc','fn':'sub','args':"
    "[...]}; fns: add,sub,mul,div,neg,abs,round,pow,pct_change). Use this to catch "
    "totals that don't match their line items, growth percentages computed the "
    "wrong way (pct_change(old,new)=(new-old)/old*100), allocations that don't sum "
    "to the budget, and similar failures - instead of trusting your own arithmetic."
)


class CheckConsistencyArgs(BaseModel):
    """Arguments for the ``check_consistency`` tool."""

    document: Dict[str, Any] = Field(
        ..., description="The JSON object to audit (budget, invoice, schedule, table...)."
    )
    rules: list[Rule] = Field(
        ..., description="Declared rules; each asserts lhs <op> rhs over the document."
    )


def check_consistency_schema() -> Dict[str, Any]:
    """Raw JSON schema of the ``check_consistency`` input."""
    return CheckConsistencyArgs.model_json_schema()


def openai_tool() -> Dict[str, Any]:
    """``check_consistency`` for the OpenAI Chat Completions / Responses API."""
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": TOOL_DESCRIPTION,
            "parameters": check_consistency_schema(),
        },
    }


def anthropic_tool() -> Dict[str, Any]:
    """``check_consistency`` for the Anthropic Messages API."""
    return {
        "name": TOOL_NAME,
        "description": TOOL_DESCRIPTION,
        "input_schema": check_consistency_schema(),
    }
