"""Deterministic controlled index for the ORION-P2 offline discovery world.

The world exists to give discovery metrics a *complete denominator*. On the open
web nobody can enumerate every relevant paper, so recall has no legitimate
denominator and "we found 40" cannot be distinguished from "we found 40 of 41"
or "of 400". Here relevance is decided by a rule over authored content, so the
gold set is complete by construction and recall is a real quantity.

Two structures carry the paper's mechanisms:

*Heterogeneous reachability.* Relevant works are not all reachable the same way.
Some sit under the topic's surface vocabulary, some only under a paraphrase that
shares no token with it, some only by following a citation edge from a document
you must already hold, some only after the query is reformulated, and some
behind a provider that goes unavailable mid-run. A single-route system therefore
cannot reach the whole gold set no matter how much budget it spends, which is
what makes route diversity, marginal route gain and fail-closed coverage
measurable rather than decorative.

*Separated identity.* A work, a copy of that work and a revision of that work are
three different things. Near-duplicates share a content identity at a different
locator, so a system that counts locators inflates its own coverage. Revisions
share a content identity but change the content digest, so a reread of a revised
work is legitimate rather than wasteful — the distinction ORION's read ledger
(`orion.knowledge.identity.decide_read`) turns on.

Reachability is *declared*, never scored: a route call is a set-membership test
against authored access keys. This module contains no ranker, no similarity
function and no retrieval machinery, and must not acquire any — the study
measures route governance, not query formulation.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

CORPUS_SCHEMA_VERSION = "orion.p2.offline-gold-world.v1"


def canonical_bytes(payload: Any) -> bytes:
    """Serialize exactly as the programme's `publication_manifest.py` does.

    Replicated rather than imported: `research/paper-programme-v1/protocols/` is
    a protocol directory, not an installed package. The convention has to agree
    byte-for-byte or a hash minted here will not match one minted by programme
    tooling over the same object, and every frozen-artifact claim rests on that.
    """

    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


class DiscoveryRoute(str, Enum):
    """The channels through which a document can be reached.

    These are study-local names for reachability structure. `ROUTE_SPECS` binds
    each to the `orion.core.search.SearchRouteKind` a real ORION configuration
    would drive it with, so the next phase wires systems without re-deciding the
    mapping.
    """

    LEXICAL = "LEXICAL"
    SEMANTIC = "SEMANTIC"
    CITATION = "CITATION"
    REFORMULATION = "REFORMULATION"
    RESTRICTED = "RESTRICTED"


@dataclass(frozen=True)
class RouteSpec:
    """Backend and query-derivation identity for one route.

    `orion.knowledge.routes.assess_pair` refuses to treat two routes as
    independent capture occasions when they share a backend or a query
    derivation. Those identities are therefore part of the world, not of a
    system's configuration: whether a route pair *can* earn independence is a
    property of the index it hits.
    """

    route: DiscoveryRoute
    backend_identity: str
    query_derivation_identity: str
    orion_route_kind: str


# LEXICAL and REFORMULATION deliberately share `index:lexical`. They are
# nominally distinct routes over one backend — the negative case P2.H2 needs, and
# what reformulating a query against the same index actually is in practice. The
# other three hit genuinely different backends and can earn independence.
ROUTE_SPECS: tuple[RouteSpec, ...] = (
    RouteSpec(DiscoveryRoute.LEXICAL, "index:lexical", "derivation:surface-terms", "CURRENT_VOCABULARY"),
    RouteSpec(DiscoveryRoute.REFORMULATION, "index:lexical", "derivation:reformulated-terms", "LEXICAL_VARIANT"),
    RouteSpec(DiscoveryRoute.SEMANTIC, "index:embedding", "derivation:paraphrase", "FUNCTION_ONLY"),
    RouteSpec(DiscoveryRoute.CITATION, "graph:citation", "derivation:reference-edge", "CITATION_NEIGHBORHOOD"),
    RouteSpec(DiscoveryRoute.RESTRICTED, "provider:restricted", "derivation:restricted-terms", "LITERATURE_BRIDGE"),
)

ROUTE_SPEC_BY_ROUTE: dict[DiscoveryRoute, RouteSpec] = {
    spec.route: spec for spec in ROUTE_SPECS
}


@dataclass(frozen=True)
class Document:
    """One retrievable record: a copy of a work, at a locator, in a revision.

    `doc_id` identifies the copy. `content_identity` identifies the work, and is
    what recall is counted over — two locators holding the same work are one
    discovery. `content_digest` identifies this exact rendition, and is what a
    reread decision turns on: a revision keeps the work and changes the digest.
    """

    doc_id: str
    content_identity: str
    content_digest: str
    version: int
    title: str
    abstract: str
    venue: str
    year: int
    authors: tuple[str, ...]
    references: tuple[str, ...]
    concept_tags: tuple[str, ...]
    access_keys: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.doc_id.strip() or not self.content_identity.strip():
            raise ValueError("a document requires a locator and a content identity")
        if self.version < 1:
            raise ValueError("document versions start at 1")
        if len(set(self.access_keys)) != len(self.access_keys):
            raise ValueError(f"{self.doc_id}: duplicate access keys")

    def keys_for(self, route: DiscoveryRoute) -> tuple[str, ...]:
        return tuple(
            sorted(key for name, key in self.access_keys if name == route.value)
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content_identity": self.content_identity,
            "content_digest": self.content_digest,
            "version": self.version,
            "title": self.title,
            "abstract": self.abstract,
            "venue": self.venue,
            "year": self.year,
            "authors": list(self.authors),
            "references": list(self.references),
            "concept_tags": list(self.concept_tags),
            "access_keys": [list(pair) for pair in self.access_keys],
        }


@dataclass(frozen=True)
class Topic:
    """A research topic and the rule that decides relevance to it.

    `required_concepts` *is* the relevance rule. The gold set stored on a task is
    a materialized cache of applying this rule to the corpus; `relevant_doc_ids`
    below recomputes it. Keeping the rule separate from the cache is what makes
    completeness checkable instead of tautological — a test can recompute over
    every document and demand the two agree.
    """

    topic_id: str
    label: str
    required_concepts: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.required_concepts:
            raise ValueError("a topic without required concepts admits everything")

    def as_json(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "label": self.label,
            "required_concepts": list(self.required_concepts),
        }


def is_relevant(document: Document, topic: Topic) -> bool:
    """The relevance rule: a document is relevant iff it carries every required concept."""

    return set(topic.required_concepts).issubset(set(document.concept_tags))


@dataclass(frozen=True)
class DiscoveryWorld:
    """The frozen corpus plus its topics. Host-owned; systems never hold one."""

    schema_version: str
    seed: int
    documents: tuple[Document, ...]
    topics: tuple[Topic, ...]

    def __post_init__(self) -> None:
        ids = [item.doc_id for item in self.documents]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate document ids in corpus")
        known = set(ids)
        for document in self.documents:
            missing = sorted(set(document.references) - known)
            if missing:
                raise ValueError(f"{document.doc_id}: dangling references {missing}")
        # Host-side lookup indexes, built once. Rebuilding these per call turned
        # freezing the 78-topic world into a 22-second operation: `by_id` alone was
        # reconstructing a 1230-entry dict inside a loop over every topic.
        # `object.__setattr__` is how a frozen dataclass caches derived state.
        object.__setattr__(self, "_by_id", {item.doc_id: item for item in self.documents})
        postings: dict[tuple[str, str], list[str]] = {}
        for document in self.documents:
            for route_name, key in document.access_keys:
                postings.setdefault((route_name, key), []).append(document.doc_id)
        object.__setattr__(
            self, "_postings", {key: tuple(sorted(value)) for key, value in postings.items()}
        )

    @property
    def by_id(self) -> dict[str, Document]:
        """Host-internal document index. Systems never reach this — they get a
        `PublicIndex` projection with the relevance rule stripped out."""

        return self._by_id  # type: ignore[attr-defined,no-any-return]

    def topic(self, topic_id: str) -> Topic:
        for candidate in self.topics:
            if candidate.topic_id == topic_id:
                return candidate
        raise KeyError(topic_id)

    def relevant_doc_ids(self, topic: Topic) -> tuple[str, ...]:
        """Apply the relevance rule to every document. The complete denominator."""

        return tuple(
            sorted(item.doc_id for item in self.documents if is_relevant(item, topic))
        )

    def relevant_content_identities(self, topic: Topic) -> tuple[str, ...]:
        """The denominator recall is actually counted over: works, not copies."""

        return tuple(
            sorted(
                {item.content_identity for item in self.documents if is_relevant(item, topic)}
            )
        )

    def citation_reachable(self, seed_doc_id: str) -> tuple[str, ...]:
        """Documents reachable by following one reference edge out of a seed."""

        document = self.by_id.get(seed_doc_id)
        if document is None:
            return ()
        return tuple(sorted(set(document.references)))

    def lookup(self, route: DiscoveryRoute, probe: str) -> tuple[Document, ...]:
        """Every document whose authored access key for `route` equals `probe`.

        Pure set membership, deliberately. A scored or ranked lookup would make
        this module a retrieval system and the study a measurement of that
        retrieval system rather than of route governance.
        """

        index = self.by_id
        if route is DiscoveryRoute.CITATION:
            return tuple(
                index[item] for item in self.citation_reachable(probe) if item in index
            )
        return tuple(
            index[item]
            for item in self._postings.get((route.value, probe), ())  # type: ignore[attr-defined]
        )

    def probes_for(self, route: DiscoveryRoute) -> tuple[str, ...]:
        """Every probe that route accepts. Used to build public route vocabularies."""

        if route is DiscoveryRoute.CITATION:
            return tuple(
                sorted({item.doc_id for item in self.documents if item.references})
            )
        return tuple(
            sorted(
                key
                for (route_name, key) in self._postings  # type: ignore[attr-defined]
                if route_name == route.value
            )
        )

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "seed": self.seed,
            "documents": [item.as_json() for item in sorted(self.documents, key=lambda d: d.doc_id)],
            "topics": [item.as_json() for item in sorted(self.topics, key=lambda t: t.topic_id)],
        }

    @property
    def content_hash(self) -> str:
        return sha256_digest(self.as_json())


# --------------------------------------------------------------------------
# Generation
#
# Structure is authored; the seed varies only surface metadata and filler. A
# fully random world could not guarantee that every gold work is reachable
# without a repair pass, and a repair pass would make the reachability structure
# opaque to the reader — the opposite of what a controlled index is for.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class _Stem:
    """One half of a composed topic: a tag plus three token-disjoint vocabularies."""

    tag: str
    lexical: str
    semantic: str
    reformulation: str


# Topics are composed from a method stem and a domain stem rather than authored
# one by one. The statistical plan commits `offline_complete_gold` to N >= 385
# tasks, and 78 hand-written topics would be 78 chances to introduce a vocabulary
# collision by hand. Composition makes the invariants checkable instead: every
# topic's rule is a two-tag conjunction, so a document carrying one method tag and
# one domain tag satisfies exactly one topic, and the completeness checker
# verifies that over the whole corpus for every topic.
#
# Lexical and semantic vocabularies are globally token-disjoint. That is what
# makes paraphrase-only reachability real: no amount of lexical budget reaches a
# work whose only access key shares no token with the lexical key.
_METHODS: tuple[_Stem, ...] = (
    _Stem("capture_recapture", "capture recapture", "mark release resight", "abundance estimator"),
    _Stem("sequential_stopping", "sequential stopping", "halting criterion", "sample size reestimation"),
    _Stem("query_diversification", "query diversification", "probe spreading", "novelty maximisation"),
    _Stem("measurement_invariance", "measurement invariance", "scalar equivalence", "differential item functioning"),
    _Stem("active_screening", "active screening", "adaptive triage", "prioritised assessment"),
    _Stem("information_foraging", "information foraging", "patch residence", "scent following"),
    _Stem("federated_search", "federated search", "distributed broker", "cross provider merge"),
    _Stem("citation_snowballing", "citation snowballing", "reference chaining", "backward forward tracing"),
    _Stem("duplicate_detection", "duplicate detection", "near identical matching", "record linkage"),
    _Stem("relevance_feedback", "relevance feedback", "iterative refinement", "pseudo expansion"),
    _Stem("coverage_estimation", "coverage estimation", "unseen mass inference", "richness extrapolation"),
    _Stem("protocol_registration", "protocol registration", "prespecified declaration", "amendment tracking"),
    _Stem("provenance_tracking", "provenance tracking", "lineage recording", "audit trail"),
)

_DOMAINS: tuple[_Stem, ...] = (
    _Stem("clinical_trials", "clinical trials", "therapeutic studies", "randomised medicine"),
    _Stem("materials_science", "materials science", "condensed matter", "alloy discovery"),
    _Stem("ecology_surveys", "ecology surveys", "field census", "habitat sampling"),
    _Stem("software_engineering", "software engineering", "program construction", "build practice"),
    _Stem("astronomy_catalogues", "astronomy catalogues", "sky inventories", "transient archives"),
    _Stem("education_assessment", "education assessment", "learner appraisal", "classroom testing"),
)


@dataclass(frozen=True)
class _TopicPlan:
    topic_id: str
    label: str
    required_concepts: tuple[str, str]
    lexical_key: str
    semantic_key: str
    reformulation_key: str
    restricted_key: str
    partial_concept: str


def _topic_plans() -> tuple[_TopicPlan, ...]:
    plans: list[_TopicPlan] = []
    for method in _METHODS:
        for domain in _DOMAINS:
            slug = f"{method.tag}-{domain.tag}".replace("_", "-")
            plans.append(
                _TopicPlan(
                    topic_id=f"topic-{slug}",
                    label=f"{method.lexical.title()} in {domain.lexical}",
                    required_concepts=(method.tag, domain.tag),
                    lexical_key=f"{method.lexical} {domain.lexical}",
                    semantic_key=f"{method.semantic} {domain.semantic}",
                    reformulation_key=f"{method.reformulation} {domain.reformulation}",
                    restricted_key=f"restricted archive: {method.lexical} {domain.lexical}",
                    # A distractor carries one required tag and never both, so the
                    # two-tag rule excludes it while a lexical route still returns it.
                    partial_concept=method.tag,
                )
            )
    return tuple(plans)


_TOPIC_PLANS: tuple[_TopicPlan, ...] = _topic_plans()

_VENUES = (
    "Journal of Measurement Science",
    "Proceedings of Retrieval Systems",
    "Review Methodology Quarterly",
    "Transactions on Information Access",
    "Annals of Applied Statistics Practice",
)

_SURNAMES = (
    "Adeyemi", "Bakhtiari", "Castellanos", "Dvorak", "Eriksson", "Fujimoto",
    "Gruber", "Haldorsen", "Ibarra", "Jankowski", "Kowalczyk", "Lindqvist",
    "Mensah", "Nakagawa", "Oyelaran", "Petrov", "Quintero", "Rasmussen",
    "Sindhu", "Tanaka", "Ustinov", "Vasquez", "Wierzbicka", "Yamamoto",
)

_NOISE_CONCEPTS = (
    "compiler_optimization", "protein_folding", "orbital_mechanics",
    "sediment_transport", "market_microstructure", "phoneme_alignment",
    "graph_partitioning", "catalyst_design",
)


def _digest_of(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:32]


def _author_block(rng: random.Random) -> tuple[str, ...]:
    count = rng.randint(2, 4)
    chosen = rng.sample(sorted(_SURNAMES), count)
    return tuple(sorted(chosen))


def _make_document(
    *,
    doc_id: str,
    content_identity: str,
    version: int,
    title: str,
    abstract: str,
    concept_tags: tuple[str, ...],
    access_keys: tuple[tuple[str, str], ...],
    references: tuple[str, ...],
    rng: random.Random,
) -> Document:
    return Document(
        doc_id=doc_id,
        content_identity=content_identity,
        content_digest=_digest_of(content_identity, str(version), abstract),
        version=version,
        title=title,
        abstract=abstract,
        venue=rng.choice(sorted(_VENUES)),
        year=rng.randint(2016, 2026),
        authors=_author_block(rng),
        references=tuple(sorted(set(references))),
        concept_tags=tuple(sorted(set(concept_tags))),
        access_keys=tuple(sorted(set(access_keys))),
    )


def _topic_documents(plan: _TopicPlan, rng: random.Random) -> list[Document]:
    """Author one topic's neighbourhood: gold by route, copies, revisions, distractors."""

    prefix = plan.topic_id.removeprefix("topic-")
    gold = tuple(plan.required_concepts)
    documents: list[Document] = []

    def add(
        slug: str,
        *,
        title: str,
        concepts: tuple[str, ...],
        keys: tuple[tuple[str, str], ...],
        references: tuple[str, ...] = (),
        content_identity: str | None = None,
        version: int = 1,
    ) -> str:
        doc_id = f"{prefix}:{slug}"
        identity = content_identity or f"work:{prefix}:{slug}"
        documents.append(
            _make_document(
                doc_id=doc_id,
                content_identity=identity,
                version=version,
                title=title,
                abstract=(
                    f"{title}. This record concerns {plan.label.lower()} and reports "
                    f"findings tagged {', '.join(sorted(set(concepts)))}."
                ),
                concept_tags=concepts,
                access_keys=keys,
                references=references,
                rng=rng,
            )
        )
        return doc_id

    lexical = ((DiscoveryRoute.LEXICAL.value, plan.lexical_key),)
    semantic = ((DiscoveryRoute.SEMANTIC.value, plan.semantic_key),)

    # Citation-only gold is authored first so the lexical seeds can point at it.
    citation_a = add("cite-a", title=f"Citation-reachable evidence A for {plan.label}", concepts=gold, keys=())
    citation_b = add("cite-b", title=f"Citation-reachable evidence B for {plan.label}", concepts=gold, keys=())

    # Lexical seeds. These are the entry points a system can reach unaided, and
    # the only way into the citation neighbourhood.
    add(
        "lex-a",
        title=f"Surface-vocabulary account of {plan.label}",
        concepts=gold,
        keys=lexical,
        references=(citation_a,),
    )
    add(
        "lex-b",
        title=f"Second surface-vocabulary account of {plan.label}",
        concepts=gold,
        keys=lexical,
        references=(citation_b,),
    )

    # Paraphrase-only gold: the semantic key shares no token with the lexical
    # key, so no amount of lexical budget reaches these.
    add("sem-a", title=f"Paraphrased treatment A of {plan.label}", concepts=gold, keys=semantic)
    add("sem-b", title=f"Paraphrased treatment B of {plan.label}", concepts=gold, keys=semantic)

    # Multi-route gold: the overlap that lets two routes be compared on content.
    add("multi-a", title=f"Cross-listed synthesis of {plan.label}", concepts=gold, keys=lexical + semantic)

    add(
        "reform-a",
        title=f"Reformulation-only study of {plan.label}",
        concepts=gold,
        keys=((DiscoveryRoute.REFORMULATION.value, plan.reformulation_key),),
    )

    # Restricted gold: reachable only through the provider that goes down.
    add(
        "restricted-a",
        title=f"Restricted-archive record for {plan.label}",
        concepts=gold,
        keys=((DiscoveryRoute.RESTRICTED.value, plan.restricted_key),),
    )

    # A republication: same work, same bytes, different locator. A system that
    # counts locators books this as a second discovery.
    add(
        "lex-a-mirror",
        title=f"Surface-vocabulary account of {plan.label}",
        concepts=gold,
        keys=lexical,
        references=(citation_a,),
        content_identity=f"work:{prefix}:lex-a",
    )

    # A revision: same work, different bytes. Rereading this after the v1 is
    # legitimate, not duplicated effort.
    add(
        "sem-a-v2",
        title=f"Paraphrased treatment A of {plan.label} (revised)",
        concepts=gold,
        keys=semantic,
        content_identity=f"work:{prefix}:sem-a",
        version=2,
    )

    # Distractors: lexically reachable, carrying only one required concept, so
    # the relevance rule excludes them. A lexical-only system pays precision.
    for index in range(4):
        add(
            f"distractor-{index}",
            title=f"Adjacent but non-qualifying note {index} on {plan.label}",
            concepts=(plan.partial_concept, rng.choice(sorted(_NOISE_CONCEPTS))),
            keys=lexical,
        )

    return documents


