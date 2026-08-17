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
- `UNAVAILABLE_ROUTE` — a provider goes down mid-run, opening an obligation that
  makes the material *censored* rather than absent;
- `EXTRACTION_QUESTION_SHIFT` — the extraction frame changes mid-task, so a
  reread is legitimate (`NEW_FRAME`) rather than wasteful;
- `EXTRACTION_SCHEMA_SHIFT` — the extraction schema version changes mid-task,
  exercising `NEW_SCHEMA`. This family exists because binding B14 types
  `read_encounter.decision_before_execution` over the full `ReadDecision` enum,
  and a state no task can reach is a state no metric can measure.

There is deliberately no duplicate-identity family. Republications and revisions
are present in every topic, so duplicate processing is measured everywhere by
O3's encounter-denominator rates; a separate label would have been a task
structurally identical to the multiroute one wearing a different name.

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

TASK_SCHEMA_VERSION = "orion.p2.discovery-task.v2"

#: The only value that may appear as `task_family` in a result record. The
#: protocol froze five families; this world is one of them, and inventing a
#: sixth would put results outside the frozen design.
PROTOCOL_TASK_FAMILY = "offline_complete_gold"

#: Extraction schema versions. The second is reached only by the schema-shift
#: family and is what makes `ReadDecision.NEW_SCHEMA` reachable.
EXTRACTION_SCHEMA_V1 = "p2.extraction.v1"
EXTRACTION_SCHEMA_V2 = "p2.extraction.v2"


class CaseFamily(str, Enum):
    COMPLETE_GOLD_MULTIROUTE = "complete_gold_multiroute"
    ROUTE_EXHAUSTION = "route_exhaustion"
    UNAVAILABLE_ROUTE = "unavailable_route"
    EXTRACTION_QUESTION_SHIFT = "extraction_question_shift"
    EXTRACTION_SCHEMA_SHIFT = "extraction_schema_shift"


# Frozen resource ladder from STATISTICAL_PLAN_V1.json `matched_budget_policy`.
# A cap that is not a rung on this ladder cannot be written into a run manifest.
LADDER_QUERY_COUNT: tuple[int, ...] = (10, 20, 40, 80, 120, 200)
LADDER_TOOL_CALLS: tuple[int, ...] = (20, 40, 80, 160, 260, 400)
LADDER_MODEL_TOKENS: tuple[int, ...] = (100_000, 250_000, 500_000, 1_000_000, 2_000_000)
LADDER_WALLCLOCK_SECONDS: tuple[int, ...] = (300, 600, 1200, 1800, 3600)


@dataclass(frozen=True)
class Budget:
    """Matched resources, on the plan's frozen ladder.

    The four capped resources are exactly `matched_budget_policy.capped_resources`
    and every value must be a rung on its ladder, because a cap that is not a rung
    cannot legally be written into a run manifest. Caps are identical for every
    task and every system in the family, as the plan requires — there is no
    per-task tightening.

    Reads are charged against `tool_calls` rather than getting a cap of their own:
    a read *is* a tool call, and inventing a fifth capped resource would put the
    world outside the plan's budget-matching verification.
    """

    query_count: int
    tool_calls: int
    model_tokens: int
    wallclock_seconds: int

    def __post_init__(self) -> None:
        for name, value, ladder in (
            ("query_count", self.query_count, LADDER_QUERY_COUNT),
            ("tool_calls", self.tool_calls, LADDER_TOOL_CALLS),
            ("model_tokens", self.model_tokens, LADDER_MODEL_TOKENS),
            ("wallclock_seconds", self.wallclock_seconds, LADDER_WALLCLOCK_SECONDS),
        ):
            if value not in ladder:
                raise ValueError(f"{name}={value} is not a rung on the frozen ladder {ladder}")

    def as_json(self) -> dict[str, Any]:
        return {
            "query_count": self.query_count,
            "tool_calls": self.tool_calls,
            "model_tokens": self.model_tokens,
            "wallclock_seconds": self.wallclock_seconds,
        }


#: The suite's reference cap. `matched_budget_policy.cap_derivation_rule` derives
#: the final cap from the maximum consumption observed by any baseline during a
#: declared pilot — which cannot be run before any baseline exists. This is
#: therefore a *placeholder on the ladder*, frozen so the world's difficulty is a
#: checkable property, and the next phase must re-derive it from a pilot rather
#: than inherit it.
#:
#: The constraint that must survive re-derivation: `query_count` has to stay below
#: `PUBLISHED_PROBES_PER_ROUTE * len(PUBLISHED_PROBE_ROUTES)`, or a system can
#: enumerate every published probe and the task stops measuring route allocation.
REFERENCE_BUDGET = Budget(
    query_count=20,
    tool_calls=40,
    model_tokens=100_000,
    wallclock_seconds=300,
)

