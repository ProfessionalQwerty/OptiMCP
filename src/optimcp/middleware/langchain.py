"""LangChain StructuredTool wrapping ``check_consistency``."""

from __future__ import annotations

from typing import Any

from optimcp.check import check_consistency as _check_consistency
from optimcp.schemas import TOOL_DESCRIPTION, TOOL_NAME, CheckConsistencyArgs


def build_check_consistency_tool() -> Any:
    """Return a LangChain ``StructuredTool`` wrapping ``check_consistency``."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "LangChain is required. Install with `pip install optimcp[langchain]`."
        ) from exc

    def _run(**kwargs: Any) -> dict:
        args = CheckConsistencyArgs.model_validate(kwargs)
        return _check_consistency(args.document, args.rules).model_dump()

    return StructuredTool.from_function(
        func=_run,
        name=TOOL_NAME,
        description=TOOL_DESCRIPTION,
        args_schema=CheckConsistencyArgs,
    )