def _filler_documents(count: int, rng: random.Random) -> list[Document]:
    """Unrelated records. They satisfy no topic rule and are reachable by nobody's probe."""

    documents: list[Document] = []
    for index in range(count):
        concepts = tuple(sorted(rng.sample(sorted(_NOISE_CONCEPTS), 2)))
        slug = f"filler:{index:03d}"
        documents.append(
            _make_document(
                doc_id=slug,
                content_identity=f"work:{slug}",
                version=1,
                title=f"Unrelated record {index:03d}",
                abstract=f"An unrelated record concerning {', '.join(concepts)}.",
                concept_tags=concepts,
                access_keys=(),
                references=(),
                rng=rng,
            )
        )
    return documents


def build_world(seed: int, *, filler_documents: int = 60) -> DiscoveryWorld:
    """Generate the controlled index deterministically from a seed.

    Determinism is load-bearing: the committed frozen suite is only meaningful if
    a clean checkout reproduces its hash. Every collection that can reach the
    output is sorted before use, because iteration order of a `set` of strings
    varies with `PYTHONHASHSEED` across processes.
    """

    rng = random.Random(seed)
    documents: list[Document] = []
    for plan in _TOPIC_PLANS:
        documents.extend(_topic_documents(plan, rng))
    documents.extend(_filler_documents(filler_documents, rng))

    topics = tuple(
        Topic(plan.topic_id, plan.label, plan.required_concepts) for plan in _TOPIC_PLANS
    )
    return DiscoveryWorld(
        schema_version=CORPUS_SCHEMA_VERSION,
        seed=seed,
        documents=tuple(sorted(documents, key=lambda item: item.doc_id)),
        topics=tuple(sorted(topics, key=lambda item: item.topic_id)),
    )


