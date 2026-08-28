"""Fault ledger for the independent checker.

Every refusal the checker makes is recorded here with a fault class, so the
output can state WHICH invariant failed and how the checker mapped it onto
the frozen terminal set. Refusals are never merged into a generic error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Fault classes that force "could not check" (exit 3).
FAULT_MALFORMED_TRACE = "MALFORMED_TRACE"
FAULT_MISSING_TRACE = "MISSING_TRACE"
FAULT_CONTAMINATED_ROW = "CONTAMINATED_ROW"
FAULT_UNDECOMPOSABLE_COST = "UNDECOMPOSABLE_COST"
FAULT_NEGATIVE_COST_COMPONENT = "NEGATIVE_COST_COMPONENT"
FAULT_ACTIONS_DISAGREE_WITH_COMPONENTS = "ACTIONS_DISAGREE_WITH_COMPONENTS"
FAULT_MISSING_ACTIONS = "MISSING_ACTIONS"
FAULT_BUDGET_FLAG_INCONSISTENT = "BUDGET_FLAG_INCONSISTENT"
FAULT_STRATUM_ALIAS_COLLISION = "STRATUM_ALIAS_COLLISION"
FAULT_UNKNOWN_STRATUM = "UNKNOWN_STRATUM"
FAULT_UNKNOWN_ARM = "UNKNOWN_ARM"
FAULT_DUPLICATE_ROW = "DUPLICATE_ROW"
FAULT_INCONSISTENT_WORLD_STRATUM = "INCONSISTENT_WORLD_STRATUM"
FAULT_INCONSISTENT_WORLD_SEED = "INCONSISTENT_WORLD_SEED"
FAULT_ARM_COVERAGE = "ARM_COVERAGE"
FAULT_ORACLE_PLACEMENT = "ORACLE_PLACEMENT"
FAULT_PAIRING_INCOMPLETE = "PAIRING_INCOMPLETE"
FAULT_MISSING_GATE_CONSUMED_ARM = "MISSING_GATE_CONSUMED_ARM"
FAULT_DP_ORACLE_INFEASIBLE = "DP_ORACLE_INFEASIBLE"
FAULT_G7_INSTRUMENT = "G7_INSTRUMENT_FAULT"
FAULT_SEED_SENSITIVE_VERDICT = "SEED_SENSITIVE_VERDICT"
FAULT_EMPTY_COMPARISON_SET = "EMPTY_COMPARISON_SET"

# Fault classes for which a frozen terminal exists in EXPECTED_TERMINALS.json.
# Anything not listed here has NO frozen terminal, and the checker refuses to
# invent one: it emits terminal=null with NO_FROZEN_TERMINAL_MATCHES.
FAULT_TO_FROZEN_TERMINAL = {
    FAULT_UNDECOMPOSABLE_COST: "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE",
    FAULT_NEGATIVE_COST_COMPONENT: "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE",
    FAULT_ACTIONS_DISAGREE_WITH_COMPONENTS: "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE",
    FAULT_MISSING_ACTIONS: "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE",
    FAULT_DP_ORACLE_INFEASIBLE: "CANNOT_CHECK__DP_ORACLE_INFEASIBLE",
}

NO_FROZEN_TERMINAL = "NO_FROZEN_TERMINAL_MATCHES"

# Cap on how many example offenders are echoed per fault class, so a wholly
# broken trace file does not produce an unreadable report. Counts are exact.
MAX_EXAMPLES = 10


@dataclass
class Ledger:
    """Accumulates faults and warnings. Faults refuse; warnings do not."""

    faults: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    protocol_defects: list[str] = field(default_factory=list)

    def fault(self, fault_class: str, detail: str, examples: Any = None, count: int = 1) -> None:
        for entry in self.faults:
            if entry["fault_class"] == fault_class and entry["detail"] == detail:
                entry["count"] += count
                if examples is not None and len(entry["examples"]) < MAX_EXAMPLES:
                    entry["examples"].append(examples)
                return
        self.faults.append(
            {
                "fault_class": fault_class,
                "detail": detail,
                "count": count,
                "examples": [] if examples is None else [examples],
            }
        )

    def warn(self, warning_class: str, detail: str, examples: Any = None) -> None:
        for entry in self.warnings:
            if entry["warning_class"] == warning_class and entry["detail"] == detail:
                entry["count"] += 1
                if examples is not None and len(entry["examples"]) < MAX_EXAMPLES:
                    entry["examples"].append(examples)
                return
        self.warnings.append(
            {
                "warning_class": warning_class,
                "detail": detail,
                "count": 1,
                "examples": [] if examples is None else [examples],
            }
        )

    def defect(self, text: str) -> None:
        if text not in self.protocol_defects:
            self.protocol_defects.append(text)

    @property
    def refused(self) -> bool:
        return bool(self.faults)

    def fault_classes(self) -> list[str]:
        seen: list[str] = []
        for entry in self.faults:
            if entry["fault_class"] not in seen:
                seen.append(entry["fault_class"])
        return seen

    def frozen_terminal_for_faults(self) -> str | None:
        """Frozen CANNOT_CHECK terminal for the recorded faults, else None.

        Returns a terminal only when EVERY recorded fault class maps to the
        SAME frozen terminal. A mixed or unmapped fault set yields None, and
        the caller emits terminal=null rather than inventing an id.
        """
        mapped = {FAULT_TO_FROZEN_TERMINAL.get(fc) for fc in self.fault_classes()}
        if len(mapped) == 1:
            only = mapped.pop()
            return only
        return None
