import pytest

from orion.study.p9.bootstrap import bootstrap_information_lattice


def test_bootstrap_information_lattice_is_strictly_resolving():
    summary = bootstrap_information_lattice()
    views = summary["views"]

    assert summary["world_count"] == 6
    assert summary["scientific_authority"] == "NONE_MODEL_EVALUATION_ONLY"

    assert views["SURFACE"]["unique_fingerprint_count"] == 3
    assert views["SURFACE"]["collision_count"] == 3
    assert views["SURFACE"]["deterministic_accuracy_ceiling"] == pytest.approx(0.5)
    assert views["SURFACE"]["is_identifying"] is False

    assert views["TOPOLOGY"]["unique_fingerprint_count"] == 3
    assert views["TOPOLOGY"]["collision_count"] == 3
    assert views["TOPOLOGY"]["deterministic_accuracy_ceiling"] == pytest.approx(0.5)
    assert views["TOPOLOGY"]["is_identifying"] is False

    assert views["TYPED"]["unique_fingerprint_count"] == 4
    assert views["TYPED"]["collision_count"] == 2
    assert views["TYPED"]["deterministic_accuracy_ceiling"] == pytest.approx(4 / 6)
    assert views["TYPED"]["is_identifying"] is False

    assert views["CURRENT"]["unique_fingerprint_count"] == 5
    assert views["CURRENT"]["collision_count"] == 1
    assert views["CURRENT"]["deterministic_accuracy_ceiling"] == pytest.approx(5 / 6)
    assert views["CURRENT"]["is_identifying"] is False

    assert views["SEMANTIC"]["unique_fingerprint_count"] == 6
    assert views["SEMANTIC"]["collision_count"] == 0
    assert views["SEMANTIC"]["deterministic_accuracy_ceiling"] == pytest.approx(1.0)
    assert views["SEMANTIC"]["is_identifying"] is True


def test_bootstrap_world_order_is_stable_and_family_explicit():
    summary = bootstrap_information_lattice()

    assert summary["world_ids"] == [
        "relation-support",
        "relation-defeat",
        "transport-compatible",
        "transport-obstructed",
        "history-clean",
        "history-negative",
    ]
