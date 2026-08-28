"""Terminal selection, drawn ONLY from the frozen set.

The frozen terminal ids are read from EXPECTED_TERMINALS.json at runtime, not
hardcoded, and every id this module emits is validated against that file. When
no frozen terminal matches an observed condition the checker emits
terminal=null with NO_FROZEN_TERMINAL_MATCHES rather than inventing an id.

That case is real, not hypothetical: PROTOCOL says a G7 instrument fault
"forces CANNOT_CHECK", and contamination, coverage and pairing faults are all
mandated refusals, but EXPECTED_TERMINALS.json enumerates CANNOT_CHECK
terminals only for undecomposable cost traces, an infeasible DP oracle, a
failed anchor reproduction and checker disagreement. The gap is surfaced, not
papered over.

Composition is NON-COMPENSATORY, and G6 dominates G3: a cost advantage over
Active-VOI that a simple p/c baseline also achieves is not an ORION property,
so the p/c falsification is selected even when G3 passes.
"""

from __future__ import annotations

import json
from typing import Any

from . import _constants as K
from . import _faults as F

T_SUPPORTED = "H_SUPPORTED__SAFETY_PRICED_LEVEL_ORDERING"
T_PC_BASELINE = "H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION"
T_COST_RATIO = "H_FALSIFIED__COST_RATIO_GATE_MISSED"
T_DP_GAP = "H_FALSIFIED__DP_OPTIMALITY_GAP_EXCEEDED"
T_SUCCESS = "H_FALSIFIED__SUCCESS_NONINFERIORITY_FAILED"
T_FORBIDDEN = "H_FALSIFIED__FORBIDDEN_MUTATION_OBSERVED"
T_ATTRIBUTION = "H_FALSIFIED__ADVANTAGE_PERSISTS_ON_ASSUMPTION_VIOLATION_CONTROLS"
T_BOUNDED = "H_BOUNDED__ECONOMY_ON_A_SUBFAMILY_ONLY"
T_DISAGREEMENT = "CANNOT_CHECK__CHECKER_DISAGREEMENT"


