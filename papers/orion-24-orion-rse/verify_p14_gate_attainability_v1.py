"""Adjudicate what P14A's two failed gates measured, and where the question is answered.

Reads nothing new into the paper's evidence. It drives three registered
instruments over artifacts that are already frozen and writes their verdicts to
``P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json``:

* ``orion.study.p14.governance_gates`` loads the shipped P14A generator,
  reproduces its committed ``full_result_sha256`` and asks whether either failing
  threshold had a value the frozen sampling support could produce;
* ``orion.study.p14.specification_conformance`` loads the shipped P14C runner and
  frozen case table, reproduces the committed canonical digest, asks the same
  question over the coordinate P14C leaves free, and reads P14A's two thresholds
  --- unchanged --- on P14C's benchmark;
* ``orion.study.p14.balanced_governance`` loads the shipped P14B generator,
  reproduces its committed ``replay_sha256``, and asks the same question of a
  **positive** terminal.

The P14B block is the one this file used to be missing. Earlier revisions of this
docstring said no P14B threshold "is edited, re-run or relabelled" --- true, and
P14B had never been audited either, which
``orion.programme.registry_coverage`` recorded as an unexamined positive. It is
audited now, and the answer has two halves that must not be collapsed: P14B's
terminal **could** have printed either word --- the full contract clears all
eight gates and each of the four registered component ablations, placed in the
graded slot, fails at least one --- while only **four of the eight** gates could
have gone either way. ``full_discovery_recall_one`` and ``matched_budget`` are
hypothesis gates no admissible world can fail, and the two preconditions are
unconditional as preconditions should be. "Eight gates, all true" is four
readings and four constants.

No P14A, P14B or P14C threshold, seed, case, gold label, policy, comparator or
result is edited, re-run or relabelled by this adjudication. P14A's terminal
remains ``P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET`` verbatim, P14B's
remains ``P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED`` verbatim under its
standing ``P14B_NON_AUTHORITATIVE_PROTOCOL_MISMATCH`` downgrade, and P14C's
stands as published.

    python papers/orion-24-orion-rse/verify_p14_gate_attainability_v1.py

Exits ``1`` when the adjudication does not reach its positive terminal.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.programme.records import Outcome
from orion.study.p14 import balanced_governance as p14b
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

    p14b_report = p14b.audit_p14b_balanced_terminal()
    p14b_json = p14b.report_as_json(p14b_report)

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
        # P14B: the positive terminal this file used to leave unaudited. Three
        # measurements, each of which could have come out the other way --- the
        # last one is exactly what P14A failed. How many of P14B's eight gates
        # discriminate is *not* a gate here: it is a defect in P14B's battery,
        # reported by name in the block below, and folding it into this
        # conjunction would make an adjudication about P14A's terminal turn on
        # something else. Same rule P14C's unexercised recall gate gets.
        "p14b_committed_digest_reproduced": bool(p14b_json["digest_reproduced"]),
        "p14b_terminal_had_two_reachable_values": p14b_json["terminal_reach"][
            "distinct_terminals"
        ]
        == 2,
        "p14b_no_threshold_was_unattainable": p14b_report["threshold_panel"].unattainable
        == (),
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
            "P14B_BALANCED_GOVERNANCE_PROTOCOL_V1.md",
            "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_PROTOCOL_V1.md",
        ],
        "instruments": [
            "orion.study.p14.governance_gates",
            "orion.study.p14.gate_audit",
            "orion.study.p14.balanced_governance",
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
        "p14b": {
            "terminal_retained_verbatim": p14b.SHIPPED_TERMINAL,
            "standing_downgrade_retained": "P14B_NON_AUTHORITATIVE_PROTOCOL_MISMATCH",
            "replay_sha256": p14b.SHIPPED_RESULT_DIGEST,
            "committed_digest_reproduced": p14b_json["digest_reproduced"],
            "receipt_fidelity": p14b_json["receipt_fidelity"],
            "stratum_share": p14b_json["stratum_share"],
            "world_register": [
                {
                    "world_id": world.world_id,
                    "admits": world.admits,
                    "seed": world.payload.seed,
                    "subject": world.payload.subject,
                }
                for world in p14b.declared_worlds()
            ],
            "terminal_reach": p14b_json["terminal_reach"],
            # Reported and not rolled up: the sub-register that varies only the
            # draw. Its per-gate readings are the same eight already above, so
            # only the roll-up is carried here.
            "seed_only_terminal_reach": {
                key: p14b_json["seed_only_terminal_reach"][key]
                for key in (
                    "label",
                    "outcome",
                    "distinct_terminals",
                    "worlds",
                    "clearing_every_gate",
                    "unattainable",
                    "unconditional",
                )
            },
            "pre_run_threshold_panel": p14b_json["threshold_panel"],
            "gates_published": len(p14b.GATES),
            "gates_that_discriminate": p14b_json["discriminating_gates"],
            "hypothesis_gates_without_refutation_capacity": p14b_json[
                "unexercised_hypothesis_gates"
            ],
            "unconditional_preconditions": [
                gate_id
                for gate_id in p14b_json["terminal_reach"]["unconditional"]
                if gate_id not in set(p14b_json["unexercised_hypothesis_gates"])
            ],
            "arms_missing_a_promotable_state": p14b_json[
                "arms_missing_a_promotable_state"
            ],
            "arm_error_strata": p14b_json["arm_error_strata"],
            "graded_arm_divergence_from_gold": p14b_json["graded_arm_divergence"],
            "evidential_disposition": "TERMINAL_REACHABLE__GATE_COUNT_INFLATED",
            "disposition_detail": (
                "P14B's conjunction could have printed either word: the full contract "
                "clears all eight gates and each of the four component ablations its own "
                "protocol registers, placed in the graded slot, fails at least one. That is "
                "the property P14A's conjunction did not have, and nothing here disturbs "
                "it. But only four of the eight gates could have gone either way. "
                "full_discovery_recall_one is satisfied by every one of the nine arms in "
                "every admissible run -- exactly three of the 256 fact assignments are "
                "adjudicated SUPPORTED_RESIDUAL by gold and no registered policy declines "
                "any of them, because the rule baselines promote supersets of gold and an "
                "ablation removes a check -- and matched_budget reads a module literal "
                "assigned identically to all nine arms. Both are hypothesis gates and both "
                "publish true without being able to publish anything else. The remaining "
                "two unconditional gates are preconditions, where holding everywhere is "
                "the intended behaviour: the difficulty bar P14A could not reach in any "
                "admissible world is 2.9x cleared here in every one. Separately, the "
                "coordinate the protocol leaves free at run time is the seed, and over the "
                "shipped draw and two alternates the terminal is a constant -- the balanced "
                "strata make every rate an exact fraction -- so the terminal's two words "
                "come entirely from substituting the graded implementation, whose own side "
                "of all four discriminating gates is fixed by policy('ORION_RSE_FULL', c) "
                "being return gold(c) at 0 divergent points of 256. The receipt, protocol, "
                "seed, thresholds, gold labels, comparators and terminal are retained "
                "verbatim, as is P14B's standing non-authoritative downgrade; only the "
                "reading of what its eight gates established changes."
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
