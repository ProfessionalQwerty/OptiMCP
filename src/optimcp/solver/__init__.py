"""Optional constraint solver and repair path (``pip install optimcp[solver]``)."""

from optimcp.solver.repair import build_repair_spec, try_repair
from optimcp.solver.result import ConstraintCheck, DecisionResult, VerificationCertificate
from optimcp.solver.solve import solve_decision
from optimcp.solver.spec import (
    ConstraintSpec,
    DecisionSpec,
    ObjectiveSpec,
    Term,
    VariableSpec,
)
from optimcp.solver.verify import verify_assignment

__all__ = [
    "ConstraintCheck",
    "ConstraintSpec",
    "DecisionResult",
    "DecisionSpec",
    "ObjectiveSpec",
    "Term",
    "VariableSpec",
    "VerificationCertificate",
    "build_repair_spec",
    "solve_decision",
    "try_repair",
    "verify_assignment",
]
