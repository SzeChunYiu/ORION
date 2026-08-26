from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

import pytest

import fiberguard_cleanroom as fg


def test_graph_generator_and_primitives_are_exact() -> None:
    masks = fg.graph_masks()
    assert len(masks) == 2**15
    assert masks[0] == 0
    assert masks[-1] == 2**15 - 1

    triangle = sum(1 << fg.GRAPH_EDGE_INDEX[edge] for edge in ((0, 1), (0, 2), (1, 2)))
    path = sum(1 << fg.GRAPH_EDGE_INDEX[edge] for edge in ((0, 1), (1, 2)))
    assert fg.graph_representation(triangle) == ((0, 0, 0, 2, 2, 2), 1)
    assert fg.graph_chromatic_by_coloring(triangle) == 3
    assert fg.graph_chromatic_by_independent_cover(triangle) == 3
    assert fg.graph_chromatic_by_coloring(path) == 2
    assert fg.graph_chromatic_by_independent_cover(path) == 2
    assert fg.graph_endpoint_check(triangle) == {
        "representation": ((0, 0, 0, 2, 2, 2), 1),
        "target": 3,
    }


def test_graph_refinements_count_simple_four_cycles_not_induced_cycles() -> None:
    complete = 2**15 - 1
    features = fg.graph_refinements(complete)
    assert features == {
        "clique_number": 6,
        "component_count": 1,
        "four_cycle_count": 45,
    }


def test_cover_generator_and_dual_targets_are_exact() -> None:
    families = fg.cover_families()
    assert len(families) == 155_106
    assert families == tuple(sorted(families))
    assert len(families) == len(set(families))

    family = (0b00001, 0b00011, 0b00100, 0b01000, 0b10000)
    assert fg.cover_representation(family) == (
        (1, 1, 1, 1, 2),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    )
    assert fg.cover_size_by_subset_search(family) == 4
    assert fg.cover_size_by_mask_dp(family) == 4
    assert fg.cover_endpoint_check(family) == {
        "representation": fg.cover_representation(family),
        "target": 4,
    }


def test_cover_refinements_have_frozen_shapes() -> None:
    family = (1, 2, 4, 8, 16)
    assert fg.cover_refinements(family) == {
        "element_frequency_multiset": (1, 1, 1, 1, 1),
        "pairwise_union_multiset": (2,) * 10,
        "triple_intersection_multiset": (0,) * 10,
    }


def test_cnf_generator_representation_and_dual_targets_are_exact() -> None:
    clauses = fg.binary_clauses()
    assert len(clauses) == 24
    assert len(clauses) == len(set(clauses))
    assert all(abs(a) != abs(b) for a, b in clauses)
    assert all(abs(a) < abs(b) for a, b in clauses)

    formula = ((1, 2), (1, -2), (-1, 2), (-1, -2), (3, 4))
    expected_representation = (
        ((2, 2), (2, 2), (1, 0), (1, 0)),
        (4, 0, 0, 0, 0, 1),
    )
    assert fg.cnf_representation(formula) == expected_representation
    assert fg.cnf_count_by_truth_table(formula) == 0
    assert fg.cnf_count_by_clause_recursion(formula) == 0
    assert fg.cnf_endpoint_check(formula) == {
        "representation": expected_representation,
        "target": 0,
    }


def test_cnf_refinements_preserve_signed_pair_binding() -> None:
    formula = ((1, 2), (1, -2), (-1, 2), (-1, -2), (3, 4))
    features = fg.cnf_refinements(formula)
    assert features["global_clause_sign_type_counts"] == (1, 2, 2)
    assert features["unlabeled_signed_pair_profiles"] == (
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (1, 1, 1, 1),
    )
    assert features["labeled_signed_pair_profile"][0] == (1, 1, 1, 1)
    assert features["labeled_signed_pair_profile"][-1] == (1, 0, 0, 0)


def test_cnf_formula_generator_has_exact_combinatorial_denominator() -> None:
    formulas = fg.cnf_formulas()
    assert len(formulas) == 42_504
    assert formulas[0] == tuple(fg.binary_clauses()[:5])
    assert formulas[-1] == tuple(fg.binary_clauses()[-5:])


