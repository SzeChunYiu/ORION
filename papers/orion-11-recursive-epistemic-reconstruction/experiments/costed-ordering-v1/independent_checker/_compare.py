"""Field-by-field comparison against a supplied RESULT_V1.json.

Two tiers, because they are not the same kind of quantity:

* EXACT fields are deterministic functions of the traces -- counts, rates,
  mean costs, matched-set sizes, point ratios, gate booleans, the terminal.
  Two correct implementations must agree on these to floating tolerance. Any
  difference is a disagreement.

* TOLERANCE fields are Monte-Carlo estimates -- bootstrap bounds and
  p-values. Identical integer seeds still diverge across draw orders and RNG
  APIs, so demanding bit-equality here would manufacture disagreements. These
  are flagged only when the DECISION they imply differs, or when they move
  further than plausible Monte-Carlo error.

Every disagreeing field is reported. The comparison never stops at the first.
"""

from __future__ import annotations

from typing import Any

BOOTSTRAP_RELATIVE_TOLERANCE = 0.02
EXACT_TOLERANCE = 1e-9

MISSING = object()


def find_field(obj: Any, names: tuple[str, ...]) -> tuple[str | None, Any]:
    """First value in a nested structure whose key matches one of `names`.

    RESULT_V1.json is authored by the other party and its layout is not fixed
    by any frozen document, so the comparison locates fields by name at any
    depth rather than assuming a shape.
    """
    stack: list[tuple[str, Any]] = [("", obj)]
    lowered = tuple(n.lower() for n in names)
    while stack:
        path, node = stack.pop(0)
        if isinstance(node, dict):
            for key, value in node.items():
                here = f"{path}.{key}" if path else str(key)
                if str(key).lower() in lowered:
                    return here, value
                stack.append((here, value))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                stack.append((f"{path}[{i}]", item))
    return None, MISSING


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool) or value is None or value is MISSING:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


class Comparison:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def exact(self, field: str, mine: Any, theirs_path: str | None, theirs: Any) -> None:
        if theirs is MISSING:
            self.rows.append(
                {
                    "field": field,
                    "tier": "exact",
                    "checker_value": mine,
                    "result_value": None,
                    "status": "NOT_PRESENT_IN_RESULT",
                    "disagreement": False,
                }
            )
            return
        mine_num, theirs_num = _numeric(mine), _numeric(theirs)
        if mine_num is not None and theirs_num is not None:
            agree = abs(mine_num - theirs_num) <= EXACT_TOLERANCE
        else:
            agree = mine == theirs
        self.rows.append(
            {
                "field": field,
                "tier": "exact",
                "checker_value": mine,
                "result_value": theirs,
                "result_path": theirs_path,
                "status": "AGREE" if agree else "DISAGREE",
                "disagreement": not agree,
            }
        )

    def tolerance(
        self,
        field: str,
        mine: Any,
        theirs_path: str | None,
        theirs: Any,
        threshold: float | None = None,
    ) -> None:
        if theirs is MISSING:
            self.rows.append(
                {
                    "field": field,
                    "tier": "tolerance",
                    "checker_value": mine,
                    "result_value": None,
                    "status": "NOT_PRESENT_IN_RESULT",
                    "disagreement": False,
                }
            )
            return
        mine_num, theirs_num = _numeric(mine), _numeric(theirs)
        if mine_num is None or theirs_num is None:
            status = "AGREE" if mine == theirs else "DISAGREE"
            self.rows.append(
                {
                    "field": field,
                    "tier": "tolerance",
                    "checker_value": mine,
                    "result_value": theirs,
                    "result_path": theirs_path,
                    "status": status,
                    "disagreement": status == "DISAGREE",
                }
            )
            return

        scale = max(abs(mine_num), abs(theirs_num), 1e-12)
        drift = abs(mine_num - theirs_num) / scale
        crosses = False
        if threshold is not None:
            crosses = (mine_num < threshold) != (theirs_num < threshold)
        disagree = crosses or drift > BOOTSTRAP_RELATIVE_TOLERANCE
        self.rows.append(
            {
                "field": field,
                "tier": "tolerance",
                "checker_value": mine_num,
                "result_value": theirs_num,
                "result_path": theirs_path,
                "relative_drift": drift,
                "decision_threshold": threshold,
                "crosses_decision_threshold": crosses,
                "status": "DISAGREE" if disagree else "AGREE",
                "disagreement": disagree,
            }
        )

    def summary(self) -> dict[str, Any]:
        disagreements = [r for r in self.rows if r["disagreement"]]
        comparable = [r for r in self.rows if r["status"] in ("AGREE", "DISAGREE")]
        return {
            "n_fields_examined": len(self.rows),
            "n_fields_comparable": len(comparable),
            "n_not_present_in_result": len(self.rows) - len(comparable),
            "n_disagreements": len(disagreements),
            "disagreeing_fields": [r["field"] for r in disagreements],
            "fields": self.rows,
        }


