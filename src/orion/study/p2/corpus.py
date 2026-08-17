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
import re
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

    @property
    def by_id(self) -> dict[str, Document]:
        return {item.doc_id: item for item in self.documents}

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

        if route is DiscoveryRoute.CITATION:
            reachable = set(self.citation_reachable(probe))
            return tuple(
                sorted(
                    (item for item in self.documents if item.doc_id in reachable),
                    key=lambda item: item.doc_id,
                )
            )
        return tuple(
            sorted(
                (item for item in self.documents if probe in item.keys_for(route)),
                key=lambda item: item.doc_id,
            )
        )

    def probes_for(self, route: DiscoveryRoute) -> tuple[str, ...]:
        """Every probe that route accepts. Used to build public route vocabularies."""

        if route is DiscoveryRoute.CITATION:
            return tuple(
                sorted({item.doc_id for item in self.documents if item.references})
            )
        keys: set[str] = set()
        for document in self.documents:
            keys.update(document.keys_for(route))
        return tuple(sorted(keys))

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


#: Topics in the frozen world. Five case families per topic, so 78 topics is 390
#: tasks — at or above the 385 `STATISTICAL_PLAN_V1.json` committed this family to
#: for its TIER_B_committed proportion half-width of 0.05 at assumed_p 0.5. The
#: count is set by that pre-registered power commitment, not by any observed
#: outcome: the plan was frozen outcome-blind and the world moves to meet it.
TOPIC_COUNT = 78


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


_AUTHORED_TOPIC_PLANS: tuple[_TopicPlan, ...] = (
    _TopicPlan(
        "topic-measurement-invariance",
        "Measurement invariance of latent trait instruments",
        ("latent_trait", "measurement_invariance"),
        "measurement invariance latent trait",
        "scalar equivalence across respondent groups",
        "differential item functioning",
        "restricted archive: psychometric invariance",
        "latent_trait",
    ),
    _TopicPlan(
        "topic-capture-recapture",
        "Capture-recapture coverage estimation for literature search",
        ("capture_recapture", "coverage_estimation"),
        "capture recapture coverage estimation",
        "mark release resight abundance inference",
        "unseen species richness estimator",
        "restricted archive: population size estimation",
        "coverage_estimation",
    ),
    _TopicPlan(
        "topic-sequential-stopping",
        "Sequential stopping rules in screening workflows",
        ("sequential_stopping", "screening_recall"),
        "sequential stopping screening recall",
        "when to halt reviewing candidate records",
        "sample size re-estimation for reviews",
        "restricted archive: stopping criteria",
        "screening_recall",
    ),
    _TopicPlan(
        "topic-query-diversification",
        "Query diversification across federated search backends",
        ("query_diversification", "federated_search"),
        "query diversification federated search",
        "spreading probes over heterogeneous providers",
        "result set novelty maximization",
        "restricted archive: distributed retrieval",
        "federated_search",
    ),
)


# --------------------------------------------------------------------------
# Coined vocabulary for the generated topics
#
# The four topics above are authored, and stay exactly as they were. Reaching the
# committed N needs 74 more, and hand-authoring 74 topics whose vocabularies stay
# pairwise disjoint is exactly the kind of thing a human does wrong once and never
# notices. So the rest are coined from syllable banks by an injective function,
# which makes the disjointness invariants hold *by construction* instead of by a
# collision check bolted on afterwards.
#
# Three invariants are load-bearing, and `validate_topic_plans` enforces all three
# at import time:
#
# 1. A topic's semantic key shares no token with its lexical key. This is what
#    makes paraphrase-only gold genuinely unreachable by lexical budget — the
#    single structural fact the whole reachability story rests on.
# 2. No access key is shared between topics. Route lookup is exact-key set
#    membership, so a shared key would silently hand one topic's documents to
#    another topic's probe.
# 3. Concept tokens are globally unique per topic, so the relevance rule cannot
#    leak across topics and every gold set stays the topic's own.
#
# A fourth invariant belongs to the *systems* layer but is enforced here because
# only here can it be guaranteed: any two topic labels share at most one
# non-generic token. `offline_systems._on_topic` screens a record by demanding two
# shared tokens between the question and the record text, and a record's text
# embeds its topic label. Two labels sharing two tokens would make one topic's
# records screen as on-topic for another topic's question, quietly inflating
# claims and destroying precision. Combinatorial label generation — reusing a stem
# across several topics — is precisely how that breaks, so labels are built only
# from tokens unique to their own topic.
# --------------------------------------------------------------------------