def test_generic_audit_selects_endpoint_deterministically_and_checks_it_third_way() -> None:
    checked: list[int] = []

    def checker(value: int) -> dict[str, object]:
        checked.append(value)
        return {"representation": (value % 2,), "target": value // 2}

    result = fg.audit_records(
        instances=(0, 1, 2, 3, 4, 5),
        representation=lambda value: (value % 2,),
        target_solvers=(lambda value: value // 2, lambda value: divmod(value, 2)[0]),
        candidates={"mod_three": lambda value: value % 3},
        serialize_instance=lambda value: value,
        endpoint_checker=checker,
    )

    assert result["instance_count"] == 6
    assert result["representation_fibre_count"] == 2
    assert result["ambiguous_fibre_count"] == 2
    assert result["maximum_target_diameter"] == 2
    assert result["selected_endpoint_fibre"] == {
        "fibre_multiplicity": 3,
        "high_target": 2,
        "high_witness": 4,
        "low_target": 0,
        "low_witness": 0,
        "representation": [0],
    }
    assert result["candidate_refinements"]["mod_three"] == {
        "ambiguous_fibre_count": 0,
        "fibre_count": 6,
        "maximum_target_diameter": 0,
    }
    assert checked == [0, 4]


def test_audit_rejects_duplicate_instances_and_solver_disagreement() -> None:
    kwargs = {
        "representation": lambda value: (value,),
        "candidates": {},
        "serialize_instance": lambda value: value,
        "endpoint_checker": lambda value: {"representation": (value,), "target": value},
    }
    with pytest.raises(ValueError, match="duplicate instance"):
        fg.audit_records(
            instances=(1, 1),
            target_solvers=(lambda value: value, lambda value: value),
            **kwargs,
        )
    with pytest.raises(fg.TargetSolverDisagreement, match="target solvers disagree"):
        fg.audit_records(
            instances=(1,),
            target_solvers=(lambda value: value, lambda value: value + 1),
            **kwargs,
        )


def test_audit_rejects_third_checker_disagreement() -> None:
    with pytest.raises(fg.EndpointCheckerDisagreement, match="endpoint checker"):
        fg.audit_records(
            instances=(0, 2),
            representation=lambda value: (0,),
            target_solvers=(lambda value: value, lambda value: value),
            candidates={},
            serialize_instance=lambda value: value,
            endpoint_checker=lambda value: {"representation": (0,), "target": value + 1},
        )


def test_canonical_payload_hash_is_order_independent_and_tamper_evident() -> None:
    left = {"b": [2, 1], "a": {"x": True}}
    right = {"a": {"x": True}, "b": [2, 1]}
    assert fg.canonical_json_bytes(left) == fg.canonical_json_bytes(right)
    sealed = fg.seal_payload(left, manifest_sha256="a" * 64)
    assert fg.verify_sealed_payload(sealed)
    sealed["payload"]["b"][0] = 999
    assert not fg.verify_sealed_payload(sealed)


def test_manifest_is_deterministic_and_detects_tampering(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a\n")
    (tmp_path / "b.txt").write_text("b\n")
    first = fg.build_manifest(tmp_path, ("b.txt", "a.txt"))
    second = fg.build_manifest(tmp_path, ("a.txt", "b.txt"))
    assert first == second
    assert first["files"] == [
        {"bytes": 2, "path": "a.txt", "sha256": hashlib.sha256(b"a\n").hexdigest()},
        {"bytes": 2, "path": "b.txt", "sha256": hashlib.sha256(b"b\n").hexdigest()},
    ]
    fg.verify_manifest(tmp_path, first)
    (tmp_path / "b.txt").write_text("tampered\n")
    with pytest.raises(fg.ManifestMismatch, match="b.txt"):
        fg.verify_manifest(tmp_path, first)


def test_packet_gate_rejects_placeholder_and_non_ancestor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    packet = tmp_path / "R8_PACKET_COMMIT.json"
    packet.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketCommit.v1",
                "packet_commit": "TO_BE_BOUND_AFTER_MATERIALIZATION",
                "base_commit": "0" * 40,
                "branch": "codex/five-paper-top-tier-r8-20260826",
            }
        )
    )
    with pytest.raises(fg.PacketIdentityUnresolved, match="placeholder"):
        fg.require_packet_identity(packet, repository=tmp_path)

    packet.write_text(
        json.dumps(
            {
                "schema": "ORION.FivePaperR8.PacketCommit.v1",
                "packet_commit": "1" * 40,
                "base_commit": "0" * 40,
                "branch": "codex/five-paper-top-tier-r8-20260826",
            }
        )
    )
    monkeypatch.setattr(fg, "_git_commit_exists", lambda *_: True)
    monkeypatch.setattr(fg, "_git_is_ancestor", lambda *_: False)
    with pytest.raises(fg.PacketIdentityMismatch, match="not an ancestor"):
        fg.require_packet_identity(packet, repository=tmp_path)


def test_non_outcome_fixture_validation_exposes_no_panel_result() -> None:
    receipt = fg.validate_non_outcome_fixtures()
    assert receipt["terminal"] == "NON_OUTCOME_FIXTURES_VALIDATED"
    assert receipt["independence_terminal"] == "CANNOT_CHECK"
    assert receipt["blinding_breach"] == "BLINDING_BREACH_ISSUE_BODY"
    forbidden = {
        "representation_fibre_count",
        "maximum_target_diameter",
        "candidate_refinements",
        "selected_endpoint_fibre",
    }
    assert forbidden.isdisjoint(receipt)


def test_protocol_domain_counts_are_derived_not_hard_coded_in_generators() -> None:
    assert fg.expected_domain_counts() == {
        "graphs": 1 << len(tuple(combinations(range(6), 2))),
        "set_cover": len(fg.cover_families()),
        "two_cnf": len(tuple(combinations(fg.binary_clauses(), 5))),
    }
