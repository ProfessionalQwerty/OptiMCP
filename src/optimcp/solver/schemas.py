"""Function-calling schemas for the optional solver tools."""

from __future__ import annotations

from typing import Any, Dict

from optimcp.solver.spec import DecisionSpec

SOLVE_TOOL_NAME = "solve_decision"
SOLVE_TOOL_DESCRIPTION = (
    "Solve a decision-under-constraints problem and return an assignment that is "
    "independently verified to satisfy every declared constraint. Provide the "
    "decision as structured data (binary/integer variables, an objective to "
    "maximize/minimize, and hard constraints). Use this to produce a corrected, "
    "verified answer when check_consistency reports a violation on a linear "
    "numeric problem. IMPORTANT: use ONE consistent unit for every number across "
    "the whole spec - if costs are in thousands (e.g. 60 for $60k), the budget "
    "rhs must also be in thousands (100, not 100000). Read 'exactly N' / 'must be "
    "covered' as '==', not '<='."
)


def decision_spec_schema() -> Dict[str, Any]:
    """Raw JSON schema of the ``solve_decision`` input (a ``DecisionSpec``)."""
    return DecisionSpec.model_json_schema()


def solve_openai_tool() -> Dict[str, Any]:
    """``solve_decision`` for the OpenAI Chat Completions / Responses API."""
    return {
        "type": "function",
        "function": {
            "name": SOLVE_TOOL_NAME,
            "description": SOLVE_TOOL_DESCRIPTION,
            "parameters": decision_spec_schema(),
        },
    }


def solve_anthropic_tool() -> Dict[str, Any]:
    """``solve_decision`` for the Anthropic Messages API."""
    return {
        "name": SOLVE_TOOL_NAME,
        "description": SOLVE_TOOL_DESCRIPTION,
        "input_schema": decision_spec_schema(),
    }