# Routes whose probe vocabulary is published to the system. CITATION is excluded:
# its probes are document identifiers, earned by retrieval rather than given.
PUBLISHED_PROBE_ROUTES: tuple[DiscoveryRoute, ...] = (
    DiscoveryRoute.LEXICAL,
    DiscoveryRoute.SEMANTIC,
    DiscoveryRoute.REFORMULATION,
    DiscoveryRoute.RESTRICTED,
)

#: Probes published per route per task: the task's own, plus decoys drawn from
#: other topics. Bounded per task rather than world-wide so the allocation problem
#: stays the same size as the corpus grows — publishing all 78 topics' probes
#: would turn a route-allocation task into a needle-in-a-haystack search, which is
#: query formulation and explicitly not what this world measures.
PUBLISHED_PROBES_PER_ROUTE = 12


@dataclass(frozen=True)
class RouteAvailability:
    """When a route stops being usable, and how it fails.

    `goes_unavailable_after_calls` is a transport failure: under O4 it opens an
    obligation, and whatever the route held is *censored*, not absent.
    `goes_flat_after_calls` is exhaustion: the route still answers and has nothing
    new. Conflating them is the error the typed route/task stop separation exists
    to prevent — one licenses switching routes, neither licenses closing the task.
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
            "gold_set_complete": self.gold_set_complete,
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
    initial_extraction_schema: str
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
    extraction_schemas: tuple[str, ...]
    extraction_shift_after_reads: int | None
    availability: tuple[RouteAvailability, ...]
    budget: Budget
    protected_gold: ProtectedGold
    public_route_probes: tuple[tuple[str, tuple[str, ...]], ...]
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.extraction_questions or not self.extraction_schemas:
            raise ValueError(f"{self.task_id}: an extraction question and schema are required")
        shifting = len(self.extraction_questions) > 1 or len(self.extraction_schemas) > 1
        if shifting and self.extraction_shift_after_reads is None:
            raise ValueError(f"{self.task_id}: a second frame or schema needs a shift point")
        lowered = self.task_id.lower()
        for identity in self.protected_gold.gold_content_identities:
            if identity.lower() in lowered:
                raise ValueError(f"{self.task_id}: task id leaks a gold identity")

    @property
    def task_family(self) -> str:
        """The protocol-frozen family every record carries."""

        return PROTOCOL_TASK_FAMILY

    @property
    def public_probe_digest(self) -> str:
        """Binds the derived probe vocabulary into the frozen suite hash.

        The probes themselves are recomputed from the world on load rather than
        stored per task — 48 probes on each of 390 tasks is most of a megabyte of
        duplicated strings. Storing the digest keeps the selection inside the
        fingerprint, so changing the decoy count changes the suite identity.
        """

        return sha256_digest(
            [{"route": name, "probes": list(probes)} for name, probes in self.public_route_probes]
        )

    @property
    def public_view(self) -> PublicView:
        return PublicView(
            task_id=self.task_id,
            question=self.question,
            initial_extraction_question=self.extraction_questions[0],
            initial_extraction_schema=self.extraction_schemas[0],
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
            "extraction_schemas": list(self.extraction_schemas),
            "extraction_shift_after_reads": self.extraction_shift_after_reads,
            "availability": [item.as_json() for item in self.availability],
            "budget": self.budget.as_json(),
            "protected_gold": self.protected_gold.as_json(),
            "public_probe_digest": self.public_probe_digest,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ProbeMap:
    """Each topic's own probe on each published route, built in one pass.

    Documents are named `<topic-slug>:<slug>`, so a single scan attributes every
    access key to its topic. Rebuilding this per task would be quadratic in the
    corpus, which at 78 topics and 1230 documents is the difference between a
    fast freeze and a slow one.
    """

    topic_ids: tuple[str, ...]
    probes: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]

    def probe(self, route: DiscoveryRoute, topic_id: str) -> str:
        for name, pairs in self.probes:
            if name != route.value:
                continue
            for candidate, value in pairs:
                if candidate == topic_id:
                    return value
        return ""


def build_probe_map(world: DiscoveryWorld) -> ProbeMap:
    by_route: dict[str, dict[str, set[str]]] = {
        route.value: {topic.topic_id: set() for topic in world.topics}
        for route in PUBLISHED_PROBE_ROUTES
    }
    slug_to_topic = {
        topic.topic_id.removeprefix("topic-"): topic.topic_id for topic in world.topics
    }
    for document in world.documents:
        slug = document.doc_id.split(":", 1)[0]
        topic_id = slug_to_topic.get(slug)
        if topic_id is None:
            continue
        for route in PUBLISHED_PROBE_ROUTES:
            by_route[route.value][topic_id].update(document.keys_for(route))
    return ProbeMap(
        topic_ids=tuple(item.topic_id for item in world.topics),
        probes=tuple(
            (
                route.value,
                tuple(
                    (topic_id, sorted(keys)[0] if keys else "")
                    for topic_id, keys in sorted(by_route[route.value].items())
                ),
            )
            for route in PUBLISHED_PROBE_ROUTES
        ),
    )


def published_probes(
    probe_map: ProbeMap, topic_id: str
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """The task's own probe per route, plus deterministic decoys from other topics.

    Selection strides through the sorted topic list rather than sampling, so it is
    stable across processes and independent of `PYTHONHASHSEED`.
    """

    topic_ids = list(probe_map.topic_ids)
    if topic_id not in topic_ids:
        raise KeyError(topic_id)
    home = topic_ids.index(topic_id)
    total = len(topic_ids)
    wanted = min(PUBLISHED_PROBES_PER_ROUTE, total)
    positions: list[int] = []
    step = 0
    while len(positions) < wanted:
        candidate = (home + step * 7) % total
        if candidate not in positions:
            positions.append(candidate)
        step += 1
        if step > total * 7:  # pragma: no cover - stride covers a full cycle first
            break

    published: list[tuple[str, tuple[str, ...]]] = []
    for route in PUBLISHED_PROBE_ROUTES:
        chosen = {probe_map.probe(route, topic_ids[position]) for position in positions}
        chosen.add(probe_map.probe(route, topic_id))
        published.append((route.value, tuple(sorted(item for item in chosen if item))))
    return tuple(published)


def _reachability(
    world: DiscoveryWorld, topic: Topic
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Which gold works each route can reach, derived from the corpus itself.

    Citation reachability is recomputed from the reference edges rather than
    declared separately, so the map cannot drift away from the graph it describes.
    """

    gold_docs = [item for item in world.documents if is_relevant(item, topic)]
    gold_ids = {item.doc_id for item in gold_docs}
    reachable: list[tuple[str, tuple[str, ...]]] = []
    for route in DiscoveryRoute:
        identities: set[str] = set()
        if route is DiscoveryRoute.CITATION:
            for seed in world.documents:
                for target in world.citation_reachable(seed.doc_id):
                    if target in gold_ids:
                        identities.add(world.by_id[target].content_identity)
        else:
            for document in gold_docs:
                if document.keys_for(route):
                    identities.add(document.content_identity)
        reachable.append((route.value, tuple(sorted(identities))))
    return tuple(reachable)


