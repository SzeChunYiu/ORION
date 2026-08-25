"""Frozen ORION-P2 discovery tasks over the controlled index.

A task pairs a research question with a `ProtectedGold` the system never sees.
The gold is not authored by hand: it is computed by applying the topic's
relevance rule to every document in the world, so the denominator is complete by
construction and a test can recompute it rather than trust it.

Each `CaseFamily` isolates one mechanism the paper claims:

- `COMPLETE_GOLD_MULTIROUTE` — gold spread across routes, so single-route
  coverage is bounded above no matter the budget spent;
- `ROUTE_EXHAUSTION` — a route stops yielding new material, so route-stop can be
  separated from task-stop;
- `UNAVAILABLE_ROUTE` — a provider goes down mid-run, leaving gold that is
  *censored* rather than absent, so closing the task as complete is an error a
  fail-closed system does not make;
- `EXTRACTION_QUESTION_SHIFT` — the extraction question changes mid-task, so a
  reread of already-read material is legitimate rather than wasteful;
- `DUPLICATE_IDENTITY` — republications and a revision are both present, so
  duplicate processing and legitimate reread must be told apart.

The record-level `task_family` emitted for every one of these is
`offline_complete_gold`, the single P2 family PROTOCOL_V1 froze for this world.
`CaseFamily` is internal structure and never travels as `task_family`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .corpus import (
    DiscoveryRoute,
    DiscoveryWorld,
    Topic,
    is_relevant,
    sha256_digest,
)

TASK_SCHEMA_VERSION = "orion.p2.discovery-task.v1"

#: The only value that may appear as `task_family` in a result record. The
#: protocol froze five families; this world is one of them, and inventing a
#: sixth would put results outside the frozen design.
PROTOCOL_TASK_FAMILY = "offline_complete_gold"

#: Routes for which probe keys are published to the candidate. CITATION is
#: excluded because it is snowball-based: seeds are withheld and probes are
#: discovered during execution, not announced upfront.
PUBLISHED_PROBE_ROUTES = (
    DiscoveryRoute.LEXICAL,
    DiscoveryRoute.SEMANTIC,
    DiscoveryRoute.REFORMULATION,
    DiscoveryRoute.RESTRICTED,
)

#: Number of probes published per route per topic. Bound at 4 to hold
#: difficulty fixed while N moves from 20 to 390 tasks.
PUBLISHED_PROBES_PER_ROUTE = 4


class CaseFamily(str, Enum):
    COMPLETE_GOLD_MULTIROUTE = "complete_gold_multiroute"
    ROUTE_EXHAUSTION = "route_exhaustion"
    UNAVAILABLE_ROUTE = "unavailable_route"
    EXTRACTION_QUESTION_SHIFT = "extraction_question_shift"
    DUPLICATE_IDENTITY = "duplicate_identity"


@dataclass(frozen=True)
class Budget:
    """Matched resources. A system that wins by spending more has not won.

    `max_route_calls` is set below the cost of enumerating every published probe
    on every route. Exhaustive probing is therefore not a strategy, and route
    allocation and stopping become the thing under measurement.
    """

    max_route_calls: int
    max_reads: int
    max_tool_calls: int
    max_model_tokens: int
    max_wallclock_seconds: float

    def __post_init__(self) -> None:
        if min(self.max_route_calls, self.max_reads, self.max_tool_calls) < 1:
            raise ValueError("every budget dimension must admit at least one action")
        if self.max_model_tokens < 1 or self.max_wallclock_seconds <= 0:
            raise ValueError("token and wall-clock budgets must be positive")

    def as_json(self) -> dict[str, Any]:
        return {
            "max_route_calls": self.max_route_calls,
            "max_reads": self.max_reads,
            "max_tool_calls": self.max_tool_calls,
            "max_model_tokens": self.max_model_tokens,
            "max_wallclock_seconds": self.max_wallclock_seconds,
        }


@dataclass(frozen=True)
class RouteAvailability:
    """When a route stops being usable, and how it fails.

    `goes_unavailable_after_calls` is a transport failure: the provider is gone
    and whatever it held is *censored*, not absent. `goes_flat_after_calls` is
    exhaustion: the route still answers but has nothing new. Conflating them is
    the error the paper's typed route/task stop separation exists to prevent —
    one licenses switching routes, neither licenses closing the task.
    """

    route: DiscoveryRoute
    goes_unavailable_after_calls: int | None = None
    goes_flat_after_calls: int | None = None

    def as_json(self) -> dict[str, Any]:
        return {
            "route": self.route.value,
            "goes_unavailable_after_calls": self.goes_unavailable_after_calls,
            "goes_flat_after_calls": self.goes_flat_after_calls,
        }


@dataclass(frozen=True)
class ProtectedGold:
    """Host-owned labels. Never handed to a system under test.

    Every collection is a tuple. A frozen dataclass holding a dict or a set is
    still mutable through the reference, and this object is the one thing in the
    study a candidate must not be able to touch.
    """

    gold_doc_ids: tuple[str, ...]
    gold_content_identities: tuple[str, ...]
    route_reachable_identities: tuple[tuple[str, tuple[str, ...]], ...]
    censored_content_identities: tuple[str, ...]
    unreachable_content_identities: tuple[str, ...]
    relevance_rule_concepts: tuple[str, ...]
    #: Whether `gold_content_identities` is the COMPLETE relevant set, which is
    #: what makes a recall denominator valid. True by construction in this
    #: study: the world is synthetic and enumerable, and the gold set is built
    #: from every relevant document in it, so nothing relevant exists outside
    #: the label set.
    #:
    #: A task built over a real corpus must set this False. Recall against a
    #: partial gold set is not a lower bound on recall -- it is a ratio whose
    #: denominator is unknown, and reporting it as recall is the failure this
    #: flag exists to prevent.
    gold_set_complete: bool = True

    def reachable_via(self, route: DiscoveryRoute) -> tuple[str, ...]:
        for name, identities in self.route_reachable_identities:
            if name == route.value:
                return identities
        return ()

    def as_json(self) -> dict[str, Any]:
        return {
            "gold_doc_ids": list(self.gold_doc_ids),
            "gold_content_identities": list(self.gold_content_identities),
            "route_reachable_identities": [
                {"route": name, "content_identities": list(items)}
                for name, items in self.route_reachable_identities
            ],
            "censored_content_identities": list(self.censored_content_identities),
            "unreachable_content_identities": list(self.unreachable_content_identities),
            "relevance_rule_concepts": list(self.relevance_rule_concepts),
        }


@dataclass(frozen=True)
class PublicView:
    """Exactly what a system under test may read.

    No gold, no reachability map, no relevance rule. The access-control boundary
    the protocol's `hidden_labels` policy requires, enforced by types rather than
    by discipline: a system's `run` signature cannot name anything else.

    Citation probes are absent on purpose. A system may chain from a document
    identifier only after actually retrieving that document, which is what
    snowballing is; publishing the seed list up front would turn it into another
    keyword list.
    """

    task_id: str
    question: str
    initial_extraction_question: str
    available_routes: tuple[str, ...]
    route_probes: tuple[tuple[str, tuple[str, ...]], ...]
    budget: Budget

    def probes_for(self, route: DiscoveryRoute) -> tuple[str, ...]:
        for name, probes in self.route_probes:
            if name == route.value:
                return probes
        return ()


@dataclass(frozen=True)
class DiscoveryTask:
    task_id: str
    case_family: CaseFamily
    topic_id: str
    question: str
    extraction_questions: tuple[str, ...]
    extraction_shift_after_reads: int | None
    availability: tuple[RouteAvailability, ...]
    budget: Budget
    protected_gold: ProtectedGold
    public_route_probes: tuple[tuple[str, tuple[str, ...]], ...]
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.extraction_questions:
            raise ValueError(f"{self.task_id}: an extraction question is required")
        if len(self.extraction_questions) > 1 and self.extraction_shift_after_reads is None:
            raise ValueError(f"{self.task_id}: a second extraction question needs a shift point")
        lowered = self.task_id.lower()
        for identity in self.protected_gold.gold_content_identities:
            if identity.lower() in lowered:
                raise ValueError(f"{self.task_id}: task id leaks a gold identity")

    @property
    def task_family(self) -> str:
        """The protocol-frozen family every record carries."""

        return PROTOCOL_TASK_FAMILY

    @property
    def public_view(self) -> PublicView:
        return PublicView(
            task_id=self.task_id,
            question=self.question,
            initial_extraction_question=self.extraction_questions[0],
            available_routes=tuple(sorted(item.route.value for item in self.availability)),
            route_probes=self.public_route_probes,
            budget=self.budget,
        )

    def availability_for(self, route: DiscoveryRoute) -> RouteAvailability | None:
        for item in self.availability:
            if item.route is route:
                return item
        return None

    def as_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "case_family": self.case_family.value,
            "task_family": self.task_family,
            "topic_id": self.topic_id,
            "question": self.question,
            "extraction_questions": list(self.extraction_questions),
            "extraction_shift_after_reads": self.extraction_shift_after_reads,
            "availability": [item.as_json() for item in self.availability],
            "budget": self.budget.as_json(),
            "protected_gold": self.protected_gold.as_json(),
            "public_route_probes": [
                {"route": name, "probes": list(probes)} for name, probes in self.public_route_probes
            ],
            "notes": self.notes,
        }


# Routes whose probe vocabulary is published to the system. CITATION is excluded:
# its probes are document identifiers, earned by retrieval rather than given.
PUBLISHED_PROBE_ROUTES: tuple[DiscoveryRoute, ...] = (
    DiscoveryRoute.LEXICAL,
    DiscoveryRoute.SEMANTIC,
    DiscoveryRoute.REFORMULATION,
    DiscoveryRoute.RESTRICTED,
)

#: Probes published per route per task: the task's own key plus decoys drawn from
#: other topics.
#:
#: This is bounded rather than world-wide, and the bound is what keeps a larger
#: world the *same* measurement rather than a harder one. `DEFAULT_BUDGET`'s
#: `max_route_calls` is deliberately set below the cost of enumerating every
#: published probe on every route, so with four published routes the search space
#: a system faces is `4 * PUBLISHED_PROBES_PER_ROUTE = 16` against a 12-call
#: budget. Publishing all 78 topics' keys instead would make that 312 against 12,
#: and the semantic route — whose correct key shares no token with the question by
#: construction, so lexical scoring cannot order it — would stop being a bounded
#: trial and become a lottery. Recall would collapse for every system, and the
#: collapse would be an artifact of the enlarged denominator rather than anything
#: about route governance.
#:
#: Four is therefore not a free parameter: it is the value the superseded 20-task
#: world published (one key per route per topic, four topics), held fixed so that
#: raising N changes the denominator and nothing else.
PUBLISHED_PROBES_PER_ROUTE = 4

#: Stride used to pick decoys. Coprime with nothing in particular — it only has to
#: be deterministic and to walk away from the home position, which it does.
_DECOY_STRIDE = 7

DEFAULT_BUDGET = Budget(
    max_route_calls=12,
    max_reads=24,
    max_tool_calls=48,
    max_model_tokens=120_000,
    max_wallclock_seconds=120.0,
)

#: Read budgets are per-family because each family measures a different waste.
#: `DUPLICATE_IDENTITY` is tightened until re-reading a republication actually
#: costs recall — a duplicate-processing metric that no budget ever binds is
#: measuring nothing. `EXTRACTION_QUESTION_SHIFT` is loosened so that the
#: legitimate rereads the shift creates are affordable; charging them against a
#: budget sized for one frame would punish the correct behaviour.
_FAMILY_READ_BUDGET: dict[str, int] = {
    CaseFamily.DUPLICATE_IDENTITY.value: 12,
    CaseFamily.EXTRACTION_QUESTION_SHIFT.value: 30,
}


def _budget_for(family: CaseFamily) -> Budget:
    reads = _FAMILY_READ_BUDGET.get(family.value, DEFAULT_BUDGET.max_reads)
    if reads == DEFAULT_BUDGET.max_reads:
        return DEFAULT_BUDGET
    return Budget(
        max_route_calls=DEFAULT_BUDGET.max_route_calls,
        max_reads=reads,
        max_tool_calls=DEFAULT_BUDGET.max_tool_calls,
        max_model_tokens=DEFAULT_BUDGET.max_model_tokens,
        max_wallclock_seconds=DEFAULT_BUDGET.max_wallclock_seconds,
    )


def _route_key_index(
    world: DiscoveryWorld,
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Map each published route to the sorted (topic, key) pairs that route accepts.

    Derived from the corpus rather than declared alongside it: a topic's key on a
    route is the key its own relevant documents carry there. A separately authored
    map could drift away from the documents it claims to describe; this one cannot.
    """

    collected: dict[str, list[tuple[str, str]]] = {
        route.value: [] for route in PUBLISHED_PROBE_ROUTES
    }
    for topic in sorted(world.topics, key=lambda item: item.topic_id):
        # Relevance is decided once per topic and reused across routes; deciding it
        # per route would rescan the whole corpus four times over.
        relevant = [item for item in world.documents if is_relevant(item, topic)]
        for route in PUBLISHED_PROBE_ROUTES:
            keys: set[str] = set()
            for document in relevant:
                keys.update(document.keys_for(route))
            for key in sorted(keys):
                collected[route.value].append((topic.topic_id, key))
    return {name: tuple(pairs) for name, pairs in collected.items()}


