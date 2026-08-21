"""ORION-Q post-R6O gap-responsibility diagnosis campaign (Lane B, dual-harness benchmark).

Frozen protocol: development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md
(benchmark/diagnostic authority only; no scientific, novelty, promotion, or R6 authority).

This manifest poses one native decision to the production ``orion.transfer.v2`` /
``orion.self_orion`` modules through ``campaign_control``: given the committed R6
receipts through R6O, which epistemic layer is responsible for the remaining gap and
what is the correct next research move.  There is exactly ONE decision phase (``D0``)
plus one terminal phase (``DIAGNOSIS_RECORDED``).  The manifest does not encode the
answer: every responsibility hypothesis below has a genuine survival region in
observation space, discrimination is performed by ``assess_responsibility`` /
``assess_revision_gate`` / ``select_epistemic_computation`` /
``compose_epistemic_control`` over the transcribed observations, and every selectable
revision mechanic and computation action is mapped to a (non-executing, recording)
capability so that any native outcome can complete the cycle.

Observation transcription (every value is traceable to committed receipt fields)
================================================================================

R6_EARNED = "NO"
    development/orion-q-max-r0/harness-r6-drive-2026-08-21/CAMPAIGN_RUN_RECEIPT.json,
    final cycle ``evidence_updates.R6_EARNED == "NO"`` (native transform of
    ``r6_earned: false`` from the frozen prospective replay token); also carried in the
    terminal state ``observations``.

R6_PROTECTED_SUBJECT_ACCESSED = "NO"
    Same receipt, final cycle ``evidence_updates.R6_PROTECTED_SUBJECT_ACCESSED == "NO"``
    (``protected_stretched_n2_accessed: false``).

SUPPORT_DOMINANCE_LOCAL_INEQUALITY = "VERIFIED_ZERO_VIOLATIONS"
    research/extensions/orion-q/MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json:
    ``discovery.local_violation_count == 0``;
    ``local_verification.r6i_primary.violations == 0`` (``holds: true``),
    ``local_verification.r6m_primary.violations == 0`` (``holds: true``),
    ``local_verification.r6m_letterwise_monotone.violations == 0`` (``holds: true``);
    ``gates.r6i_local_inequality_holds``, ``gates.r6m_local_inequality_holds``,
    ``gates.r6m_letterwise_monotonicity_holds`` all true
    (688,041,472 local configurations checked).

SUPPORT_DOMINANCE_FAMILY_CLOSURE = "REFUTED_TAG_ANCHOR_REGIME"
    MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json: ``gates.synthetic_joint_equality == false``;
    ``discovery.characterization.donor_family_tag_anchor_coupling_violated == true``
    with ``frame_support_dominance_violated == false``; ``authority ==
    "MAX_R6N_SUPPORT_DOMINANCE_REFUTED__NEW_REGIME_FOUND__NOT_R6"``.

DPLUS_CLOSURE = "REFUTED_SECOND_COUPLING_REGIME"
    research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json: ``authority ==
    "MAX_R6O_ENLARGED_TAG_DONOR_CLOSURE_REFUTED__SECOND_NEW_REGIME_FOUND__NOT_R6"``;
    ``gates.dp_dplus_equal_random_panel == false`` and
    ``gates.dp_dplus_equal_structured_n2 == false``; ``discovery.note``: "a second
    coupling mechanism beyond the R6N Tag-anchor coupling is present on the listed
    instances" (40 verbatim ``instances_with_dp_strictly_below_dplus``).

CHEMISTRY_DONOR_EXACT = "YES_ALL_30"
    MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json: ``domains.chemistry.all_dp_equal == true``,
    ``domains.chemistry.all_tie_r6l == true``, ``domains.chemistry.matchings_checked ==
    30`` (H4 15 + N2 15, source blobs verified); corroborated by
    MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json ``frozen_subject_equality.r6m.all_equal ==
    true`` (30 matchings) and ``frozen_subject_equality.r6i.all_equal == true``
    (20 partitions).

EXACT_DP_VERIFICATION = "HOSTILE_EXACT_ALL_PANELS"
    research/extensions/orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json:
    ``gates.hostile_dp_vs_brute_exact == true`` and
    ``hostile.gates.dp_vs_brute_exact_all_panels == true`` (``hostile.all_pass``);
    MAX_R6O ``gates.dp_reader_binding_exact == true`` and
    ``gates.witness_reverification_pass == true``.

REGIME_MEMBERSHIP_PREDICATE = "ABSENT"
    Absence transcription: no committed receipt registers a frozen regime-membership
    predicate/gate for the refuting regimes.  Positive evidence of absence:
    MAX_R6N ``discovery.characterization.note`` ("This characterization is post-gate
    diagnosis, not a frozen gate"); MAX_R6O ``claim_boundary.machine_evidenced_only``
    ("the Tag-repair coupling remains analytically unbounded and is repaired here by
    enlarging the family, not by a proof"); MAX_R6O ``discovery.note`` (a second
    coupling mechanism is present but has no characterization at all).

WEIGHT2_CLOSURE = "UNTESTED"
    MAX_R6N ``claim_boundary.does_not_cover`` ("larger Tag ranks, grammars outside the
    frozen families") and MAX_R6O ``claim_boundary.does_not_cover`` ("larger Tag ranks,
    grammars outside the frozen family"): closure for weight-two frames / larger Tag
    ranks is explicitly outside the machine-evidenced coverage of every committed
    receipt.

Responsibility layer design (frozen; at least four materially different layers)
===============================================================================

RESP:CURRENT_SEARCH_INCOMPLETE  -> REV:SEARCH_CURRENT_ALPHABET
    Survives only if the exact-search machinery itself is unverified/incomplete
    (EXACT_DP_VERIFICATION in {INCOMPLETE, FAILED}).  Defeated here by the hostile
    exact DP-vs-brute verification.

RESP:DONOR_FAMILY_INCOMPLETE  -> REV:ABSORB_DONOR
    A further donor-family extension could close the gap.  Survives only while the
    enlarged-tag donor closure is untested or verified equal
    (DPLUS_CLOSURE in {UNTESTED, VERIFIED_EQUAL}).  Defeated here by the R6O
    refutation (second coupling regime).

RESP:REPRESENTATION_REGIME_UNCHARACTERIZED  -> REV:SPLIT_REPRESENTATION_REGIME
    The regime structure itself is the unknown.  Its bound revision carries the hard
    requirement OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN, whose phase obligation
    state is UNRESOLVED (the receipts show the predicate is ABSENT).  Under the
    production semantics an unresolved hard requirement makes the bound revision
    non-selectable (fail-closed), so the controller itself derives that computation
    must precede revision and selects COMPUTE:REGIME_CHARACTERIZATION on net value.
    This is the framework-native encoding of "computation before revision": the hard
    obligation lives on the revision mechanic, so the computation is reached ONLY when
    this hypothesis is the identified survivor - it is never forced phase-wide.

RESP:METHOD_LANGUAGE_INADEQUATE  -> REV:GROW_METHOD_LANGUAGE
    The method language is the responsible layer only if the refuting regimes are
    already fully characterized by a frozen predicate that the language cannot
    express (REGIME_MEMBERSHIP_PREDICATE == PRESENT).  Defeated here because the
    predicate is ABSENT.

No phase-wide hard obligations are declared in D0 (a phase-wide obligation would force
one fixed computation regardless of the responsibility resolution and thereby bake in
the selected move).  All capabilities are PYTHON recording stubs that transcribe the
natively selected move for the benchmark and terminate the campaign; they execute no
research, read no subject data, and assert non-authorizing authority strings.  The
protected stretched-N2 DUCC2 subject remains unreleased throughout.
"""