@dataclass(frozen=True)
class _TopicGoldBase:
    """Per-topic quantities shared by that topic's five tasks.

    Reachability is the expensive part and does not depend on the case family —
    only the censored split does. Recomputing it once per family made freezing
    five times slower for no additional truth.
    """

    doc_ids: tuple[str, ...]
    identities: tuple[str, ...]
    reachable: tuple[tuple[str, tuple[str, ...]], ...]
    concepts: tuple[str, ...]


def _gold_base(world: DiscoveryWorld, topic: Topic) -> _TopicGoldBase:
    return _TopicGoldBase(
        doc_ids=world.relevant_doc_ids(topic),
        identities=world.relevant_content_identities(topic),
        reachable=_reachability(world, topic),
        concepts=tuple(sorted(topic.required_concepts)),
    )


def _build_gold(
    base: _TopicGoldBase,
    availability: tuple[RouteAvailability, ...],
) -> ProtectedGold:
    reachable = base.reachable
    all_identities = set(base.identities)

    live_routes = {
        item.route for item in availability if item.goes_unavailable_after_calls is None
    }
    reachable_live: set[str] = set()
    reachable_any: set[str] = set()
    for name, identities in reachable:
        reachable_any.update(identities)
        if DiscoveryRoute(name) in live_routes:
            reachable_live.update(identities)

    return ProtectedGold(
        gold_doc_ids=base.doc_ids,
        gold_content_identities=tuple(sorted(all_identities)),
        route_reachable_identities=reachable,
        # Censored: relevant, reachable in principle, but only through a route
        # this task takes away. Absence of evidence produced by a dead provider
        # is not evidence of absence.
        censored_content_identities=tuple(sorted(reachable_any - reachable_live)),
        unreachable_content_identities=tuple(sorted(all_identities - reachable_any)),
        relevance_rule_concepts=base.concepts,
        # B6. True here because `base.identities` was derived by applying the
        # relevance rule to every document in the corpus, so the denominator is
        # the complete relevant set by construction; `test_gold_is_complete_by_
        # construction_for_every_task` recomputes the rule and checks it both
        # ways. Completeness is not the same property as reachability — gold
        # behind a dead provider is still in the denominator, and is accounted
        # for by `censored_content_identities` instead. The field exists because
        # the plan makes every complete-denominator metric CANNOT_CHECK when it
        # is false, which is what a live-corpus family would set.
        gold_set_complete=True,
    )


