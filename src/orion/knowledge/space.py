from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum

from orion.core.evidence import normalized_content


class AuthorityAxis(str, Enum):
    """The coordinates scientific authority is held on, absorbed from RAKL.

    Authority is not one ladder. A result can be well grounded and still say
    nothing about mechanism; a model can predict without identifying. RAKL's
    Paper-1 formalism separates these, and the separation is the point:
    collapsing them to a scalar lets prediction quietly mint mechanism, which is
    the substitution the whole apparatus exists to prevent.
    """

    GROUNDING = "G"
    REPRESENTATION = "R"
    MECHANISM = "M"
    IDENTIFICATION = "I"
    DECISION = "D"


class ClaimAuthority(str, Enum):
    """How far a claim may be relied on *on one axis*.

    Presence in the space is not authority. A claim arrives as a source
    projection — this document asserts this — and rises only on independent
    corroboration or an external certificate, and only for the axis that
    certificate names.
    """

    SOURCE_PROJECTION = "SOURCE_PROJECTION"
    CORROBORATED = "CORROBORATED"
    CONTESTED = "CONTESTED"
    VERIFIED = "VERIFIED"


class RelationKind(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    REFINES = "REFINES"
    EQUIVALENT_TO = "EQUIVALENT_TO"
    DEPENDS_ON = "DEPENDS_ON"

    @property
    def symmetric(self) -> bool:
        return self in {RelationKind.EQUIVALENT_TO, RelationKind.CONTRADICTS}


def claim_id_for(text: str) -> str:
    """Content-addressed claim identity.

    Derived from normalized text, never from a caller-supplied string. An
    externally chosen id lets the same assertion enter the space twice under two
    names, which inflates corroboration counts with copies of one source — the
    identifier-space mistake this repository has already made once, in the growth
    vector.
    """

    if not text.strip():
        raise ValueError("a claim needs text")
    return "claim:" + hashlib.sha256(
        normalized_content(text).encode("utf-8")
    ).hexdigest()[:16]


@dataclass(frozen=True)
class Claim:
    """One assertion, bound to the evidence that carries it."""

    text: str
    evidence_digests: frozenset[str]
    source_ids: frozenset[str] = field(default_factory=frozenset)
    verified_axes: frozenset[AuthorityAxis] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("a claim needs text")
        if not self.evidence_digests:
            raise ValueError(
                "a claim must carry the evidence it came from; an unbound claim "
                "cannot be traced back and cannot be re-checked"
            )

    @property
    def claim_id(self) -> str:
        return claim_id_for(self.text)

    @property
    def independent_support(self) -> int:
        """Distinct sources asserting it. Copies of one source count once."""

        return len(self.source_ids)


@dataclass(frozen=True)
class Relation:
    """A typed edge, itself evidence-bound."""

    subject: str
    object: str
    kind: RelationKind
    evidence_digests: frozenset[str]

    def __post_init__(self) -> None:
        if self.subject == self.object:
            raise ValueError("a claim cannot relate to itself")
        if not self.evidence_digests:
            raise ValueError("a relation must cite the evidence that establishes it")


@dataclass(frozen=True)
class TraversalResult:
    """What the space offers toward a question, and what it cannot settle."""

    query: str
    reached: tuple[Claim, ...]
    supporting: tuple[Claim, ...]
    contested: tuple[tuple[Claim, Claim], ...]
    unreached_terms: tuple[str, ...]

    @property
    def settles(self) -> bool:
        """A question is settled only if something supports it and nothing
        contradicts it. An unresolved contradiction is not a weak answer — it is
        the absence of one, and reporting the majority side would discard the
        very disagreement worth knowing about."""

        return bool(self.supporting) and not self.contested


class KnowledgeSpace:
    """The structured store ORION traverses, rather than a pile of documents.

    Claims are content-addressed, so one assertion is one node however many
    documents carry it, and corroboration is counted over distinct *sources*
    rather than repetitions. Edges are typed and evidence-bound: a contradiction
    is retained as a contradiction rather than resolved by majority, because a
    space that silently drops the losing side of a disagreement is more
    confident and less informative than the literature it came from.
    """

    def __init__(self) -> None:
        self._claims: dict[str, Claim] = {}
        self._relations: set[Relation] = set()

    def __len__(self) -> int:
        return len(self._claims)

    @property
    def claims(self) -> tuple[Claim, ...]:
        return tuple(self._claims[key] for key in sorted(self._claims))

    @property
    def relations(self) -> tuple[Relation, ...]:
        return tuple(sorted(self._relations, key=lambda item: (item.subject, item.object, item.kind.value)))

    def add_claim(self, claim: Claim) -> Claim:
        """Add or merge a claim, accumulating evidence and sources.

        Merging is by content identity only. Two assertions that mean the same
        thing in different words remain separate nodes: deciding they are the
        same requires a model, and a false merge silently destroys a claim with
        a clean receipt, which is the worse error direction.
        """

        key = claim.claim_id
        existing = self._claims.get(key)
        if existing is None:
            self._claims[key] = claim
            return claim
        merged = Claim(
            text=existing.text,
            evidence_digests=existing.evidence_digests | claim.evidence_digests,
            source_ids=existing.source_ids | claim.source_ids,
            # Axis authority is not accumulated by re-assertion: a second source
            # repeating a claim adds corroboration, never a certificate.
            verified_axes=existing.verified_axes,
        )
        self._claims[key] = merged
        return merged

    def add_relation(self, relation: Relation) -> None:
        if relation.subject not in self._claims or relation.object not in self._claims:
            raise KeyError("both endpoints must be in the space before relating them")
        self._relations.add(relation)
        if relation.kind.symmetric:
            self._relations.add(
                Relation(
                    subject=relation.object,
                    object=relation.subject,
                    kind=relation.kind,
                    evidence_digests=relation.evidence_digests,
                )
            )

    def neighbours(self, claim_id: str, kind: RelationKind | None = None) -> tuple[Claim, ...]:
        return tuple(
            self._claims[item.object]
            for item in self.relations
            if item.subject == claim_id and (kind is None or item.kind is kind)
        )

    def resolve_authority(
        self, claim_id: str, axis: AuthorityAxis = AuthorityAxis.GROUNDING
    ) -> ClaimAuthority:
        """Derive authority on one axis, from the space rather than a declaration.

        A claim contradicted by anything is CONTESTED regardless of how much
        supports it, because a contradiction is a reason to look again, not a
        vote to be outweighed. Authority earned on one axis does not transfer:
        corroborated GROUNDING says nothing about MECHANISM, so an axis with no
        certificate stays a source projection however well supported the claim
        is elsewhere.
        """

        claim = self._claims[claim_id]
        if axis in claim.verified_axes:
            return ClaimAuthority.VERIFIED
        if self.neighbours(claim_id, RelationKind.CONTRADICTS):
            return ClaimAuthority.CONTESTED
        if claim.independent_support >= 2:
            return ClaimAuthority.CORROBORATED
        return ClaimAuthority.SOURCE_PROJECTION

    def traverse(self, query: str, *, depth: int = 2) -> TraversalResult:
        """Walk the space for claims bearing on a question.

        Lexical seeding then typed expansion. The seeding is deliberately
        mechanical: an embedding or model-driven entry point would put the
        weakest-calibrated component at the front of the path, where its errors
        would silently determine what the traversal can ever reach.
        """

        terms = {item for item in normalized_content(query).lower().split() if len(item) > 3}
        seeds = [
            claim
            for claim in self.claims
            if terms & set(normalized_content(claim.text).lower().split())
        ]
        reached: dict[str, Claim] = {item.claim_id: item for item in seeds}
        frontier = list(reached)
        for _ in range(max(depth - 1, 0)):
            nxt: list[str] = []
            for claim_id in frontier:
                for neighbour in self.neighbours(claim_id):
                    if neighbour.claim_id not in reached:
                        reached[neighbour.claim_id] = neighbour
                        nxt.append(neighbour.claim_id)
            frontier = nxt

        contested: list[tuple[Claim, Claim]] = []
        seen_pairs: set[frozenset[str]] = set()
        for claim_id in reached:
            for other in self.neighbours(claim_id, RelationKind.CONTRADICTS):
                pair = frozenset({claim_id, other.claim_id})
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    contested.append((reached[claim_id], other))

        supporting = tuple(
            item
            for item in reached.values()
            if self.resolve_authority(item.claim_id)
            in {ClaimAuthority.CORROBORATED, ClaimAuthority.VERIFIED}
        )
        matched = {
            term
            for term in terms
            for claim in reached.values()
            if term in normalized_content(claim.text).lower()
        }
        return TraversalResult(
            query=query,
            reached=tuple(reached[key] for key in sorted(reached)),
            supporting=supporting,
            contested=tuple(contested),
            unreached_terms=tuple(sorted(terms - matched)),
        )


def build_space(
    claims: Iterable[Claim], relations: Sequence[Relation] = ()
) -> KnowledgeSpace:
    space = KnowledgeSpace()
    for claim in claims:
        space.add_claim(claim)
    for relation in relations:
        space.add_relation(relation)
    return space
