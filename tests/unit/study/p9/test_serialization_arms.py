"""The invertibility claim must be checked, and the check must be able to fail."""

from __future__ import annotations

import pytest

from orion.study.p9.d1 import (
    D1Domain,
    D1Split,
    D1View,
    SurfaceRemintScope,
    _split_instances,
)
from orion.study.p9.serialization_arms import (
    comparison_graph,
    parse_serialized,
    round_trip_typed,
    wl_histogram,
)


def _instances(domain: D1Domain, n: int = 2):
    return _split_instances(
        seed="unit",
        split=D1Split.TEST,
        domains=(domain,),
        instances_per_base_pair=n,
        include_double=True,
        surface_remint_scope=SurfaceRemintScope.PER_INSTANCE,
    )


@pytest.mark.parametrize("domain", list(D1Domain))
def test_serialized_view_round_trips_in_every_domain(domain: D1Domain) -> None:
    for inst in _instances(domain):
        typed = inst.model_payload(D1View.TYPED)
        tokens = inst.model_payload(D1View.TYPED_SERIALIZED)["sequence"]
        assert round_trip_typed(typed, tokens)


def test_round_trip_rejects_corruption() -> None:
    """A check that cannot fail is not a check."""
    inst = _instances(D1Domain.CACHE, 1)[0]
    typed = inst.model_payload(D1View.TYPED)
    tokens = list(inst.model_payload(D1View.TYPED_SERIALIZED)["sequence"])
    assert round_trip_typed(typed, tokens)
    assert not round_trip_typed(typed, tokens[:-1])
    assert not round_trip_typed(typed, [tokens[1], tokens[0]] + tokens[2:])
    assert not round_trip_typed(typed, [t.replace("=", "=X", 1) for t in tokens])


def test_nested_sequences_survive_the_parser() -> None:
    """``dependencies`` is a list of lists; a flat path split loses it."""
    inst = _instances(D1Domain.NUMERICAL, 1)[0]
    tokens = inst.model_payload(D1View.TYPED_SERIALIZED)["sequence"]
    recovered = parse_serialized(tokens)
    deps = recovered["left"]["dependencies"]
    assert isinstance(deps, list) and deps and isinstance(deps[0], list)


def test_comparison_graph_makes_agreement_a_degree_fact() -> None:
    inst = _instances(D1Domain.CACHE, 1)[0]
    labels, edges = comparison_graph(inst.model_payload(D1View.TYPED))
    degree = {i: 0 for i in range(len(labels))}
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
    # atom nodes shared by both methods reach degree 2, private atoms degree 1
    assert max(degree[i] for i in range(2, len(labels))) <= 2
    assert wl_histogram(labels, edges)