_ALL_ROUTES_LIVE = tuple(RouteAvailability(route) for route in DiscoveryRoute)


def build_tasks(world: DiscoveryWorld) -> tuple[DiscoveryTask, ...]:
    """Author one task per (topic, case family). Gold is computed, never typed in."""

    tasks: list[DiscoveryTask] = []
    probe_map = build_probe_map(world)

    for topic in world.topics:
        slug = topic.topic_id.removeprefix("topic-")
        probes = published_probes(probe_map, topic.topic_id)
        gold_base = _gold_base(world, topic)
        base_question = f"Identify every study addressing {topic.label.lower()}."
        primary = f"What does this record report about {topic.label.lower()}?"
        secondary = f"Which procedure does this record use for {topic.label.lower()}?"

        specs: tuple[tuple[CaseFamily, dict[str, Any]], ...] = (
            (
                CaseFamily.COMPLETE_GOLD_MULTIROUTE,
                {
                    "availability": _ALL_ROUTES_LIVE,
                    "questions": (primary,),
                    "schemas": (EXTRACTION_SCHEMA_V1,),
                    "shift": None,
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
                    "questions": (primary,),
                    "schemas": (EXTRACTION_SCHEMA_V1,),
                    "shift": None,
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
                    "questions": (primary,),
                    "schemas": (EXTRACTION_SCHEMA_V1,),
                    "shift": None,
                    "notes": "The restricted provider dies after one call, opening an obligation over the gold only it reaches.",
                },
            ),
            (
                CaseFamily.EXTRACTION_QUESTION_SHIFT,
                {
                    "availability": _ALL_ROUTES_LIVE,
                    "questions": (primary, secondary),
                    "schemas": (EXTRACTION_SCHEMA_V1,),
                    "shift": 3,
                    "notes": "The extraction question changes after three reads; rereads under the new frame are NEW_FRAME.",
                },
            ),
            (
                CaseFamily.EXTRACTION_SCHEMA_SHIFT,
                {
                    "availability": _ALL_ROUTES_LIVE,
                    "questions": (primary,),
                    "schemas": (EXTRACTION_SCHEMA_V1, EXTRACTION_SCHEMA_V2),
                    "shift": 3,
                    "notes": "The extraction schema changes after three reads; rereads under the new schema are NEW_SCHEMA.",
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
                    extraction_questions=spec["questions"],
                    extraction_schemas=spec["schemas"],
                    extraction_shift_after_reads=spec["shift"],
                    availability=availability,
                    budget=REFERENCE_BUDGET,
                    protected_gold=_build_gold(gold_base, availability),
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


def task_from_json(payload: dict[str, Any], probe_map: ProbeMap) -> DiscoveryTask:
    """Rebuild a task, recomputing its probe vocabulary from the frozen world."""

    gold = payload["protected_gold"]
    probes = published_probes(probe_map, payload["topic_id"])
    task = DiscoveryTask(
        task_id=payload["task_id"],
        case_family=CaseFamily(payload["case_family"]),
        topic_id=payload["topic_id"],
        question=payload["question"],
        extraction_questions=tuple(payload["extraction_questions"]),
        extraction_schemas=tuple(payload["extraction_schemas"]),
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
            gold_set_complete=bool(gold["gold_set_complete"]),
        ),
        public_route_probes=probes,
        notes=payload.get("notes", ""),
    )
    if task.public_probe_digest != payload["public_probe_digest"]:
        raise ValueError(
            f"{task.task_id}: recomputed probe vocabulary does not match the frozen digest"
        )
    return task


__all__ = [
    "Budget",
    "CaseFamily",
    "EXTRACTION_SCHEMA_V1",
    "EXTRACTION_SCHEMA_V2",
    "LADDER_MODEL_TOKENS",
    "LADDER_QUERY_COUNT",
    "LADDER_TOOL_CALLS",
    "LADDER_WALLCLOCK_SECONDS",
    "PROTOCOL_TASK_FAMILY",
    "PUBLISHED_PROBES_PER_ROUTE",
    "PUBLISHED_PROBE_ROUTES",
    "ProtectedGold",
    "ProbeMap",
    "PublicView",
    "REFERENCE_BUDGET",
    "build_probe_map",
    "RouteAvailability",
    "TASK_SCHEMA_VERSION",
    "DiscoveryTask",
    "build_tasks",
    "published_probes",
    "suite_fingerprint",
    "task_from_json",
]
