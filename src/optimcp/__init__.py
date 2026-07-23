"""OptiMCP - verification layer over agent structured emissions.

Use :func:`check_consistency` for one-shot checks, or register named rulesets
and run the self-hosted daemon for always-on monitoring with observe/refuse
policies. Every number is recomputed in exact Decimal arithmetic (no LLM).
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

__version__ = "0.4.0"

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
