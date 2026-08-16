from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum


class BudgetBasis(str, Enum):
    """Where a rate number came from, which decides how far to trust it."""

    PUBLISHED = "PUBLISHED"
    OBSERVED = "OBSERVED"
    ASSUMED = "ASSUMED"


@dataclass(frozen=True)
class ProviderBudget:
    """One provider's request discipline, with the provenance of the numbers.

    A rate limit is a claim about someone else's service, so it carries the same
    obligation as any other claim here: say where it came from. `ASSUMED` means
    nobody checked, and an assumed budget should be conservative, because the
    cost of being wrong is an IP block rather than a slow run.
    """

    provider: str
    min_interval_seconds: float
    max_concurrent: int
    basis: BudgetBasis
    citation: str

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("a budget must name its provider")
        if self.min_interval_seconds < 0:
            raise ValueError("minimum interval cannot be negative")
        if self.max_concurrent < 1:
            raise ValueError("a provider must allow at least one connection")
        if not self.citation.strip():
            raise ValueError("a budget must cite the basis for its numbers")


# Verified 2026-08-15/16. Deliberately literal about which are published limits
# and which were observed by probing, because the two failed differently: the
# published Semantic Scholar figure and the observed keyless behaviour disagree.
PROVIDER_BUDGETS: dict[str, ProviderBudget] = {
    "arxiv": ProviderBudget(
        provider="arxiv",
        min_interval_seconds=3.0,
        max_concurrent=1,
        basis=BudgetBasis.PUBLISHED,
        citation=(
            "arXiv API Terms of Use: no more than one request every three "
            "seconds, single connection, across all machines under your control"
        ),
    ),
    "semantic_scholar": ProviderBudget(
        provider="semantic_scholar",
        min_interval_seconds=1.0,
        max_concurrent=1,
        basis=BudgetBasis.PUBLISHED,
        citation=(
            "Semantic Scholar docs: introductory API-key rate limit is 1 RPS on "
            "all endpoints; keyless observed returning 429 immediately"
        ),
    ),
    "openalex": ProviderBudget(
        provider="openalex",
        min_interval_seconds=0.1,
        max_concurrent=2,
        basis=BudgetBasis.OBSERVED,
        citation=(
            "OpenAlex requires an API key since Feb 2026 and ignores mailto; "
            "keyless carries a $0.1/IP budget observed to 429 after ~3 list calls"
        ),
    ),
    "crossref_list": ProviderBudget(
        provider="crossref_list",
        min_interval_seconds=1.0,
        max_concurrent=1,
        basis=BudgetBasis.PUBLISHED,
        citation=(
            "Crossref limits changed 2025-12-01: list requests 1/s public, "
            "3/s polite; list is 3-5x tighter than single-DOI lookup"
        ),
    ),
    "crossref_single": ProviderBudget(
        provider="crossref_single",
        min_interval_seconds=0.2,
        max_concurrent=1,
        basis=BudgetBasis.PUBLISHED,
        citation="Crossref: single-DOI lookups 5/s public, 10/s polite",
    ),
    "pubmed": ProviderBudget(
        provider="pubmed",
        min_interval_seconds=1.0 / 3.0,
        max_concurrent=1,
        basis=BudgetBasis.PUBLISHED,
        citation=(
            "NCBI E-utilities: 3 requests/second without an API key, 10/s with; "
            "tool and email must be registered, not merely supplied"
        ),
    ),
    "europepmc": ProviderBudget(
        provider="europepmc",
        min_interval_seconds=1.0,
        max_concurrent=1,
        basis=BudgetBasis.ASSUMED,
        citation=(
            "Europe PMC publishes no rate limit; 1/s assumed conservatively "
            "because an unstated limit is not an absent one"
        ),
    ),
    "unpaywall": ProviderBudget(
        provider="unpaywall",
        min_interval_seconds=0.1,
        max_concurrent=1,
        basis=BudgetBasis.PUBLISHED,
        citation="Unpaywall: 100,000 calls/day; no per-second figure published",
    ),
}


class UnknownProvider(KeyError):
    """Raised rather than defaulting to an optimistic budget."""


@dataclass
class RateGate:
    """Per-provider request spacing over an injected clock.

    Budgets are strictly per provider. A shared pool would let one service's
    idleness fund another's burst, which is exactly how a client ends up
    exceeding the tightest limit it is subject to — arXiv's three seconds does
    not become negotiable because Crossref was quiet.

    The clock is injected so the policy can be tested without waiting, and so a
    caller can drive it from whatever time source it already trusts.
    """

    clock: Callable[[], float]
    budgets: Mapping[str, ProviderBudget] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.budgets is None:
            self.budgets = PROVIDER_BUDGETS
        self._next_allowed: dict[str, float] = {}

    def budget_for(self, provider: str) -> ProviderBudget:
        """Return a provider's budget, refusing to invent one.

        Falling back to a default for an unrecognised provider would silently
        apply a limit nobody verified to a service nobody characterized.
        """

        try:
            return self.budgets[provider]
        except KeyError as error:
            raise UnknownProvider(
                f"no verified rate budget for provider '{provider}'"
            ) from error

    def wait_seconds(self, provider: str) -> float:
        """How long to wait before this provider may be called again."""

        self.budget_for(provider)
        return max(0.0, self._next_allowed.get(provider, 0.0) - self.clock())

    def ready(self, provider: str) -> bool:
        return self.wait_seconds(provider) == 0.0

    def record_request(self, provider: str) -> float:
        """Register that a request was issued; returns the next allowed time."""

        budget = self.budget_for(provider)
        allowed = self.clock() + budget.min_interval_seconds
        self._next_allowed[provider] = max(
            allowed, self._next_allowed.get(provider, 0.0)
        )
        return self._next_allowed[provider]

    def record_retry_after(self, provider: str, seconds: float) -> float:
        """Honour a server's explicit back-off, which always dominates.

        A `Retry-After` is the service stating its own limit for this moment. It
        can only extend the wait, never shorten it: taking the smaller of the
        two would let a short back-off header override a longer standing budget.
        """

        if seconds < 0:
            raise ValueError("retry-after cannot be negative")
        self.budget_for(provider)
        self._next_allowed[provider] = max(
            self._next_allowed.get(provider, 0.0), self.clock() + seconds
        )
        return self._next_allowed[provider]
