"""Deterministic consistency checking for structured JSON documents."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Union

from optimcp.check.eval import check_document, check_rule
from optimcp.check.result import ConsistencyReport, RuleCheck
from optimcp.check.rules import Expr, Rule, Ruleset

RulesArg = Union[Ruleset, Mapping[str, Any], Iterable[Any]]


def _as_ruleset(rules: RulesArg) -> Ruleset:
    if isinstance(rules, Ruleset):
        return rules
    if isinstance(rules, Mapping):
        if "rules" in rules:
            return Ruleset.model_validate(rules)
        return Ruleset(rules=[Rule.model_validate(rules)])
    return Ruleset(rules=[Rule.model_validate(r) for r in rules])


def check_consistency(document: Any, rules: RulesArg) -> ConsistencyReport:
    """Check ``document`` against ``rules`` and return a :class:`ConsistencyReport`."""
    return check_document(document, _as_ruleset(rules))


__all__ = [
    "check_consistency",
    "check_document",
    "check_rule",
    "ConsistencyReport",
    "Expr",
    "Rule",
    "RuleCheck",
    "Ruleset",
]
