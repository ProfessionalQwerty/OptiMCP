"""LangChain StructuredTool for check_consistency."""

import pytest

langchain_core = pytest.importorskip("langchain_core")

from optimcp.middleware.langchain import build_check_consistency_tool


def test_build_check_consistency_tool():
    tool = build_check_consistency_tool()
    assert tool.name == "check_consistency"
    out = tool.invoke(
        {
            "document": {"a": 1, "b": 1},
            "rules": [
                {
                    "id": "eq",
                    "lhs": {"kind": "ref", "path": "a"},
                    "op": "==",
                    "rhs": {"kind": "ref", "path": "b"},
                }
            ],
        }
    )
    assert out["consistent"] is True