def world_from_json(payload: dict[str, Any]) -> DiscoveryWorld:
    """Rebuild a world from its frozen JSON form."""

    documents = tuple(
        Document(
            doc_id=item["doc_id"],
            content_identity=item["content_identity"],
            content_digest=item["content_digest"],
            version=int(item["version"]),
            title=item["title"],
            abstract=item["abstract"],
            venue=item["venue"],
            year=int(item["year"]),
            authors=tuple(item["authors"]),
            references=tuple(item["references"]),
            concept_tags=tuple(item["concept_tags"]),
            access_keys=tuple((pair[0], pair[1]) for pair in item["access_keys"]),
        )
        for item in payload["documents"]
    )
    topics = tuple(
        Topic(item["topic_id"], item["label"], tuple(item["required_concepts"]))
        for item in payload["topics"]
    )
    return DiscoveryWorld(
        schema_version=payload["schema_version"],
        seed=int(payload["seed"]),
        documents=tuple(sorted(documents, key=lambda item: item.doc_id)),
        topics=tuple(sorted(topics, key=lambda item: item.topic_id)),
    )


__all__ = [
    "CORPUS_SCHEMA_VERSION",
    "DiscoveryRoute",
    "DiscoveryWorld",
    "Document",
    "ROUTE_SPECS",
    "ROUTE_SPEC_BY_ROUTE",
    "RouteSpec",
    "Topic",
    "build_world",
    "canonical_bytes",
    "is_relevant",
    "sha256_digest",
    "world_from_json",
]
