"""OptiMCP - verification layer over agent structured emissions.

OptiMCP checks whether structured output obeys declared numeric/logical rules
and *provably tells you which rule broke*. Use :func:`check_consistency` for
one-shot checks, or register named rulesets and run the self-hosted daemon for
always-on monitoring with observe/refuse policies.

No LLM is used inside OptiMCP: every number is recomputed in exact Decimal
arithmetic. Optional constraint solving lives in :mod:`optimcp.solver`
(``pip install optimcp[solver]``).
"""

from optimcp.check import (
    ConsistencyReport,
    Expr,
    Rule,
    RuleCheck,
    Ruleset,
    check_consistency,
)
from optimcp.monitor import (
    MonitorService,
    MonitorStore,
    RulesetRecord,
    VerifyResult,
    document_hash,
)

__version__ = "0.3.0"

__all__ = [
    "ConsistencyReport",
    "Expr",
    "MonitorService",
    "MonitorStore",
    "Rule",
    "RuleCheck",
    "Ruleset",
    "RulesetRecord",
    "VerifyResult",
    "check_consistency",
    "document_hash",
]
