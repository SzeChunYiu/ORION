#!/usr/bin/env python3
"""Structural and finite witness checker for ORION13.EXTERNAL_COORDINATE_NECESSITY.v1."""
from __future__ import annotations

import copy
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "COORDINATE_NECESSITY_PROTOCOL_V1.json"


def projection(pattern, omitted):
    return tuple(bit for i, bit in enumerate(pattern) if i != omitted)


def verify_exclusive_witness_theorem(n_coordinates=7):
    checks = 0
    for omitted in range(n_coordinates):
        for base in itertools.product((0, 1), repeat=n_coordinates):
            other = list(base)
            other[omitted] ^= 1
            other = tuple(other)
            # The two cases differ only on the target coordinate.  Once that
            # coordinate is omitted they are observationally identical, so no
            # deterministic rule on the reduced projection can label both
            # opposite verdicts correctly.
            assert projection(base, omitted) == projection(other, omitted)
            checks += 1
    return checks


def validate(p):
    assert p["schema_version"] == "orion13.external-coordinate-necessity.v1"
    assert p["identity"] == "ORION13.EXTERNAL_COORDINATE_NECESSITY.v1"
    assert p["status"] == "DESIGN_ONLY__REFERENCE_OUTCOMES_NOT_OPENED_BY_THIS_PACKET"
    assert p["scientific_authority_delta"] == "NONE"
    assert len(p["semantic_coordinates"]) == 7
    assert set(p["priority_nonpolarity_coordinates"]) == set(p["semantic_coordinates"]) - {"polarity"}

    witness = p["exclusive_witness"]
    assert all(witness.values())

    acquisition = p["acquisition"]
    assert acquisition["candidate_selection_uses_final_gold_labels"] is False
    assert acquisition["candidate_replacement_after_adjudication_begins"] is False
    assert acquisition["minimum_candidates_per_nonpolarity_coordinate"] >= 10
    assert acquisition["target_minimum_source_families_per_coordinate"] >= 3
    assert acquisition["closed_world_absence_is_gold_negative"] is False

    gate = p["coordinate_support_gate"]
    assert gate["valid_exclusive_witnesses_min"] >= 5
    assert gate["source_families_min"] >= 3
    assert gate["bounded_witness_range"] == [1, 4]

    adj = p["independent_adjudication"]
    assert adj["required_when_source_lacks_explicit_relation"] is True
    assert adj["primary_adjudicators"] >= 2
    assert adj["pre_named_tiebreak_or_frozen_conflict_rule"] is True
    assert adj["orion_policy_output_hidden"] is True
    assert adj["retain_disagreements_and_abstentions"] is True
    assert adj["programme_generated_label_counts_as_external_gold"] is False

    assert p["analysis_order"] == [
        "exclusive_witness_audit",
        "complete_frozen_corpus_reduct_and_core",
        "policy_comparison",
    ]
    assert "CANNOT_CHECK_COORDINATE_STRATUM_UNAVAILABLE" in p["terminals"]
    assert "CANNOT_CHECK_EXTERNAL_ADJUDICATION" in p["terminals"]


def expect_reject(base, mutator):
    candidate = copy.deepcopy(base)
    mutator(candidate)
    try:
        validate(candidate)
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError("hostile protocol mutation accepted")


def main():
    p = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    validate(p)
    witness_checks = verify_exclusive_witness_theorem()
    mutations = [
        lambda x: x["acquisition"].__setitem__("candidate_selection_uses_final_gold_labels", True),
        lambda x: x["acquisition"].__setitem__("candidate_replacement_after_adjudication_begins", True),
        lambda x: x["acquisition"].__setitem__("closed_world_absence_is_gold_negative", True),
        lambda x: x["coordinate_support_gate"].__setitem__("valid_exclusive_witnesses_min", 1),
        lambda x: x["independent_adjudication"].__setitem__("primary_adjudicators", 1),
        lambda x: x["independent_adjudication"].__setitem__("orion_policy_output_hidden", False),
        lambda x: x["analysis_order"].reverse(),
    ]
    for mutation in mutations:
        expect_reject(p, mutation)

    print(
        "ORION13_COORDINATE_NECESSITY_PROTOCOL_V1_PASS "
        f"exclusive_witness_projection_checks={witness_checks} "
        f"hostile_protocol_mutations={len(mutations)} outcomes_accessed=NONE"
    )


if __name__ == "__main__":
    main()