from __future__ import annotations


_RECORD_PREFIX = "ORIONQ_POST_R6O_DIAGNOSIS_RECORD="
_RECORD_AUTHORITY = "POST_R6O_DIAGNOSIS_MOVE_RECORDED__NOT_EXECUTED__NOT_R6"


def _recording_capability(selected_id: str) -> dict:
    code = (
        "import json; print('"
        + _RECORD_PREFIX
        + "' + json.dumps({"
        + "'authority': '"
        + _RECORD_AUTHORITY
        + "', "
        + "'recorded_move': '"
        + selected_id
        + "', "
        + "'r6_authority': False, "
        + "'reserved_stretched_n2_accessed': False, "
        + "'fresh_r6_subject_coefficients_accessed': False}))"
    )
    return {
        "host_capability": "PYTHON",
        "payload": {"code": code, "cwd": ".", "timeout": 30},
        "result_contract": {
            "kind": "SHELL_JSON_TOKEN",
            "prefix": _RECORD_PREFIX,
            "required_payload_values": [
                {"path": ["authority"], "equals": _RECORD_AUTHORITY},
                {"path": ["reserved_stretched_n2_accessed"], "equals": False},
                {"path": ["fresh_r6_subject_coefficients_accessed"], "equals": False},
            ],
            "evidence_rules": [
                {
                    "evidence_key": "DIAGNOSIS_SELECTED_MOVE",
                    "path": ["recorded_move"],
                    "transform": "STRING",
                },
                {
                    "evidence_key": "DIAGNOSIS_RECORD_TERMINAL",
                    "literal": "MOVE_RECORDED_FOR_DUAL_HARNESS_BENCHMARK",
                },
            ],
        },
        "next_phase": "DIAGNOSIS_RECORDED",
    }


