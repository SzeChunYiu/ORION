from __future__ import annotations

import inspect

from orion.study.p9.d1 import D1Domain, D1View
from orion.study.p9.d1_experiment import exact_relational_comparator
from orion.study.p9.s3_access import (
    serialized_exact_generic_comparator,
    serialized_generic_binding_features,
)
from orion.study.p9.s3_rotation import (
    DOMAIN_ORDER,
    generate_rotation_dataset,
    rotation_label_counts,
)


REFERENCE_WORKFLOW_DIGEST = "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"


def _sequence(row) -> list[str]:
    payload = row.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    assert isinstance(sequence, list)
    return list(map(str, sequence))


def test_frozen_adapter_still_accepts_only_serialized_sequence():
    assert tuple(inspect.signature(serialized_generic_binding_features).parameters) == ("sequence",)


def test_workflow_rotation_reproduces_immutable_d1_manifest():
    dataset = generate_rotation_dataset(D1Domain.WORKFLOW)
    assert dataset.manifest_digest == REFERENCE_WORKFLOW_DIGEST


def test_all_rotations_have_disjoint_instance_identities():
    for holdout in DOMAIN_ORDER:
        dataset = generate_rotation_dataset(holdout, train_instances_per_base_pair=3, dev_instances_per_base_pair=2, test_instances_per_base_pair=2)
        train = {row.instance_id for row in dataset.train}
        dev = {row.instance_id for row in dataset.dev}
        test = {row.instance_id for row in dataset.test}
        assert not (train & dev)
        assert not (train & test)
        assert not (dev & test)


def test_holdout_identity_is_not_visible_to_f1_adapter():
    source = inspect.getsource(serialized_generic_binding_features)
    for forbidden in ("domain", "split", "mutation_coordinates", "label", "instance_id"):
        assert forbidden not in source


def test_all_rotations_share_label_count_design():
    designs = []
    for holdout in DOMAIN_ORDER:
        dataset = generate_rotation_dataset(holdout, train_instances_per_base_pair=4, dev_instances_per_base_pair=2, test_instances_per_base_pair=3)
        designs.append(rotation_label_counts(dataset))
    assert designs[0] == designs[1] == designs[2]


def test_f2_matches_exact_typed_comparator_on_train_and_dev_for_every_rotation():
    # This is deliberately pre-protected: no test rows are inspected here.
    for holdout in DOMAIN_ORDER:
        dataset = generate_rotation_dataset(holdout)
        for row in (*dataset.train, *dataset.dev):
            assert serialized_exact_generic_comparator(_sequence(row)) == exact_relational_comparator(row)


def test_each_test_rotation_contains_double_corruptions_and_unresolved_cases():
    for holdout in DOMAIN_ORDER:
        dataset = generate_rotation_dataset(holdout, train_instances_per_base_pair=2, dev_instances_per_base_pair=1, test_instances_per_base_pair=4)
        assert any(len(row.mutation_coordinates) == 2 for row in dataset.test)
        assert any(row.label.value == "UNRESOLVED" for row in dataset.test)
