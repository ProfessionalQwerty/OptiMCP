"""Optional repair bridge (requires optimcp[solver])."""

import pytest

ortools = pytest.importorskip("ortools")

from optimcp.check.rules import Expr, Rule, Ruleset
from optimcp.solver.repair import build_repair_spec, try_repair

LINEAR_RULES = Ruleset(
    rules=[
        Rule.model_validate(
            {
                "id": "budget",
                "lhs": {
                    "kind": "calc",
                    "fn": "add",
                    "args": [
                        {"kind": "ref", "path": "a"},
                        {"kind": "ref", "path": "b"},
                    ],
                },
                "op": "<=",
                "rhs": {"kind": "lit", "value": 100},
            }
        )
    ]
)

VARIABLES = [
    {"name": "a", "kind": "integer", "lb": 0, "ub": 100},
    {"name": "b", "kind": "integer", "lb": 0, "ub": 100},
]

OBJECTIVE = {
    "sense": "maximize",
    "terms": [{"vars": ["a"], "coeff": 3}, {"vars": ["b"], "coeff": 2}],
}


def test_build_repair_spec_and_solve():
    spec = build_repair_spec(LINEAR_RULES, variables=VARIABLES, objective=OBJECTIVE)
    assert spec is not None
    result = try_repair(LINEAR_RULES, variables=VARIABLES, objective=OBJECTIVE)
    assert result is not None
    assert result.feasible


def test_nonlinear_ruleset_is_not_repairable():
    nonlinear = Ruleset(
        rules=[
            Rule.model_validate(
                {
                    "id": "agg",
                    "lhs": {"kind": "agg", "fn": "sum", "path": "items[*].x"},
                    "op": "==",
                    "rhs": {"kind": "lit", "value": 1},
                }
            )
        ]
    )
    assert build_repair_spec(nonlinear, variables=VARIABLES, objective=OBJECTIVE) is None
    assert try_repair(nonlinear, variables=VARIABLES, objective=OBJECTIVE) is None
