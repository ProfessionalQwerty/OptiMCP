"""Function-calling tool schemas for non-MCP agents (OpenAI / Anthropic shapes)."""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field

from optimcp.check.rules import Rule

TOOL_NAME = "check_consistency"
TOOL_DESCRIPTION = (
    "Verify a JSON document against numeric/logical rules and report which rule "
    "broke (computed vs expected, with delta). Exact Decimal arithmetic, no LLM. "
    "Expressions: lit, ref, agg (sum/avg/min/max/count), calc "
    "(add/sub/mul/div/neg/abs/round/pow/pct_change)."
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