_ONSETS = (
    "bar", "cel", "dor", "fen", "gil", "hos",
    "kav", "lum", "mir", "nod", "pel", "quor",
)
_MIDS = ("a", "e", "i", "o", "u", "ae", "ia", "ou")
_TAILS = ("dine", "kar", "lith", "mos", "nex", "phor", "sil", "tane")

#: Coined tokens allocated per generated topic. Nine rather than eight because one
#: generated topic in four needs a ninth token for a restricted key that shares
#: nothing with its label — see `_RESTRICTED_OPAQUE_EVERY`.
_TOKENS_PER_TOPIC = 9

#: One generated topic in this many gets a restricted key with no label token in it.
#:
#: This mirrors the authored composition rather than inventing one. Three of the four
#: authored topics share a label word with their restricted key — "invariance",
#: "estimation", "stopping" — so the correct restricted probe outranks the decoys.
#: The fourth, query diversification, shares nothing, and its correct probe ranks
#: third. That is not a detail: the restricted route is the one taken away in the
#: `UNAVAILABLE_ROUTE` family, and the single task the superseded suite reported as
#: `CANNOT_CHECK` was that same topic's unavailable-route task. A generator that made
#: every restricted probe rank first would erase the harder quarter of the
#: distribution and with it the censored-evidence case the family exists to measure.
_RESTRICTED_OPAQUE_EVERY = 4

#: Seed for the token pool shuffle. Fixed, so the pool is part of what the frozen
#: seed determines.
_TOKEN_POOL_SEED = 20260816

#: Length of the leading character run that identifies a syllable bank entry. Three,
#: because every onset is three characters except `quor`, whose first three are
#: shared with nothing else — so a three-character prefix names the onset exactly.
_ONSET_LEN = 3


def _topic_token_blocks(count: int) -> tuple[tuple[str, ...], ...]:
    """Allocate each generated topic eight tokens with eight distinct onsets.

    Both halves of this matter, and each cost a failed attempt to understand.

    *Why shuffled.* `_coined` is a mixed-radix encoding, so any arithmetic rule
    relating a topic's tokens leaves a shared spelling signature. Contiguous indices
    share an onset and differ only in the final syllable. A stride of 96 fixes the
    onset but, being a multiple of eight, leaves every token of a topic ending in
    the same syllable. A stride of 97 fixes both and still leaves the middle
    syllable alternating with period two, so a topic's whole vocabulary draws on the
    same two vowels while other topics draw on others.

    *Why that leaks.* A system orders public probes by a Jaccard term plus a
    character-similarity term, and the paraphrase-only routes are built to score
    exactly zero on the Jaccard term — being unreachable by surface vocabulary is
    what they are *for*. Any spelling regularity shared between a topic's label and
    its semantic key therefore decides the ordering through the second term, and a
    probe that was supposed to require blind trial allocation instead ranks first.
    Measured against the superseded world, the arithmetic layouts put the correct
    semantic probe first for 71 of 74 generated topics where the authored topics
    spread uniformly across all four ranks.

    *Why distinct onsets rather than a bare shuffle.* A shuffle alone destroys the
    systematic signature but, with twelve onsets and eight tokens per topic,
    collides incidentally most of the time. Requiring the eight onsets to differ
    makes the no-shared-spelling invariant hold by construction, so
    `validate_generated_vocabulary` becomes a check on the allocator rather than a
    filter the allocator has to get lucky to pass.

    Deterministic throughout: the pool is sorted before a fixed-seed shuffle, and
    the allocation is a left-to-right scan, so nothing here varies with
    `PYTHONHASHSEED`. Tokens passed over by one topic stay available to the next.
    """

    pool = sorted(_coined(index) for index in range(_COINED_SPAN))
    random.Random(_TOKEN_POOL_SEED).shuffle(pool)

    remaining = pool
    blocks: list[tuple[str, ...]] = []
    for position in range(count):
        chosen: list[str] = []
        onsets: set[str] = set()
        leftover: list[str] = []
        for token in remaining:
            onset = token[:_ONSET_LEN]
            if len(chosen) < _TOKENS_PER_TOPIC and onset not in onsets:
                onsets.add(onset)
                chosen.append(token)
            else:
                leftover.append(token)
        if len(chosen) < _TOKENS_PER_TOPIC:
            raise ValueError(
                f"token pool exhausted allocating topic {position}: needed "
                f"{_TOKENS_PER_TOPIC} distinct-onset tokens, found {len(chosen)}; "
                "widen the syllable banks before raising TOPIC_COUNT"
            )
        blocks.append(tuple(chosen))
        remaining = leftover
    return tuple(blocks)

