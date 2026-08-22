"""Adjudicate what P14A's two failed gates measured, and where the question is answered.

Reads nothing new into the paper's evidence. It drives two registered
instruments over artifacts that are already frozen and writes their verdicts to
``P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json``:

* ``orion.study.p14.governance_gates`` loads the shipped P14A generator,
  reproduces its committed ``full_result_sha256`` and asks whether either failing
  threshold had a value the frozen sampling support could produce;
* ``orion.study.p14.specification_conformance`` loads the shipped P14C runner and
  frozen case table, reproduces the committed canonical digest, asks the same
  question over the coordinate P14C leaves free, and reads P14A's two thresholds
  --- unchanged --- on P14C's benchmark.

No P14A, P14B or P14C threshold, seed, case, gold label, policy, comparator or
result is edited, re-run or relabelled by this adjudication. P14A's terminal
remains ``P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`` verbatim.

    python papers/paper-14-orion-rse/verify_p14_gate_attainability_v1.py

Exits ``1`` when the adjudication does not reach its positive terminal.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.records import Outcome
from orion.study.p14 import gate_audit, governance_gates as p14a
from orion.study.p14 import specification_conformance as p14c

HERE = Path(__file__).resolve().parent
OUT = HERE / "P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json"

POSITIVE_TERMINAL = (
    "P14A_SUPERIORITY_GATES_UNMEASURABLE__QUESTION_ANSWERED_BY_P14C_AT_UNCHANGED_THRESHOLDS"
)
NEGATIVE_TERMINAL = "P14_GATE_ATTAINABILITY_ADJUDICATION_GATE_NOT_MET"


def main() -> None:
    p14a_report = gate_audit.audit_p14a_governance_terminal()
    p14a_json = gate_audit.report_as_json(p14a_report)
    p14a_panel = p14a.threshold_panel()

    p14c_report = p14c.audit_p14c_conformance_terminal()
    p14c_json = p14c.report_as_json(p14c_report)

    p14a_reaches = {
        reach.gate.gate_id: reach
        for reach in p14a.gate_reaches()
        if reach.gate.gate_id in set(p14a.SUPPORT_BOUNDED_GATES)
    }

    gates = {
        # The two fidelity anchors: both instruments reproduce the committed
        # digests, so every verdict below is about the shipped artifacts.
        "p14a_committed_digest_reproduced": bool(p14a_json["digest_reproduced"]),
        "p14c_committed_digest_reproduced": bool(p14c_json["digest_reproduced"]),
        # P14A: neither failing threshold had a reachable value.
        "p14a_both_failed_gates_unattainable": p14a_panel.unattainable
        == tuple(p14a.SUPPORT_BOUNDED_GATES),
        "p14a_terminal_had_one_reachable_value": p14a_json["terminal_reach"][
            "distinct_terminals"
        ]
        == 1,
        "p14a_emitter_was_responsive": p14a_report["responsiveness"].outcome == Outcome.PASS,
        # P14C: the successor's conjunction could have printed either word, and
        # its own thresholds sit inside the interval its freeze declares.
        "p14c_terminal_had_two_reachable_values": p14c_json["terminal_reach"][
            "distinct_terminals"
        ]
        == 2,
        "p14c_thresholds_inside_reach": p14c_report["threshold_panel"].outcome
        == Outcome.PASS,
        # The resolution: P14A's own bars, unedited, are reachable here and met.
        "p14a_thresholds_reachable_on_p14c": p14c_report["inherited_threshold_panel"].outcome
        == Outcome.PASS,
        "p14a_thresholds_met_on_p14c": all(p14c_json["inherited_gates_met"].values()),
    }
    terminal = POSITIVE_TERMINAL if all(gates.values()) else NEGATIVE_TERMINAL

    result = {
        "schema": "ORION.P14.GateAttainabilityAdjudication.v1",
        "adjudicates": [
            "P14A_HIDDEN_GOLD_GOVERNANCE_PROTOCOL_V1.md",
            "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_PROTOCOL_V1.md",
        ],
        "instruments": [
            "orion.study.p14.governance_gates",
            "orion.study.p14.gate_audit",
            "orion.study.p14.specification_conformance",
        ],
        "edits_no_frozen_result": True,
        "p14a": {
            "terminal_retained_verbatim": p14a.SHIPPED_TERMINAL,
            "full_result_sha256": p14a.SHIPPED_RESULT_DIGEST,
            "committed_digest_reproduced": p14a_json["digest_reproduced"],
            "declared_statistic_support": p14a.declared_statistic_support().as_json(),
            "failed_gates": {
                gate_id: {
                    "threshold": reach.gate.threshold,
                    "role": reach.gate.role.value,
                    "reason": reach.reason.value,
                    "best_value_over_admissible_worlds": reach.best_value,
                    "attainment_margin": reach.attainment_margin,
                    "satisfying_worlds": list(reach.satisfying),
                }
                for gate_id, reach in p14a_reaches.items()
            },
            "pre_run_threshold_panel": p14a_panel.as_json(),
            "terminal_reach": p14a_json["terminal_reach"],
            "receipt_responsiveness": p14a_json["responsiveness"],
            "graded_arm_divergence_from_gold": p14a_json["orion_arm_divergence"],
            "evidential_disposition": "CANNOT_CHECK",
            "disposition_detail": (
                "Both gates read one quantity: the prevalence of the single fact state on "
                "which the strongest rule baseline and the full contract disagree. Its "
                "supremum over the protocol's own declared sampling support is 0.042326, "
                "below both the 0.05 and the 0.08 bar, so no draw the freeze admits could "
                "have satisfied either. The published NOT_MET is therefore a measurement "
                "that could not be taken, not evidence against the governance contract. "
                "The result, the seed, the thresholds and the terminal are retained "
                "verbatim; only the reading of what they established changes."
            ),
        },
        "p14c": {
            "terminal": p14c.SHIPPED_TERMINAL,
            "canonical_sha256": p14c.SHIPPED_RESULT_DIGEST,
            "committed_digest_reproduced": p14c_json["digest_reproduced"],
            "discriminating_stratum_share": p14c_json["discriminating_stratum_share"],
            "arm_error_counts_over_the_frozen_table": p14c_json["arm_error_counts"],
            "subject_register": [
                {"world_id": world.world_id, "admits": world.admits, "subject": world.payload}
                for world in p14c.subject_worlds()
            ],
            "terminal_reach": p14c_json["terminal_reach"],
            "pre_run_threshold_panel": p14c_json["threshold_panel"],
            "hypothesis_gates_without_refutation_capacity": p14c_json[
                "unexercised_hypothesis_gates"
            ],
        },
        "inherited_p14a_thresholds_on_p14c": {
            "thresholds_unchanged": {
                gate.gate_id: gate.threshold for gate in p14c.INHERITED_GATES
            },
            "pre_run_threshold_panel": p14c_json["inherited_threshold_panel"],
            "realized_values": p14c_json["inherited_reading"],
            "met": p14c_json["inherited_gates_met"],
        },
        "gates": gates,
        "terminal": terminal,
        "claim_authority": (
            "Specification-separated governance-contract conformance only, inherited "
            "unchanged from P14C. This adjudication establishes that P14A's two aggregate "
            "superiority gates were unmeasurable on P14A's own benchmark and that the same "
            "two thresholds, unedited, are both reachable and met on P14C's. It does not "
            "authorize any claim about external scientific validity, which still requires "
            "blinded independent adjudication."
        ),
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text, end="")
    if terminal != POSITIVE_TERMINAL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