def _interface_checks():
    return [
        {
            "check_id": "IFACE:FROZEN_OBJECTIVE_CONTRACT_MATCHED",
            "scope": "OBJECTIVE_CONTRACT",
            "state": "PASS",
            "evidence_ids": [
                "r6n-frozen-support-count-objective",
                "r6o-frozen-support-count-objective",
            ],
        },
        {
            "check_id": "IFACE:RECEIPT_BINDING_EXACT",
            "scope": "EVIDENCE_BINDING",
            "state": "PASS",
            "evidence_ids": [
                "r6n-implementation-binding-all-exact",
                "r6o-dp-reader-binding-exact",
                "r6o-f3-table-binding-exact",
            ],
        },
    ]


def _revision_mechanics():
    return [
        {
            "mechanic_id": "REV:SEARCH_CURRENT_ALPHABET",
            "kind": "SEARCH_MORE",
            "read_coordinates": ["EVIDENCE", "METHOD_LANGUAGE"],
            "write_coordinates": ["SEARCH_POLICY"],
            "preservation_obligations": ["PRESERVE:ACCESS", "PRESERVE:RESOURCE_VECTOR"],
            "cost": 1.0,
        },
        {
            "mechanic_id": "REV:ABSORB_DONOR",
            "kind": "ABSORB_DONOR",
            "read_coordinates": ["EVIDENCE", "DONOR_REGISTRY"],
            "write_coordinates": ["DONOR_REGISTRY"],
            "preservation_obligations": ["PRESERVE:ACCESS", "PRESERVE:RESOURCE_VECTOR"],
            "cost": 1.0,
        },
        {
            "mechanic_id": "REV:SPLIT_REPRESENTATION_REGIME",
            "kind": "SPLIT_REGIME",
            "read_coordinates": ["EVIDENCE", "REPRESENTATION", "REGIME_PREDICATE"],
            "write_coordinates": ["REPRESENTATION", "REGIME_PREDICATE"],
            "hard_requirements": ["OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN"],
            "preservation_obligations": [
                "PRESERVE:ACCESS",
                "PRESERVE:SCIENTIFIC_TARGET",
                "PRESERVE:RESOURCE_VECTOR",
            ],
            "cost": 2.0,
        },
        {
            "mechanic_id": "REV:GROW_METHOD_LANGUAGE",
            "kind": "GROW_LANGUAGE",
            "read_coordinates": ["EVIDENCE", "METHOD_LANGUAGE", "REPRESENTATION"],
            "write_coordinates": ["METHOD_LANGUAGE", "REPRESENTATION"],
            "preservation_obligations": [
                "PRESERVE:ACCESS",
                "PRESERVE:SCIENTIFIC_TARGET",
                "PRESERVE:RESOURCE_VECTOR",
            ],
            "cost": 3.0,
        },
    ]


