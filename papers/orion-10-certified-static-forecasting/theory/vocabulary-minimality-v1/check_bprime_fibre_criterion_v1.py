#!/usr/bin/env python3
"""Apply ORION-10's fibre criterion to the real B' witnesses from QG-7.

The companion result in this packet closes the UNIVERSAL half of RUN_QUEUE item 9 on
the abstract space. This is the SCOPED half it explicitly disclaimed: the named
vocabulary B', on the real instance space, rather than partitions in the abstract.

Source, read as data only: research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json,
terminal QG7_FOURTH_SUPPORT2_REGIME_FOUND, whose arm1_hostile_search serialises the 64
fourth-regime candidates verbatim out of 740 instances evaluated.

The criterion (certificate-explanation-gap-v1/THEORY.md, Theorem 2): an exact Psi-only
explanation exists iff cost is constant on every Psi-fibre.

The finding is a CANNOT_CHECK, and the reason is the interesting part. Keyed on the
scalar f_B', the 64 witnesses show zero cost-mixed fibres - in fact C_Dxx = f_B' - 1
exactly, in all 64. Read naively that says the vocabulary determines the cost. But the
64 are SELECTED on C_D++ < min(C_D+, f_B'), so conditioning on a gap is what produces
the uniformity. A selection-conditioned sample cannot establish fibre-constancy over
the space; the 676 unselected instances are the ones that would test it, and they are
not serialised in this artifact.

No claim is promoted. This records what the committed data can and cannot support.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

SOURCE = "research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--emit", default="BPRIME_FIBRE_CRITERION_V1.json")
    a = ap.parse_args()

    src = Path(a.repo_root) / SOURCE
    if not src.is_file():
        raise SystemExit(f"source not found: {src}")
    doc = json.loads(src.read_text(encoding="utf-8"))
    arm = doc["arm1_hostile_search"]
    W = arm["fourth_regime_candidates_verbatim"]

    fibres = defaultdict(set)
    for w in W:
        fibres[w["f_Bprime"]].add(w["C_Dxx"])
    mixed = {k: sorted(v) for k, v in fibres.items() if len(v) > 1}

    offsets = Counter(w["f_Bprime"] - w["C_Dxx"] for w in W)
    dplus = Counter(w["C_Dplus"] - w["C_Dxx"] for w in W)
    dp = Counter(w["C_DP"] - w["C_Dxx"] for w in W)

    serialised = len(W)
    evaluated = arm["instances_evaluated_total"]
    unselected = evaluated - serialised

    out = {
        "schema": "ORION.ORION10.BprimeFibreCriterion.v1",
        "source": SOURCE,
        "source_terminal": doc.get("terminal"),
        "source_result_digest": doc.get("result_digest"),
        "criterion": "certificate-explanation-gap-v1/THEORY.md Theorem 2: exact Psi-only "
                     "explanation exists iff cost is constant on every Psi-fibre",
        "witnesses_serialised": serialised,
        "instances_evaluated_total": evaluated,
        "instances_not_serialised": unselected,
        "fibres_keyed_on_f_Bprime": {str(k): sorted(v) for k, v in sorted(fibres.items())},
        "cost_mixed_fibres": mixed,
        "cost_mixed_fibre_count": len(mixed),
        "offset_f_Bprime_minus_C_Dxx": {str(k): v for k, v in offsets.items()},
        "offset_is_uniformly_one": set(offsets) == {1},
        "offset_C_Dplus_minus_C_Dxx": {str(k): v for k, v in dplus.items()},
        "offset_C_DP_minus_C_Dxx": {str(k): v for k, v in dp.items()},
        "panels_represented": len({w.get("panel") for w in W}),
        "replay_confirmed_all": all(w.get("replay_confirmed") for w in W),
        "terminal": "CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES",
        "why_cannot_check": (
            "The 64 serialised witnesses are selected on C_D++ < min(C_D+, f_B'). Cost "
            "constancy within an f_B' fibre on a gap-selected subset is what the selection "
            "produces, not evidence about the space. Testing the criterion needs the "
            f"{unselected} unselected instances, which this artifact does not serialise."
        ),
        "what_is_established": (
            "On the 64 witnesses the relationship is exact and uniform: C_Dxx = f_B' - 1 in "
            "all 64, C_D+ - C_Dxx = 1 in all 64, and C_DP = C_Dxx in all 64, across 8 panels, "
            "all replay-confirmed. That uniformity is a fact about the witness set and is "
            "consistent with the source's own claim_boundary, which states C_DP == C_D++ for "
            "all n as a committed component."
        ),
        "what_would_settle_it": (
            "Serialise f_B' and C_D++ for all 740 evaluated instances, not only the 64 "
            "candidates, and re-run this fibre grouping over the unselected majority."
        ),
        "promotes_no_claim": True,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"  witnesses={serialised} of {evaluated} evaluated ({unselected} not serialised)")
    print(f"  cost-mixed fibres keyed on f_Bprime: {len(mixed)}")
    print(f"  offset f_Bprime - C_Dxx uniformly 1: {out['offset_is_uniformly_one']}")
    print(f"  terminal: {out['terminal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
