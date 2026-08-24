"""Deterministic systems for the frozen P2 offline complete-gold companion.

These implementations intentionally do *not* turn the synthetic world into a
query-formulation benchmark.  The world publishes route probe vocabularies and
its protocol says screening is deliberately easy; systems are therefore compared
on route allocation, route/task stopping, provider failure handling and read
identity governance.

No system can import the world, task or protected gold through its ``run``
signature.  Relevance screening below uses only the public question and the
bibliographic text returned by the host-owned session.  The conspicuous
``non-qualifying``/``unrelated`` markers are part of the public synthetic text and
are used only to keep screening from becoming the variable under test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable

from .cases import PublicView
from .corpus import DiscoveryRoute
from .runner import BudgetExhausted
from .systems import (
    DiscoverySession,
    RetrievedRecord,
    RouteOutcome,
    SystemReport,
    TransportStatus,
)

_GENERIC_WORDS = {
    "a",
    "across",
    "addressing",
    "all",
    "and",
    "every",
    "for",
    "identify",
    "in",
    "of",
    "on",
    "study",
    "the",
    "to",
}
_NEGATIVE_MARKERS = ("non-qualifying", "unrelated")


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower())) - _GENERIC_WORDS


def _probe_score(question: str, probe: str) -> float:
    """Outcome-blind ordering of public probes using lexical shape only.

    The score is deliberately weak.  Semantic/reformulation routes still require
    trial allocation because their correct probe can share no token with the
    surface question, which is exactly why the frozen world gives systems a
    bounded probe budget.
    """

    left = _tokens(question)
    right = _tokens(probe)
    union = left | right
    jaccard = (len(left & right) / len(union)) if union else 0.0
    sequence = SequenceMatcher(None, question.lower(), probe.lower()).ratio()
    return 0.7 * jaccard + 0.3 * sequence


def _ordered_probes(view: PublicView, route: DiscoveryRoute) -> tuple[str, ...]:
    return tuple(
        sorted(
            view.probes_for(route),
            key=lambda probe: (-_probe_score(view.question, probe), probe),
        )
    )


def _on_topic(record: RetrievedRecord, question: str) -> bool:
    text = f"{record.title} {record.abstract}".lower()
    if any(marker in text for marker in _NEGATIVE_MARKERS):
        return False
    question_terms = _tokens(question)
    record_terms = _tokens(text)
    # Other topics can share one generic retrieval word (for example ``search``)
    # but the authored current-topic records carry the full public topic label.
    return len(question_terms & record_terms) >= min(2, len(question_terms))


@dataclass(frozen=True)
class Policy:
    system_id: str
    mode: str
    ledger: str = "question"  # question | content | document
    ignore_unavailable: bool = False


@dataclass
class _RunContext:
    view: PublicView
    session: DiscoverySession
    policy: Policy
    claims: set[str] = field(default_factory=set)
    held: dict[str, RetrievedRecord] = field(default_factory=dict)
    read_keys: set[tuple[str, ...]] = field(default_factory=set)
    successful_routes: set[str] = field(default_factory=set)
    saw_unavailable: bool = False
    budget_exhausted: bool = False

    def _ledger_key(self, record: RetrievedRecord) -> tuple[str, ...]:
        if self.policy.ledger == "content":
            return (record.content_identity, record.content_digest)
        if self.policy.ledger == "document":
            return (
                record.doc_id,
                record.content_digest,
                self.session.current_extraction_question,
            )
        return (
            record.content_identity,
            record.content_digest,
            self.session.current_extraction_question,
        )

    def process(self, records: Iterable[RetrievedRecord]) -> None:
        """Read public on-topic records and turn only successful reads into claims."""

        for record in sorted(records, key=lambda item: item.doc_id):
            if self.budget_exhausted or not _on_topic(record, self.view.question):
                continue
            self.held.setdefault(record.doc_id, record)
            key = self._ledger_key(record)
            if key in self.read_keys:
                continue
            try:
                outcome = self.session.read(record.doc_id)
            except BudgetExhausted:
                self.budget_exhausted = True
                return
            # Use the host-returned frame in the stored key: the extraction frame
            # can advance exactly on this read.
            if self.policy.ledger == "content":
                actual_key = (record.content_identity, record.content_digest)
            elif self.policy.ledger == "document":
                actual_key = (record.doc_id, record.content_digest, outcome.extraction_question)
            else:
                actual_key = (
                    record.content_identity,
                    record.content_digest,
                    outcome.extraction_question,
                )
            self.read_keys.add(actual_key)
            self.claims.add(record.content_identity)

    def query(self, route: DiscoveryRoute, probe: str) -> RouteOutcome | None:
        if self.budget_exhausted:
            return None
        try:
            outcome = self.session.query(route.value, probe)
        except BudgetExhausted:
            self.budget_exhausted = True
            return None
        if outcome.status is TransportStatus.UNAVAILABLE:
            self.saw_unavailable = True
        return outcome

    def stop_route(self, route: DiscoveryRoute, reason: str) -> None:
        self.session.declare_route_stop(route.value, reason)

    def reread_for_new_question(self) -> None:
        """Exercise the question coordinate after the host advances the frame.

        With the full question-conditioned ledger this creates legitimate rereads.
        The ``content`` ablation suppresses them because its key has no question
        coordinate, which is the exact negative control frozen by P2.
        """

        if self.session.current_extraction_question == self.view.initial_extraction_question:
            return
        self.process(self.held.values())


def _explore_lexical(ctx: _RunContext) -> bool:
    probes = _ordered_probes(ctx.view, DiscoveryRoute.LEXICAL)
    if not probes:
        ctx.stop_route(DiscoveryRoute.LEXICAL, "no_public_probe")
        return False
    outcome = ctx.query(DiscoveryRoute.LEXICAL, probes[0])
    if outcome is None:
        ctx.stop_route(DiscoveryRoute.LEXICAL, "budget_exhausted")
        return False
    on_topic = tuple(item for item in outcome.records if _on_topic(item, ctx.view.question))
    ctx.process(on_topic)
    if on_topic:
        ctx.successful_routes.add(DiscoveryRoute.LEXICAL.value)
    ctx.stop_route(
        DiscoveryRoute.LEXICAL,
        "targeted_probe_complete" if on_topic else "targeted_probe_empty",
    )
    return bool(on_topic)


def _explore_public_route(
    ctx: _RunContext,
    route: DiscoveryRoute,
    *,
    verify_provider_state: bool = False,
) -> bool:
    """Try public probes in an outcome-blind order until this route finds the topic."""

    success_probe: str | None = None
    for probe in _ordered_probes(ctx.view, route):
        outcome = ctx.query(route, probe)
        if outcome is None:
            ctx.stop_route(route, "budget_exhausted")
            return False
        if outcome.status is TransportStatus.UNAVAILABLE:
            if ctx.policy.ignore_unavailable:
                # The negative ablation launders transport unavailability into an
                # apparently exhausted route.  It is intentionally wrong.
                ctx.saw_unavailable = False
                ctx.successful_routes.add(route.value)
                ctx.stop_route(route, "treated_unavailable_as_empty")
            else:
                ctx.stop_route(route, "provider_unavailable")
            return False
        on_topic = tuple(item for item in outcome.records if _on_topic(item, ctx.view.question))
        if not on_topic:
            continue
        ctx.process(on_topic)
        ctx.successful_routes.add(route.value)
        success_probe = probe
        break

    if success_probe is None:
        ctx.stop_route(route, "public_probe_space_exhausted")
        return False

    if verify_provider_state and not ctx.budget_exhausted:
        repeated = ctx.query(route, success_probe)
        if repeated is not None and repeated.status is TransportStatus.UNAVAILABLE:
            if ctx.policy.ignore_unavailable:
                ctx.saw_unavailable = False
                ctx.stop_route(route, "treated_unavailable_as_empty")
            else:
                ctx.stop_route(route, "provider_unavailable_after_success")
            return True

    ctx.stop_route(route, "targeted_probe_complete")
    return True


def _explore_citations(ctx: _RunContext) -> bool:
    seeds: list[RetrievedRecord] = []
    seen: set[str] = set()
    for record in sorted(ctx.held.values(), key=lambda item: item.doc_id):
        if not record.references:
            continue
        key = record.doc_id if ctx.policy.ledger == "document" else record.content_identity
        if key in seen:
            continue
        seen.add(key)
        seeds.append(record)

    found = False
    for seed in seeds:
        outcome = ctx.query(DiscoveryRoute.CITATION, seed.doc_id)
        if outcome is None:
            ctx.stop_route(DiscoveryRoute.CITATION, "budget_exhausted")
            return found
        if outcome.status is not TransportStatus.OK:
            continue
        on_topic = tuple(item for item in outcome.records if _on_topic(item, ctx.view.question))
        if on_topic:
            found = True
            ctx.process(on_topic)
    if found:
        ctx.successful_routes.add(DiscoveryRoute.CITATION.value)
    ctx.stop_route(
        DiscoveryRoute.CITATION,
        "snowball_seeds_exhausted" if seeds else "no_earned_seed",
    )
    return found


def _report(ctx: _RunContext, *, complete: bool, note: str) -> SystemReport:
    ctx.reread_for_new_question()
    return SystemReport(
        claimed_relevant_merged_source_ids=tuple(sorted(ctx.claims)),
        task_closed_as_complete=complete,
        abstained=False,
        notes=note,
    )


class OfflineDiscoverySystem:
    """One frozen policy presented through the common ``SystemUnderTest`` surface."""

    def __init__(self, policy: Policy) -> None:
        self.policy = policy
        self.system_id = policy.system_id

    def run(
        self,
        view: PublicView,
        session: DiscoverySession,
        *,
        seed: int,
    ) -> SystemReport:
        del seed  # deterministic systems; repeated seeds test harness stability
        ctx = _RunContext(view=view, session=session, policy=self.policy)
        mode = self.policy.mode

        if mode == "bm25":
            _explore_lexical(ctx)
            return _report(ctx, complete=True, note="lexical-only comparator")

        if mode == "dense":
            _explore_public_route(ctx, DiscoveryRoute.SEMANTIC)
            return _report(ctx, complete=True, note="semantic-route comparator")

        if mode in {"hybrid", "one_pass_rag"}:
            _explore_lexical(ctx)
            _explore_public_route(ctx, DiscoveryRoute.SEMANTIC)
            return _report(ctx, complete=True, note=f"{mode} comparator; no iterative route governance")

        if mode == "agentic_single_route":
            _explore_lexical(ctx)
            return _report(ctx, complete=True, note="agentic policy constrained to one route")

        if mode == "protocol_slr":
            _explore_lexical(ctx)
            _explore_citations(ctx)
            _explore_public_route(ctx, DiscoveryRoute.REFORMULATION)
            return _report(ctx, complete=True, note="keyword + snowball + reformulation protocol")

        if mode == "strong_new":
            _explore_lexical(ctx)
            _explore_public_route(ctx, DiscoveryRoute.RESTRICTED, verify_provider_state=True)
            _explore_public_route(ctx, DiscoveryRoute.SEMANTIC)
            _explore_public_route(ctx, DiscoveryRoute.REFORMULATION)
            complete = not ctx.saw_unavailable and not ctx.budget_exhausted
            return _report(ctx, complete=complete, note="exploratory adaptive multiroute comparator")

        if mode == "no_independence":
            _explore_lexical(ctx)
            _explore_public_route(ctx, DiscoveryRoute.REFORMULATION)
            return _report(
                ctx,
                complete=True,
                note="ablation counts shared-backend reformulation as independent closure evidence",
            )

        if mode == "route_stop_closes_task":
            _explore_lexical(ctx)
            return _report(
                ctx,
                complete=True,
                note="negative ablation: first route stop licenses task closure",
            )

        if mode == "coverage_authority":
            _explore_lexical(ctx)
            _explore_public_route(ctx, DiscoveryRoute.SEMANTIC)
            return _report(
                ctx,
                complete=True,
                note="negative ablation: a coverage diagnostic is promoted to stopping authority",
            )

        # Full ORION and the read/unavailability ablations share the same route
        # plan.  Independent backends are attempted before the shared lexical
        # reformulation route; citation seeds are earned rather than published.
        _explore_lexical(ctx)
        _explore_citations(ctx)
        _explore_public_route(ctx, DiscoveryRoute.RESTRICTED, verify_provider_state=True)
        _explore_public_route(ctx, DiscoveryRoute.SEMANTIC)
        _explore_public_route(ctx, DiscoveryRoute.REFORMULATION)

        if self.policy.ignore_unavailable:
            complete = not ctx.budget_exhausted and {
                DiscoveryRoute.LEXICAL.value,
                DiscoveryRoute.CITATION.value,
                DiscoveryRoute.RESTRICTED.value,
                DiscoveryRoute.SEMANTIC.value,
                DiscoveryRoute.REFORMULATION.value,
            }.issubset(ctx.successful_routes)
        else:
            complete = (
                not ctx.saw_unavailable
                and not ctx.budget_exhausted
                and {item.value for item in DiscoveryRoute}.issubset(ctx.successful_routes)
            )
        return _report(ctx, complete=complete, note=f"{self.system_id} frozen offline policy")


# Confirmatory comparator identifiers are byte-for-byte the ones frozen in
# PROTOCOL_V1.json.  The additional comparator is explicitly exploratory because
# adding it to the frozen confirmatory baseline set after design freeze would be
# a protocol change.
BASELINES: tuple[OfflineDiscoverySystem, ...] = (
    OfflineDiscoverySystem(Policy("bm25_keyword", "bm25")),
    OfflineDiscoverySystem(Policy("dense_retrieval", "dense")),
    OfflineDiscoverySystem(Policy("sparse_dense_hybrid", "hybrid")),
    OfflineDiscoverySystem(Policy("one_pass_rag", "one_pass_rag")),
    OfflineDiscoverySystem(Policy("agentic_single_route", "agentic_single_route")),
    OfflineDiscoverySystem(Policy("protocol_driven_systematic_review", "protocol_slr")),
)

EXPLORATORY_BASELINES: tuple[OfflineDiscoverySystem, ...] = (
    OfflineDiscoverySystem(Policy("adaptive_multiroute_exploratory", "strong_new")),
)

ORION_FULL = OfflineDiscoverySystem(Policy("orion_full", "orion_full"))

ABLATIONS: tuple[OfflineDiscoverySystem, ...] = (
    OfflineDiscoverySystem(Policy("no_route_independence_check", "no_independence")),
    OfflineDiscoverySystem(
        Policy("no_question_conditioned_read_ledger", "orion_full", ledger="content")
    ),
    OfflineDiscoverySystem(Policy("route_stop_can_close_task", "route_stop_closes_task")),
    OfflineDiscoverySystem(
        Policy(
            "no_unavailable_route_open_state",
            "orion_full",
            ignore_unavailable=True,
        )
    ),
    OfflineDiscoverySystem(Policy("coverage_diagnostic_controls_stopping", "coverage_authority")),
    OfflineDiscoverySystem(
        Policy("no_content_identity_dedup", "orion_full", ledger="document")
    ),
)

ALL_SYSTEMS: tuple[OfflineDiscoverySystem, ...] = (
    *BASELINES,
    *EXPLORATORY_BASELINES,
    ORION_FULL,
    *ABLATIONS,
)


def system_by_id(system_id: str) -> OfflineDiscoverySystem:
    for system in ALL_SYSTEMS:
        if system.system_id == system_id:
            return system
    raise KeyError(system_id)


__all__ = [
    "ABLATIONS",
    "ALL_SYSTEMS",
    "BASELINES",
    "EXPLORATORY_BASELINES",
    "ORION_FULL",
    "OfflineDiscoverySystem",
    "Policy",
    "system_by_id",
]