_D0_HYPOTHESES = [
    {
        "hypothesis_id": "RESP:CURRENT_SEARCH_INCOMPLETE",
        "expected_observations": {
            "R6_EARNED": ["NO"],
            "EXACT_DP_VERIFICATION": ["INCOMPLETE", "FAILED"],
        },
        "support_evidence_ids": ["r6m-hostile-dp-vs-brute-status"],
    },
    {
        "hypothesis_id": "RESP:DONOR_FAMILY_INCOMPLETE",
        "expected_observations": {
            "R6_EARNED": ["NO"],
            "CHEMISTRY_DONOR_EXACT": ["YES_ALL_30"],
            "DPLUS_CLOSURE": ["UNTESTED", "VERIFIED_EQUAL"],
        },
        "support_evidence_ids": ["r6o-enlarged-tag-donor-closure-status"],
    },
    {
        "hypothesis_id": "RESP:REPRESENTATION_REGIME_UNCHARACTERIZED",
        "expected_observations": {
            "R6_EARNED": ["NO"],
            "R6_PROTECTED_SUBJECT_ACCESSED": ["NO"],
            "SUPPORT_DOMINANCE_LOCAL_INEQUALITY": ["VERIFIED_ZERO_VIOLATIONS"],
            "SUPPORT_DOMINANCE_FAMILY_CLOSURE": ["REFUTED_TAG_ANCHOR_REGIME"],
            "DPLUS_CLOSURE": ["REFUTED_SECOND_COUPLING_REGIME"],
            "CHEMISTRY_DONOR_EXACT": ["YES_ALL_30"],
            "REGIME_MEMBERSHIP_PREDICATE": ["ABSENT"],
            "WEIGHT2_CLOSURE": ["UNTESTED"],
        },
        "support_evidence_ids": [
            "r6n-tag-anchor-regime-characterization",
            "r6o-second-coupling-regime-note",
        ],
    },
    {
        "hypothesis_id": "RESP:METHOD_LANGUAGE_INADEQUATE",
        "expected_observations": {
            "R6_EARNED": ["NO"],
            "SUPPORT_DOMINANCE_FAMILY_CLOSURE": ["REFUTED_TAG_ANCHOR_REGIME"],
            "DPLUS_CLOSURE": ["REFUTED_SECOND_COUPLING_REGIME"],
            "REGIME_MEMBERSHIP_PREDICATE": ["PRESENT"],
        },
        "support_evidence_ids": ["r6n-post-gate-diagnosis-not-frozen-gate"],
    },
]


def _bindings():
    return {
        "RESP:CURRENT_SEARCH_INCOMPLETE": ["REV:SEARCH_CURRENT_ALPHABET"],
        "RESP:DONOR_FAMILY_INCOMPLETE": ["REV:ABSORB_DONOR"],
        "RESP:REPRESENTATION_REGIME_UNCHARACTERIZED": [
            "REV:SPLIT_REPRESENTATION_REGIME"
        ],
        "RESP:METHOD_LANGUAGE_INADEQUATE": ["REV:GROW_METHOD_LANGUAGE"],
    }


