#!/usr/bin/env python3
"""Apply the criterion-churn gate, after the fact, to the two lanes that motivated it.

The gate in ``orion_research_harness.criterion_binding`` was written because
QG-23 and QG-24 each changed an acceptance criterion after seeing an outcome and
nothing in the harness checked it. A gate justified by history should be run
against that history, so this script builds a criterion-binding record for each
case out of evidence that can be checked -- committed git revisions of the
verifier, and the lanes' own disclosure fields -- and reports what the gate does.

Both cases were adjudicated by hand at the time and both changes were judged
sound. The point of this script is not to overturn either. It is to establish
whether the gate is doing work: whether it is silent on a case it should be
silent on, and whether it bites on the case where it should.

Run from the repository root. Writes CRITERION_CHURN_RETROSPECTIVE.json.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(
    0, str(pathlib.Path("packages/orion-research-harness/src").resolve())
)

from orion_research_harness.criterion_binding import (  # noqa: E402
    FAIL,
    PASS,
    criterion_digest,
    validate_criterion_binding,
)

ROOT = pathlib.Path(".").resolve()
VERIFIER = "development/orion-qg-regime-geometry/qg24_generic_verify.py"

# The revision at which QG-24's verifier was committed with its passage rule as
# first written, before any adjudication outcome; and the revision at which the
# lane was bound, where the rule had changed.
QG24_FROZEN_REV = "ce66acbd"
QG24_APPLIED_REV = "1057dbe7"


def _rule_at(rev: str) -> str:
    """The passage-matching expression as committed at `rev`.

    Extracted from the committed file rather than described, so the criterion
    texts below are quotations and not a reconstruction.
    """
    blob = subprocess.run(
        ["git", "show", f"{rev}:{VERIFIER}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    lines = blob.splitlines()
    for i, line in enumerate(lines):
        if "flat = " in line:
            # the assignment plus whatever continuation lines belong to it,
            # up to the membership test that consumes it
            out = []
            for j in range(i, min(i + 6, len(lines))):
                out.append(lines[j].strip())
                if "not in flat" in lines[j]:
                    break
            return " ".join(out)
    raise SystemExit(f"passage rule not found at {rev}")


def main() -> int:
    qg24_frozen = _rule_at(QG24_FROZEN_REV)
    qg24_applied = _rule_at(QG24_APPLIED_REV)
    if qg24_frozen == qg24_applied:
        raise SystemExit(
            "the two revisions carry the same rule; the premise of this "
            "retrospective is wrong and it must not be reported as a change"
        )

    # Do not assert what the frozen rule would have done -- run it. Each of
    # QG-24's donor passages is matched against the committed query log under
    # the rule exactly as committed at the frozen revision.
    res24 = json.loads(
        pathlib.Path(
            "research/extensions/orion-qg/QG24_ROTATION_REGIME_RESULTS.json"
        ).read_text()
    )
    log24 = pathlib.Path(
        "development/orion-qg-regime-geometry/QG24_DONOR_SEARCH.md"
    ).read_text()
    flat_frozen = " ".join(log24.split())
    located = {}
    for idx, rec in enumerate(res24["donor_search"]["records"]):
        passage = " ".join(str(rec.get("verbatim_passage", "")).split())
        if passage:
            located[idx] = passage in flat_frozen
    frozen_verdict = PASS if all(located.values()) else FAIL

    qg24 = {
        "lane": "QG-24",
        "frozen_rule_locates_each_passage": located,
        "criterion": "a donor record's verbatim_passage must occur in the committed query log",
        "frozen_criterion_digest": criterion_digest(qg24_frozen),
        "applied_criterion_digest": criterion_digest(qg24_applied),
        "frozen_criterion_text": qg24_frozen,
        "applied_criterion_text": qg24_applied,
        "frozen_revision": QG24_FROZEN_REV,
        "applied_revision": QG24_APPLIED_REV,
        "reported_verdict": PASS,
        "deviation": {
            "description": (
                "the comparison was loosened from pure whitespace normalization "
                "to additionally stripping markdown blockquote markers from each "
                "log line before flattening"
            ),
            "rationale": (
                "the committed query log quotes its search results inside "
                "blockquotes, so passages present in the log did not match under "
                "the frozen rule; the loosening removes a formatting artifact of "
                "the log, not a substantive requirement on the passage"
            ),
        },
        "verdict_under_frozen_criterion": frozen_verdict,
        "exhibited_rejection_ref": (
            "QG24_GENERIC_VERIFICATION.json#falsifiability_demonstration"
            ".cases[T4_subsuming_passage_removed] -- the loosened rule still "
            "REJECTs a donor record whose passage is stripped"
        ),
    }

    # QG-23 changed its H1 reading and its own disclosure records the direction:
    # the adopted reading is the one under which H1 is REFUTED.
    res = json.loads(
        pathlib.Path(
            "research/extensions/orion-qg/QG23_FORECAST_N_DEPENDENCE_RESULTS.json"
        ).read_text()
    )
    disc = res["criterion_disclosure"]
    all_pairs = disc["H1_under_all_pairs_reading"]
    consumed = disc["H1_under_consumed_measure_reading"]
    qg23 = {
        "lane": "QG-23",
        "criterion": "H1: normalized n=4 coverage separates accuracy",
        "frozen_criterion_digest": criterion_digest("H1 scored under the all-pairs reading"),
        "applied_criterion_digest": criterion_digest(
            "H1 scored under the consumed-support-measure reading"
        ),
        "reported_verdict": FAIL if consumed == "REFUTED" else PASS,
        "note": (
            f"the lane's own criterion_disclosure records H1 as {all_pairs} under "
            f"the frozen reading and {consumed} under the adopted one: the "
            "criterion was changed in the direction of the harsher result"
        ),
    }

    out = {"schema": "ORIONQG.CriterionChurnRetrospective.v1", "cases": []}
    for rec in (qg24, qg23):
        try:
            validate_criterion_binding(rec)
            gate = "CLEARS"
            reason = None
        except ValueError as exc:  # pragma: no cover - reported, not raised
            gate = "REFUSED"
            reason = str(exc)
        out["cases"].append({**rec, "gate": gate, "gate_reason": reason})

    # A gate that clears everything is not a gate. Show it biting on this very
    # record set: drop QG-24's exhibited rejection and it must be refused.
    stripped = {k: v for k, v in qg24.items() if k != "exhibited_rejection_ref"}
    try:
        validate_criterion_binding(stripped)
        raise SystemExit(
            "the gate cleared QG-24 with its exhibited rejection removed; it is "
            "not enforcing the check this retrospective exists to demonstrate"
        )
    except ValueError as exc:
        out["gate_is_not_vacuous"] = {
            "case": "QG-24 with exhibited_rejection_ref removed",
            "gate": "REFUSED",
            "gate_reason": str(exc),
        }

    # The finding is DERIVED from what the gate returned, not written ahead of it.
    #
    # The first draft of this script computed each gate result and then wrote a
    # fixed narrative asserting that QG-23 was silent and QG-24 cleared. Had
    # either come back REFUSED, the committed artifact would have kept saying
    # they passed -- a conclusion independent of its own evidence, written into
    # the retrospective for a module whose entire subject is conclusions that
    # must depend on their criteria. Caught in review on PR #892.
    gates = {c["lane"]: c["gate"] for c in out["cases"]}
    qg23_was_gated = (
        qg23["applied_criterion_digest"] != qg23["frozen_criterion_digest"]
        and qg23["reported_verdict"] == PASS
    )
    qg24_was_gated = (
        qg24["applied_criterion_digest"] != qg24["frozen_criterion_digest"]
        and qg24["reported_verdict"] == PASS
    )

    premises = {
        "qg23_reported_a_negative_so_the_gate_does_not_engage": not qg23_was_gated,
        "qg24_reported_a_pass_under_a_changed_rule_so_the_gate_engages": qg24_was_gated,
        "qg24_frozen_rule_would_have_failed": frozen_verdict == FAIL,
        "both_real_cases_clear": gates == {"QG-24": "CLEARS", "QG-23": "CLEARS"},
    }
    out["derivation_premises"] = premises

    engaged = "engages on" if qg24_was_gated else "does not engage on"
    silent = "silent on" if not qg23_was_gated else "engaged on"
    out["finding"] = (
        f"The gate is {silent} QG-23: that lane changed its criterion toward the "
        f"harsher reading and reported {qg23['reported_verdict']}, and a changed "
        "criterion yielding a negative is not the failure mode this module "
        f"exists to catch. It {engaged} QG-24, whose loosened rule carried "
        f"{qg24['reported_verdict']} where the frozen rule -- run, not assumed -- "
        f"returns {frozen_verdict}. Gate results: "
        + ", ".join(f"{lane} {verdict}" for lane, verdict in sorted(gates.items()))
        + ". On this programme's own history the gate therefore "
        + ("confirms rather than catches" if premises["both_real_cases_clear"]
           else "REFUSES a case that was adjudicated sound by hand, and that "
                "discrepancy is the result and must be investigated before this "
                "artifact is cited")
        + ". What it changes is that the demonstration becomes a precondition "
        "instead of something an adjudicator happened to check by hand."
    )

    # Fail closed, exactly as the vacuity check below does: this script may not
    # commit an artifact whose narrative rests on premises that did not hold.
    broken = [name for name, held in premises.items() if not held]
    if broken:
        raise SystemExit(
            "the retrospective's premises did not hold: "
            + ", ".join(broken)
            + ". The finding text is derived from these, so writing the artifact "
            "would publish a narrative its own evidence contradicts. Investigate "
            "the discrepancy rather than relaxing this check."
        )

    dest = pathlib.Path(
        "development/orion-qg-regime-geometry/CRITERION_CHURN_RETROSPECTIVE.json"
    )
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({c["lane"]: c["gate"] for c in out["cases"]}, indent=1))
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