def compare(analysis: dict[str, Any], decision: dict[str, Any], result: Any) -> dict[str, Any]:
    cmp = Comparison()

    path, value = find_field(result, ("terminal", "terminal_id", "verdict"))
    cmp.exact("terminal", decision["terminal"], path, value)

    for gate_id in ("G1", "G2", "G3", "G4", "G5", "G6", "G7"):
        gate = analysis["gates"].get(gate_id, {})
        names = (gate_id, gate.get("id", gate_id))
        gpath, gvalue = find_field(result, names)
        if gvalue is not MISSING and isinstance(gvalue, dict):
            sub_path, sub_value = find_field(gvalue, ("passed", "pass", "result", "status"))
            gpath = f"{gpath}.{sub_path}" if sub_path else gpath
            gvalue = sub_value
        cmp.exact(f"gates.{gate_id}.passed", gate.get("passed"), gpath, gvalue)

    for arm, row in sorted(analysis["score_rows"]["per_arm_overall"].items()):
        arm_path, arm_value = find_field(result, (arm,))
        if arm_value is MISSING or not isinstance(arm_value, dict):
            continue
        for metric in ("n", "success_rate", "forbidden_rate", "mean_cost_total"):
            mpath, mvalue = find_field(arm_value, (metric, f"mean_{metric}", "mean_spent_budget"))
            cmp.exact(
                f"score_rows.{arm}.{metric}",
                row.get(metric),
                f"{arm_path}.{mpath}" if mpath else arm_path,
                mvalue,
            )

    for name, comparison in sorted(analysis["comparisons"].items()):
        pooled = comparison["pooled"]
        # Scope the lookup to this comparison's own object. A bare "n_matched"
        # search would compare every comparison against whichever one appears
        # first in the supplied result, manufacturing disagreements.
        scope_path, scope = find_field(result, (name,))
        if scope is MISSING or not isinstance(scope, dict):
            scope_path, scope = None, {}
        rpath, rvalue = find_field(scope, ("ratio", "point", "point_estimate"))
        npath, nvalue = find_field(scope, ("n_matched",))
        prefix = f"{scope_path}." if scope_path else ""
        cmp.exact(
            f"comparisons.{name}.ratio",
            pooled["ratio"],
            f"{prefix}{rpath}" if rpath else None,
            rvalue,
        )
        cmp.exact(
            f"comparisons.{name}.n_matched",
            pooled["n_matched"],
            f"{prefix}{npath}" if npath else None,
            nvalue,
        )

    thresholds = {
        "G3_ratio_theorem_scope": 0.80,
        "G3_ratio_all_strata": 0.80,
        "G6_ratio_theorem_scope": 1.00,
        "G6_ratio_all_strata": 1.00,
    }
    for name, interval in sorted(analysis["bootstrap_intervals"].items()):
        for bound in ("ci_low", "ci_high"):
            bpath, bvalue = find_field(result, (f"{name}_{bound}",))
            cmp.tolerance(
                f"bootstrap.{name}.{bound}",
                interval.get(bound),
                bpath,
                bvalue,
                thresholds.get(name) if bound == "ci_high" else None,
            )

    for test, entry in sorted(analysis["holm"]["tests"].items()):
        ppath, pvalue = find_field(result, (f"{test}_p_holm_adjusted", f"{test}_p"))
        cmp.tolerance(f"holm.{test}.p_holm_adjusted", entry.get("p_holm_adjusted"), ppath, pvalue)

    apath, avalue = find_field(result, ("anchor_reproduction_gate", "anchor_gate"))
    if avalue is not MISSING:
        claimed = avalue
        if isinstance(avalue, dict):
            sub_path, sub_value = find_field(avalue, ("passed", "pass", "status", "result"))
            apath = f"{apath}.{sub_path}" if sub_path else apath
            claimed = sub_value
        claims_pass = claimed is True or (
            isinstance(claimed, str) and claimed.strip().upper() in {"PASS", "PASSED", "OK", "TRUE"}
        )
        cmp.rows.append(
            {
                "field": "anchor_reproduction_gate",
                "tier": "exact",
                "checker_value": analysis["anchor_reproduction_gate"]["status"],
                "result_value": claimed,
                "result_path": apath,
                "status": "DISAGREE" if claims_pass else "AGREE",
                "disagreement": claims_pass,
                "note": (
                    "The result claims the anchor gate passed, but no committed rates for "
                    "this world family exist in any frozen document, so the claim has no "
                    "reproducible basis from the traces."
                )
                if claims_pass
                else "Both sides treat the anchor gate as unreproducible from frozen bytes.",
            }
        )

    return cmp.summary()