POST_R6O_DIAGNOSIS_CAMPAIGN_MANIFEST = {
    "schema": "ORION.ResearchCampaignManifest.v1",
    "campaign_id": "orion-q:post-r6o-diagnosis",
    "claim_id": "orion-q:post-r6o-gap-responsibility",
    "description": (
        "Dual-harness benchmark Lane B: single native decision cycle diagnosing the "
        "epistemic layer responsible for the remaining ORION-Q MAX gap after the "
        "committed R6N/R6O receipts, decided by the production orion.transfer.v2 / "
        "orion.self_orion modules over receipt-transcribed observations."
    ),
    "authority_ceiling": "BENCHMARK_DIAGNOSTIC_ONLY__BELOW_R6",
    "initial_phase": "D0",
    "initial_observations": {
        "R6_EARNED": "NO",
        "R6_PROTECTED_SUBJECT_ACCESSED": "NO",
        "SUPPORT_DOMINANCE_LOCAL_INEQUALITY": "VERIFIED_ZERO_VIOLATIONS",
        "SUPPORT_DOMINANCE_FAMILY_CLOSURE": "REFUTED_TAG_ANCHOR_REGIME",
        "DPLUS_CLOSURE": "REFUTED_SECOND_COUPLING_REGIME",
        "CHEMISTRY_DONOR_EXACT": "YES_ALL_30",
        "EXACT_DP_VERIFICATION": "HOSTILE_EXACT_ALL_PANELS",
        "REGIME_MEMBERSHIP_PREDICATE": "ABSENT",
        "WEIGHT2_CLOSURE": "UNTESTED",
    },
    "protected_refs": [
        {
            "ref_id": "FRESH:R6:STRETCHED_N2_DUCC2",
            "path": "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt",
            "blob": "6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd",
            "released": False,
        }
    ],
    "capabilities": {
        "orion_q.record_search_current_alphabet": _recording_capability(
            "REV:SEARCH_CURRENT_ALPHABET"
        ),
        "orion_q.record_absorb_donor": _recording_capability("REV:ABSORB_DONOR"),
        "orion_q.record_split_representation_regime": _recording_capability(
            "REV:SPLIT_REPRESENTATION_REGIME"
        ),
        "orion_q.record_grow_method_language": _recording_capability(
            "REV:GROW_METHOD_LANGUAGE"
        ),
        "orion_q.record_regime_characterization": _recording_capability(
            "COMPUTE:REGIME_CHARACTERIZATION"
        ),
        "orion_q.record_receipt_replay": _recording_capability(
            "COMPUTE:RECEIPT_REPLAY"
        ),
    },
    "phases": {
        "D0": {
            "active_hard_obligations": [],
            "responsibility_hypotheses": _D0_HYPOTHESES,
            "interface_checks": _interface_checks(),
            "revision_mechanics": _revision_mechanics(),
            "mechanic_obligation_states": {
                "OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN": "UNRESOLVED"
            },
            "computation_actions": [
                {
                    "action_id": "COMPUTE:REGIME_CHARACTERIZATION",
                    "kind": "CHARACTERIZE_REPRESENTATION_REGIME",
                    "expected_decision_value": 2.0,
                    "cost": 1.0,
                    "discharges_obligations": [
                        "OBLIGATION:REGIME_MEMBERSHIP_PREDICATE_FROZEN"
                    ],
                },
                {
                    "action_id": "COMPUTE:RECEIPT_REPLAY",
                    "kind": "REPLAY_CURRENT_LANGUAGE",
                    "expected_decision_value": 0.1,
                    "cost": 1.0,
                },
            ],
            "responsibility_bindings": _bindings(),
            "shadow_allowed_revision_ids": [
                "REV:SEARCH_CURRENT_ALPHABET",
                "REV:ABSORB_DONOR",
                "REV:GROW_METHOD_LANGUAGE",
            ],
            "selected_capabilities": {
                "REV:SEARCH_CURRENT_ALPHABET": "orion_q.record_search_current_alphabet",
                "REV:ABSORB_DONOR": "orion_q.record_absorb_donor",
                "REV:SPLIT_REPRESENTATION_REGIME": "orion_q.record_split_representation_regime",
                "REV:GROW_METHOD_LANGUAGE": "orion_q.record_grow_method_language",
                "COMPUTE:REGIME_CHARACTERIZATION": "orion_q.record_regime_characterization",
                "COMPUTE:RECEIPT_REPLAY": "orion_q.record_receipt_replay",
            },
        },
        "DIAGNOSIS_RECORDED": {
            "terminal": True,
            "terminal_name": "POST_R6O_DIAGNOSIS_RECORDED__NOT_SELF_AUTHORIZING",
            "active_hard_obligations": [],
        },
    },
}

__all__ = ["POST_R6O_DIAGNOSIS_CAMPAIGN_MANIFEST"]
