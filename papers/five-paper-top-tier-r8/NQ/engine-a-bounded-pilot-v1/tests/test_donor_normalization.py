from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from nq_engine_a.canonical import canonical_multiset
from nq_engine_a.group import GroupSpec, InputError
from nq_engine_a.normalization import (
    NormalizationWitness,
    declared_donor_images,
    declared_donor_normalization_witnesses,
    is_declared_donor_normalized,
    verify_normalization_witness,
)

ROOT = Path(__file__).resolve().parents[1]
E1 = (1, 0, 0)
E2 = (0, 1, 0)
E3 = (0, 0, 1)


def test_pointwise_donor_normalization_is_exact_anchor_and_multiplicity_condition() -> None:
    spec = GroupSpec(5, 3)
    normalized = [E1, E2, E2, E3, E3, E3, (1, 1, 1)]
    assert is_declared_donor_normalized(spec, normalized)
    assert is_declared_donor_normalized(spec, tuple(reversed(normalized)))
    assert not is_declared_donor_normalized(spec, [E1, E1, E2, E3])
    assert not is_declared_donor_normalized(spec, [E1, E2, (1, 1, 1)])


def test_strictly_ordered_basis_multiplicities_give_one_donor_image() -> None:
    spec = GroupSpec(5, 3)
    sequence = [E1, E2, E2, E3, E3, E3]
    images = declared_donor_images(spec, sequence)
    assert images == (tuple(sorted(sequence)),)


def test_equal_multiplicities_retain_residual_basis_choice_images_not_one_per_orbit() -> None:
    spec = GroupSpec(5, 3)
    sequence = [E1, E2, E3, (1, 1, 1)]
    images = declared_donor_images(spec, sequence)
    assert len(images) > 1
    assert canonical_multiset(spec, sequence) in images
    assert all(is_declared_donor_normalized(spec, image) for image in images)


def test_donor_orbit_slice_is_invariant_under_gl_transform_and_input_permutation() -> None:
    spec = GroupSpec(5, 3)
    sequence = [E1, E2, E3, (1, 1, 0), (2, 3, 4)]
    matrix = ((1, 1, 0), (0, 1, 1), (0, 0, 1))
    transformed = [spec.matvec(matrix, vector) for vector in reversed(sequence)]
    assert declared_donor_images(spec, transformed) == declared_donor_images(spec, sequence)


def test_every_emitted_image_has_a_machine_checkable_basis_witness() -> None:
    spec = GroupSpec(5, 3)
    sequence = [E1, E2, E3, (1, 1, 0), (2, 3, 4)]
    witnesses = declared_donor_normalization_witnesses(spec, sequence)
    assert tuple(witness.image for witness in witnesses) == declared_donor_images(spec, sequence)
    assert all(verify_normalization_witness(spec, sequence, witness) for witness in witnesses)


def test_hostile_or_mutated_normalization_witnesses_are_rejected() -> None:
    spec = GroupSpec(5, 3)
    sequence = [E1, E2, E2, E3, E3, E3]
    valid = declared_donor_normalization_witnesses(spec, sequence)[0]
    hostile = (
        object(),
        NormalizationWitness(basis=(E1, E1, E3), image=valid.image),
        NormalizationWitness(basis=(E2, E1, E3), image=valid.image),
        NormalizationWitness(basis=(E1, E2, (4, 4, 4)), image=valid.image),
        NormalizationWitness(basis=valid.basis, image=valid.image[:-1]),
        NormalizationWitness(
            basis=valid.basis, image=((*valid.image[0][:-1], 4), *valid.image[1:])
        ),
    )
    assert all(not verify_normalization_witness(spec, sequence, witness) for witness in hostile)


def test_rank_deficient_sources_have_no_declared_rank_three_images() -> None:
    spec = GroupSpec(5, 3)
    assert declared_donor_images(spec, [E1, E2, (1, 1, 0)]) == ()


def test_contract_rejects_the_wrong_group_or_hostile_sequence() -> None:
    with pytest.raises(InputError):
        declared_donor_images(GroupSpec(3, 3), [(1, 0, 0)])
    with pytest.raises(InputError):
        is_declared_donor_normalized(GroupSpec(5, 2), [(1, 0)])
    with pytest.raises(InputError):
        declared_donor_images(GroupSpec(5, 3), "not-a-sequence")


def test_frozen_normalization_contract_and_schema_are_machine_valid() -> None:
    contract = json.loads((ROOT / "DONOR_NORMALIZATION_CONTRACT.json").read_text())
    schema = json.loads((ROOT / "schemas" / "normalization-contract.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(contract, schema)
    assert contract["binding_terminal"] == "BOUND_MATHEMATICAL_NORMALIZATION"
    assert contract["enumeration_semantics"]["one_per_gl_orbit"] is False
    assert contract["local_diff"]["local_canonicalizer_one_per_gl_orbit"] is True
    assert contract["local_diff"]["adapter"] == "declared_donor_images"
    assert contract["exposure_markers"] == [
        "EXPECTED_OUTCOME_EXPOSURE",
        "ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK",
    ]


def test_normalization_binding_receipt_is_schema_valid_and_digest_bound() -> None:
    import hashlib

    receipt = json.loads((ROOT / "NORMALIZATION_BINDING_RECEIPT.json").read_text())
    schema = json.loads(
        (ROOT / "schemas" / "normalization-binding-receipt.schema.json").read_text()
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)
    assert receipt["binding_terminal"] == "BOUND_MATHEMATICAL_NORMALIZATION"
    assert (
        receipt["contract_sha256"]
        == hashlib.sha256((ROOT / "DONOR_NORMALIZATION_CONTRACT.json").read_bytes()).hexdigest()
    )
    assert (
        receipt["implementation_sha256"]
        == hashlib.sha256(
            (ROOT / "src" / "nq_engine_a" / "normalization.py").read_bytes()
        ).hexdigest()
    )
    assert receipt["test_sha256"] == hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    assert receipt["controls"]["gl_round_trip_mismatches"] == 0
    assert receipt["controls"]["hostile_witnesses_accepted"] == 0
    assert receipt["full_census_executed"] is False