_COINED_SPAN = len(_ONSETS) * len(_MIDS) * len(_TAILS)


def _coined(index: int) -> str:
    """Injective index -> token map: distinct indices give distinct strings.

    A mixed-radix decomposition, and the concatenation stays injective because
    every onset is three characters, every mid is vowels only and every tail
    starts with a consonant — so a token's split point is recoverable and two
    different triples cannot spell the same word.
    """

    if not 0 <= index < _COINED_SPAN:
        raise ValueError(
            f"coined-token index {index} outside the injective range 0..{_COINED_SPAN - 1}"
        )
    onset = _ONSETS[index // (len(_MIDS) * len(_TAILS))]
    mid = _MIDS[(index // len(_TAILS)) % len(_MIDS)]
    tail = _TAILS[index % len(_TAILS)]
    return f"{onset}{mid}{tail}"


_TOKEN_BLOCKS: tuple[tuple[str, ...], ...] = _topic_token_blocks(
    TOPIC_COUNT - len(_AUTHORED_TOPIC_PLANS)
)


def _generated_topic_plan(index: int) -> _TopicPlan:
    """Coin one topic. Route keys mirror the authored topics' score structure.

    The mirroring is deliberate and it is the difference between scaling N and
    changing the measurement. A system orders public probes by lexical similarity
    to the question, so how much each route's correct key resembles the label
    decides how many route calls that route costs — and the route-call budget
    binds. The authored topics set the pattern: the lexical key is a subset of the
    label, the restricted key shares one label token, and the semantic and
    reformulation keys share none. Generated topics reproduce that exactly, so
    per-task difficulty is unchanged and a rate that moves after this scale-up
    moves for a reason other than the generator.
    """

    t0, t1, t2, t3, t4, t5, t6, t7, t8 = _TOKEN_BLOCKS[index]
    # Three topics in four put a label token in the restricted key, so the correct
    # restricted probe outranks the decoys; the fourth uses a token found nowhere in
    # the label, so it does not.
    restricted_tail = t8 if index % _RESTRICTED_OPAQUE_EVERY == _RESTRICTED_OPAQUE_EVERY - 1 else t3
    return _TopicPlan(
        topic_id=f"topic-{t0}-{t1}",
        # "of" is in the systems layer's generic-word stoplist, so the label's
        # screening tokens are exactly the four coined ones.
        label=f"{t0.capitalize()} {t1} of {t2} {t3}",
        required_concepts=(f"{t0}_axis", f"{t1}_regime"),
        lexical_key=f"{t0} {t1} {t2}",
        # Shares no token with the lexical key or the label: paraphrase-only.
        semantic_key=f"{t4} {t5}",
        reformulation_key=f"{t6} restatement",
        restricted_key=f"restricted archive: {t7} {restricted_tail}",
        partial_concept=f"{t0}_axis",
    )


_GENERIC_LABEL_WORDS = frozenset({"of", "the", "a", "and", "for", "in", "on", "across", "to"})


def _label_tokens(label: str) -> frozenset[str]:
    words = re.findall(r"[a-z0-9]+", label.lower())
    return frozenset(words) - _GENERIC_LABEL_WORDS


def _key_tokens(key: str) -> frozenset[str]:
    return frozenset(re.findall(r"[a-z0-9]+", key.lower()))


def validate_topic_plans(plans: tuple[_TopicPlan, ...]) -> tuple[str, ...]:
    """Return every violated world invariant. Empty means the plan set is sound.

    Returned rather than raised so a test can drive this with deliberately broken
    input and see the specific complaint, instead of only ever observing that a
    good plan set does not explode.
    """

    problems: list[str] = []

    topic_ids = [plan.topic_id for plan in plans]
    duplicate_ids = sorted({item for item in topic_ids if topic_ids.count(item) > 1})
    if duplicate_ids:
        problems.append(f"duplicate topic ids: {duplicate_ids}")

    # 1. lexical/semantic token disjointness, per topic.
    for plan in plans:
        shared = sorted(_key_tokens(plan.lexical_key) & _key_tokens(plan.semantic_key))
        if shared:
            problems.append(
                f"{plan.topic_id}: semantic key shares {shared} with its lexical key"
            )

    # 2. No access key shared between topics, on any route.
    for field in ("lexical_key", "semantic_key", "reformulation_key", "restricted_key"):
        owners: dict[str, list[str]] = {}
        for plan in plans:
            owners.setdefault(getattr(plan, field), []).append(plan.topic_id)
        for key, holders in sorted(owners.items()):
            if len(holders) > 1:
                problems.append(f"{field} {key!r} shared by topics {sorted(holders)}")

    # 3. Concept tokens globally unique to one topic.
    concept_owners: dict[str, list[str]] = {}
    for plan in plans:
        for concept in plan.required_concepts:
            concept_owners.setdefault(concept, []).append(plan.topic_id)
    for concept, holders in sorted(concept_owners.items()):
        if len(holders) > 1:
            problems.append(f"concept {concept!r} claimed by topics {sorted(holders)}")
    for plan in plans:
        if plan.partial_concept not in plan.required_concepts:
            problems.append(
                f"{plan.topic_id}: partial concept {plan.partial_concept!r} is not a required concept"
            )

    # 4. Labels pairwise share at most one non-generic token.
    tokens_by_topic = [(plan.topic_id, _label_tokens(plan.label)) for plan in plans]
    for outer in range(len(tokens_by_topic)):
        left_id, left = tokens_by_topic[outer]
        for inner in range(outer + 1, len(tokens_by_topic)):
            right_id, right = tokens_by_topic[inner]
            shared = sorted(left & right)
            if len(shared) > 1:
                problems.append(
                    f"labels of {left_id} and {right_id} share {shared}; "
                    "two shared tokens let one topic's records screen as on-topic for the other"
                )

    return tuple(problems)


def validate_generated_vocabulary(plans: tuple[_TopicPlan, ...]) -> tuple[str, ...]:
    """Check that the generator manufactures no character-level shortcut.

    Scoped to generated topics on purpose. The four authored topics are hand-written
    natural language and one of them does share an onset between its label and its
    reformulation key ("estimation"/"estimator"); that is a property of the world the
    superseded suite already measured, and flagging it here would be a false alarm
    about prose this function has no business policing. What this checks is narrower
    and is the thing that can silently go wrong at scale: that a *generated* topic's
    paraphrase-only route keys are not spelled from the same syllables as its label,
    because a system that cannot match them on tokens could otherwise still match
    them on characters.
    """

    problems: list[str] = []
    for plan in plans:
        label_prefixes = {
            token[:_ONSET_LEN] for token in _label_tokens(plan.label)
        }
        for field in ("semantic_key", "reformulation_key"):
            for token in sorted(_key_tokens(getattr(plan, field))):
                if token[:_ONSET_LEN] in label_prefixes:
                    problems.append(
                        f"{plan.topic_id}: {field} token {token!r} shares the opening "
                        f"{_ONSET_LEN} characters with a label token; a "
                        "character-similarity score would rank this probe without "
                        "sharing a single word with the question"
                    )
    return tuple(problems)


def _topic_plans() -> tuple[_TopicPlan, ...]:
    generated = tuple(
        _generated_topic_plan(index)
        for index in range(TOPIC_COUNT - len(_AUTHORED_TOPIC_PLANS))
    )
    ordered = _AUTHORED_TOPIC_PLANS + generated
    problems = validate_topic_plans(ordered) + validate_generated_vocabulary(generated)
    if problems:  # pragma: no cover - a broken generator must not produce a world
        raise ValueError(
            "topic plan invariants violated:\n  " + "\n  ".join(problems)
        )
    return ordered


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


def build_world(seed: int, *, filler_documents: int = 40) -> DiscoveryWorld:
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
    "TOPIC_COUNT",
    "Topic",
    "build_world",
    "canonical_bytes",
    "is_relevant",
    "sha256_digest",
    "validate_generated_vocabulary",
    "validate_topic_plans",
    "world_from_json",
]