def published_probes(
    route_index: dict[str, tuple[tuple[str, str], ...]],
    topic_id: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """The task's own probe on each published route, plus deterministic decoys.

    Decoys are real keys belonging to other topics, so calling one costs a route
    call and returns records that the system's own screening must reject — which is
    what makes probe selection, and therefore the route-call budget, bind.
    """

    published: list[tuple[str, tuple[str, ...]]] = []
    for route in PUBLISHED_PROBE_ROUTES:
        pairs = route_index[route.value]
        total = len(pairs)
        if total == 0:
            published.append((route.value, ()))
            continue
        home = next(
            (position for position, (owner, _) in enumerate(pairs) if owner == topic_id),
            None,
        )
        if home is None:
            raise ValueError(f"{topic_id}: no {route.value} key found in the corpus")
        positions = [home]
        wanted = min(PUBLISHED_PROBES_PER_ROUTE, total)
        # Walk the stride for at most one full lap, then fill any shortfall by
        # ascending scan. The lap bound matters: when the stride and the list length
        # share a factor the walk visits only a subset of positions and would
        # otherwise spin forever looking for a candidate it can never reach.
        for step in range(1, total + 1):
            if len(positions) >= wanted:
                break
            candidate = (home + step * _DECOY_STRIDE) % total
            if candidate not in positions:
                positions.append(candidate)
        for candidate in range(total):
            if len(positions) >= wanted:
                break
            if candidate not in positions:
                positions.append(candidate)
        published.append(
            (route.value, tuple(sorted(pairs[position][1] for position in positions)))
        )
    return tuple(published)


def _reachability(
    world: DiscoveryWorld, topic: Topic
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Which gold works each route can reach, derived from the corpus itself.

    Citation reachability is derived from reference edges rather than declared
    separately, so the map cannot drift away from the graph it describes.
    """

    gold_docs = [item for item in world.documents if is_relevant(item, topic)]
    reachable: list[tuple[str, tuple[str, ...]]] = []
    for route in DiscoveryRoute:
        identities: set[str] = set()
        if route is DiscoveryRoute.CITATION:
            for seed in world.documents:
                for target in world.citation_reachable(seed.doc_id):
                    document = world.by_id.get(target)
                    if document is not None and is_relevant(document, topic):
                        identities.add(document.content_identity)
        else:
            for document in gold_docs:
                if document.keys_for(route):
                    identities.add(document.content_identity)
        reachable.append((route.value, tuple(sorted(identities))))
    return tuple(reachable)


def _build_gold(
    world: DiscoveryWorld,
    topic: Topic,
    availability: tuple[RouteAvailability, ...],
    reachable: tuple[tuple[str, tuple[str, ...]], ...] | None = None,
) -> ProtectedGold:
    # `_reachability` is pure in (world, topic) and costs a full corpus scan plus a
    # walk of every reference edge. Availability only splits its output into live
    # and censored, so the caller computes it once per topic and passes it to all
    # five case families rather than paying for it five times.
    reachable = _reachability(world, topic) if reachable is None else reachable
    all_identities = set(world.relevant_content_identities(topic))

    live_routes = {
        item.route
        for item in availability
        if item.goes_unavailable_after_calls is None
    }
    reachable_live: set[str] = set()
    reachable_any: set[str] = set()
    for name, identities in reachable:
        reachable_any.update(identities)
        if DiscoveryRoute(name) in live_routes:
            reachable_live.update(identities)

    return ProtectedGold(
        gold_doc_ids=world.relevant_doc_ids(topic),
        gold_content_identities=tuple(sorted(all_identities)),
        route_reachable_identities=reachable,
        # Censored: relevant, reachable in principle, but only through a route
        # this task takes away. Absence of evidence produced by a dead provider
        # is not evidence of absence.
        censored_content_identities=tuple(sorted(reachable_any - reachable_live)),
        unreachable_content_identities=tuple(sorted(all_identities - reachable_any)),
        relevance_rule_concepts=tuple(sorted(topic.required_concepts)),
    )


_ALL_ROUTES_LIVE = tuple(RouteAvailability(route) for route in DiscoveryRoute)


def build_tasks(world: DiscoveryWorld) -> tuple[DiscoveryTask, ...]:
    """Author one task per (topic, case family). Gold is computed, never typed in."""

    route_index = _route_key_index(world)
    tasks: list[DiscoveryTask] = []

    for topic in world.topics:
        probes = published_probes(route_index, topic.topic_id)
        reachable = _reachability(world, topic)
        slug = topic.topic_id.removeprefix("topic-")
        base_question = f"Identify every study addressing {topic.label.lower()}."
        primary_extraction = f"What does this record report about {topic.label.lower()}?"

        specs: tuple[tuple[CaseFamily, dict[str, Any]], ...] = (
            (
                CaseFamily.COMPLETE_GOLD_MULTIROUTE,
                {
                    "availability": _ALL_ROUTES_LIVE,
                    "extraction_questions": (primary_extraction,),
                    "extraction_shift_after_reads": None,
                    "notes": "All routes live. Gold is split across routes, so no single route reaches it all.",
                },
            ),
            (
                CaseFamily.ROUTE_EXHAUSTION,
                {
                    "availability": tuple(
                        RouteAvailability(route, goes_flat_after_calls=2)
                        if route is DiscoveryRoute.LEXICAL
                        else RouteAvailability(route)
                        for route in DiscoveryRoute
                    ),
                    "extraction_questions": (primary_extraction,),
                    "extraction_shift_after_reads": None,
                    "notes": "The lexical route runs dry after two calls. Route-stop is licensed; task-stop is not.",
                },
            ),
            (
                CaseFamily.UNAVAILABLE_ROUTE,
                {
                    "availability": tuple(
                        RouteAvailability(route, goes_unavailable_after_calls=1)
                        if route is DiscoveryRoute.RESTRICTED
                        else RouteAvailability(route)
                        for route in DiscoveryRoute
                    ),
                    "extraction_questions": (primary_extraction,),
                    "extraction_shift_after_reads": None,
                    "notes": "The restricted provider dies after one call, censoring the gold only it reaches.",
                },
            ),
            (
                CaseFamily.EXTRACTION_QUESTION_SHIFT,
                {
                    "availability": _ALL_ROUTES_LIVE,
                    "extraction_questions": (
                        primary_extraction,
                        f"Which measurement or estimation procedure does this record use for {topic.label.lower()}?",
                    ),
                    "extraction_shift_after_reads": 3,
                    "notes": "The extraction question changes after three reads; rereads under the new frame are legitimate.",
                },
            ),
            (
                CaseFamily.DUPLICATE_IDENTITY,
                {
                    "availability": _ALL_ROUTES_LIVE,
                    "extraction_questions": (primary_extraction,),
                    "extraction_shift_after_reads": None,
                    "notes": "A republication and a revision are both in reach; one is a duplicate, the other is not.",
                },
            ),
        )

        for family, spec in specs:
            availability = spec["availability"]
            tasks.append(
                DiscoveryTask(
                    task_id=f"p2-{slug}-{family.value.replace('_', '-')}",
                    case_family=family,
                    topic_id=topic.topic_id,
                    question=base_question,
                    extraction_questions=spec["extraction_questions"],
                    extraction_shift_after_reads=spec["extraction_shift_after_reads"],
                    availability=availability,
                    budget=_budget_for(family),
                    protected_gold=_build_gold(world, topic, availability, reachable),
                    public_route_probes=probes,
                    notes=spec["notes"],
                )
            )

    return tuple(sorted(tasks, key=lambda item: item.task_id))


def suite_fingerprint(world: DiscoveryWorld, tasks: tuple[DiscoveryTask, ...]) -> str:
    """Content hash binding the exact frozen suite, gold included.

    The gold is inside the hash deliberately. A fingerprint over public material
    alone would let labels be swapped underneath a fixed identifier, and a result
    reported against a suite whose labels are unverifiable is not evidence.
    """

    return sha256_digest(
        {
            "schema_version": TASK_SCHEMA_VERSION,
            "world": world.as_json(),
            "tasks": [task.as_json() for task in sorted(tasks, key=lambda item: item.task_id)],
        }
    )


def task_from_json(payload: dict[str, Any]) -> DiscoveryTask:
    gold = payload["protected_gold"]
    return DiscoveryTask(
        task_id=payload["task_id"],
        case_family=CaseFamily(payload["case_family"]),
        topic_id=payload["topic_id"],
        question=payload["question"],
        extraction_questions=tuple(payload["extraction_questions"]),
        extraction_shift_after_reads=payload["extraction_shift_after_reads"],
        availability=tuple(
            RouteAvailability(
                DiscoveryRoute(item["route"]),
                goes_unavailable_after_calls=item["goes_unavailable_after_calls"],
                goes_flat_after_calls=item["goes_flat_after_calls"],
            )
            for item in payload["availability"]
        ),
        budget=Budget(**payload["budget"]),
        protected_gold=ProtectedGold(
            gold_doc_ids=tuple(gold["gold_doc_ids"]),
            gold_content_identities=tuple(gold["gold_content_identities"]),
            route_reachable_identities=tuple(
                (item["route"], tuple(item["content_identities"]))
                for item in gold["route_reachable_identities"]
            ),
            censored_content_identities=tuple(gold["censored_content_identities"]),
            unreachable_content_identities=tuple(gold["unreachable_content_identities"]),
            relevance_rule_concepts=tuple(gold["relevance_rule_concepts"]),
        ),
        public_route_probes=tuple(
            (item["route"], tuple(item["probes"])) for item in payload["public_route_probes"]
        ),
        notes=payload.get("notes", ""),
    )


__all__ = [
    "Budget",
    "CaseFamily",
    "DEFAULT_BUDGET",
    "DiscoveryTask",
    "PROTOCOL_TASK_FAMILY",
    "PUBLISHED_PROBES_PER_ROUTE",
    "PUBLISHED_PROBE_ROUTES",
    "ProtectedGold",
    "PublicView",
    "RouteAvailability",
    "TASK_SCHEMA_VERSION",
    "build_tasks",
    "published_probes",
    "suite_fingerprint",
    "task_from_json",
]