def load_frozen_terminals(path: str) -> tuple[list[str], dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        doc = json.load(handle)
    ids = [entry["id"] for entry in doc.get("terminals", [])]
    classes = {entry["id"]: entry.get("class") for entry in doc.get("terminals", [])}
    return ids, classes


def select(analysis: dict[str, Any], ledger: F.Ledger, frozen_ids: list[str]) -> dict[str, Any]:
    """Choose the terminal. Every failing gate is reported, not just the first."""
    gates = analysis["gates"]

    def state(gate_id: str) -> str:
        gate = gates.get(gate_id, {})
        if not gate.get("measured"):
            return "UNMEASURED"
        return "PASS" if gate.get("passed") else "FAIL"

    gate_states = {gid: state(gid) for gid in ("G1", "G2", "G3", "G4", "G5", "G6", "G7")}
    failing = [gid for gid, st in gate_states.items() if st == "FAIL"]
    unmeasured = [gid for gid, st in gate_states.items() if st == "UNMEASURED"]

    reasoning: list[str] = []
    terminal: str | None = None

    # ---- refusals first --------------------------------------------------
    if ledger.refused:
        terminal = ledger.frozen_terminal_for_faults()
        classes = sorted(ledger.fault_classes())
        if terminal is None:
            reasoning.append(
                "Refused on fault classes "
                + ", ".join(classes)
                + ". EXPECTED_TERMINALS.json enumerates no CANNOT_CHECK terminal for "
                "this fault set, so no terminal is selected."
            )
        else:
            reasoning.append(
                "Refused on fault classes " + ", ".join(classes) + f" -> {terminal}."
            )
    elif "G4" in unmeasured:
        # An unmeasured gate is never a passed gate. G4 has its own frozen
        # CANNOT_CHECK terminal because the optimality gap has no denominator.
        terminal = "CANNOT_CHECK__DP_ORACLE_INFEASIBLE"
        reasoning.append(
            "G4 is UNMEASURED: the exact DP oracle provides no denominator, so the "
            "optimality gap is unmeasured rather than satisfied."
        )
    elif unmeasured:
        reasoning.append(
            "Gates " + ", ".join(unmeasured) + " are UNMEASURED and no frozen terminal "
            "covers an unmeasured gate outside G4, so no terminal is selected."
        )
    else:
        # ---- non-compensatory composition, declared precedence -----------
        if gate_states["G1"] == "FAIL":
            terminal = T_SUCCESS
            reasoning.append(
                "G1 fails, so the conditional-on-equal-gates premise for any cost "
                "reading fails and no cost figure is admissible."
            )
        elif gate_states["G2"] == "FAIL":
            terminal = T_FORBIDDEN
            reasoning.append(
                "G2 fails on an A3-holding stratum: the safety property that the "
                "filtration exists to buy does not hold."
            )
        elif gate_states["G6"] == "FAIL":
            terminal = T_PC_BASELINE
            reasoning.append(
                "G6 dominates G3: gain_per_cost_greedy achieves equal success and "
                "safety without a demonstrable ORION cost advantage, so the residual "
                "belongs to p/c ordering (Theorem A, donor-owned) and not to the "
                "responsibility filtration"
                + (" even though G3 passes." if gate_states["G3"] == "PASS" else ".")
            )
        elif gate_states["G5"] == "FAIL":
            terminal = T_ATTRIBUTION
            reasoning.append(
                "G5 fails: the advantage persists where the theorem's assumptions are "
                "broken, so the theorem is not the explanation of the effect."
            )
        elif gate_states["G4"] == "FAIL":
            terminal = T_DP_GAP
            reasoning.append("G4 fails: ORION is materially suboptimal where its own theorem holds.")
        elif gate_states["G3"] == "FAIL":
            terminal = T_COST_RATIO
            reasoning.append("G3 fails: the cost ratio against the faithful comparator is not met.")
        else:
            bounded = _bounded_subfamily(analysis)
            if bounded["is_subfamily_only"]:
                terminal = T_BOUNDED
                reasoning.append(
                    "All gates hold, but the cost advantage is present on only "
                    f"{bounded['strata_with_advantage']} of the theorem-valid strata "
                    f"{bounded['theorem_valid_strata']}. Under the global-recovery "
                    "doctrine this is intermediate, not a bounded success."
                )
            else:
                terminal = T_SUPPORTED
                reasoning.append(
                    "G1, G2, G4, G5 and G7 all hold, G3 holds and G6 shows "
                    "gain_per_cost_greedy does not match or beat ORION."
                )

    if terminal is not None and terminal not in frozen_ids:
        # A terminal outside the frozen set is a checker defect, not a result.
        reasoning.append(
            f"Selected terminal {terminal!r} is absent from EXPECTED_TERMINALS.json; "
            "refusing to emit it."
        )
        terminal = None

    return {
        "terminal": terminal,
        "terminal_status": F.NO_FROZEN_TERMINAL if terminal is None else "SELECTED",
        "gate_states": gate_states,
        "failing_gates": failing,
        "unmeasured_gates": unmeasured,
        "composition": "NON_COMPENSATORY; G6 dominates G3",
        "selection_reasoning": reasoning,
        "frozen_terminal_set_size": len(frozen_ids),
    }


def _bounded_subfamily(analysis: dict[str, Any]) -> dict[str, Any]:
    """All gates hold on some but not all theorem-valid strata."""
    per_stratum = analysis["gates"]["G3"]["components"].get("per_stratum", {})
    theorem_strata = [s for s in K.THEOREM_VALID_STRATA if s in per_stratum]
    with_advantage = []
    for stratum in theorem_strata:
        entry = per_stratum[stratum]
        point = entry["point"].get("ratio")
        ci_high = (entry.get("bootstrap") or {}).get("ci_high")
        if point is not None and ci_high is not None:
            if point < K.G3_COST_RATIO_THRESHOLD and ci_high < K.G3_COST_RATIO_THRESHOLD:
                with_advantage.append(stratum)
    return {
        "theorem_valid_strata": theorem_strata,
        "strata_with_advantage": with_advantage,
        "is_subfamily_only": bool(
            theorem_strata and with_advantage and len(with_advantage) < len(theorem_strata)
        ),
    }
