from __future__ import annotations

import pytest

from orion.knowledge.rate import (
    PROVIDER_BUDGETS,
    BudgetBasis,
    ProviderBudget,
    RateGate,
    UnknownProvider,
)


class _Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _gate() -> tuple[RateGate, _Clock]:
    clock = _Clock()
    return RateGate(clock=clock), clock


def test_every_budget_states_where_its_numbers_came_from() -> None:
    """A rate limit is a claim about someone else's service."""

    for budget in PROVIDER_BUDGETS.values():
        assert budget.citation.strip()
        assert budget.min_interval_seconds >= 0
        assert budget.max_concurrent >= 1


def test_an_unverified_provider_is_refused_rather_than_defaulted() -> None:
    """Inventing a budget would apply an unverified limit to an
    uncharacterized service — the failure mode is a block, not a slow run."""

    gate, _ = _gate()
    with pytest.raises(UnknownProvider):
        gate.wait_seconds("some_new_api")


def test_arxiv_spacing_is_enforced_at_three_seconds() -> None:
    gate, clock = _gate()
    assert gate.ready("arxiv")
    gate.record_request("arxiv")

    assert gate.wait_seconds("arxiv") == 3.0
    clock.advance(2.9)
    assert not gate.ready("arxiv")
    clock.advance(0.1)
    assert gate.ready("arxiv")


def test_one_providers_idleness_does_not_fund_anothers_burst() -> None:
    """The reason budgets are per-provider and never a shared pool.

    arXiv's three seconds does not become negotiable because Crossref was quiet.
    """

    gate, clock = _gate()
    gate.record_request("arxiv")
    for _ in range(20):
        clock.advance(0.05)
        if gate.ready("crossref_single"):
            gate.record_request("crossref_single")

    assert not gate.ready("arxiv")
    assert gate.wait_seconds("arxiv") == pytest.approx(2.0, abs=1e-6)


def test_a_server_backoff_can_only_extend_the_wait() -> None:
    """Taking the smaller value would let a short header override a longer
    standing budget."""

    gate, _ = _gate()
    gate.record_request("arxiv")  # 3s standing budget
    gate.record_retry_after("arxiv", 0.5)

    assert gate.wait_seconds("arxiv") == 3.0

    gate.record_retry_after("arxiv", 30.0)
    assert gate.wait_seconds("arxiv") == 30.0


def test_a_backoff_survives_a_later_request_record() -> None:
    """A 429 must not be cleared by the next call's shorter standing interval."""

    gate, _ = _gate()
    gate.record_retry_after("openalex", 60.0)
    gate.record_request("openalex")  # 0.1s standing interval
    assert gate.wait_seconds("openalex") == 60.0


def test_a_negative_backoff_is_refused() -> None:
    gate, _ = _gate()
    with pytest.raises(ValueError):
        gate.record_retry_after("arxiv", -1.0)


def test_crossref_list_is_tighter_than_single_lookup() -> None:
    """Measured asymmetry: list endpoints are 3-5x tighter, so they are
    budgeted separately rather than sharing one 'crossref' allowance."""

    assert (
        PROVIDER_BUDGETS["crossref_list"].min_interval_seconds
        > PROVIDER_BUDGETS["crossref_single"].min_interval_seconds
    )


def test_an_unpublished_limit_is_assumed_conservatively_not_ignored() -> None:
    """Europe PMC publishes no rate limit. An unstated limit is not an absent
    one, so the budget is marked ASSUMED and set conservatively."""

    budget = PROVIDER_BUDGETS["europepmc"]
    assert budget.basis is BudgetBasis.ASSUMED
    assert budget.min_interval_seconds >= 1.0


def test_a_budget_must_cite_its_basis() -> None:
    with pytest.raises(ValueError):
        ProviderBudget(
            provider="x",
            min_interval_seconds=1.0,
            max_concurrent=1,
            basis=BudgetBasis.ASSUMED,
            citation="   ",
        )
