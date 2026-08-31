"""Domain-agnostic typed authority calculus (powerset-license least fixed point).

Implements the operator of MANUSCRIPT_V2.md section 3 verbatim:

    F_R(x)_q = {}                                            if q in R
    F_R(x)_q = sigma(q) | union_{r: head(r)=q} tau_r(x|body)  otherwise
    tau_r((l_a)_{a in A}) = cap_r & intersection_{a in A} l_a

`Auth(R) = lfp(F_R)` on the finite powerset lattice (2^Lambda)^Q.

The mathematics here is donor-owned (least fixed points, truth maintenance,
positive Datalog, semiring/annotated provenance). See README "Scope and
non-claims". This module contains no domain constants and no ORION paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Tuple

FLAT_TOKEN = "*"


class InstanceError(ValueError):
    """Raised when an instance is not well formed."""


@dataclass(frozen=True)
class Rule:
    """A positive conjunctive rule `body -> head` with license cap `cap`."""

    id: str
    body: Tuple[str, ...]
    head: str
    cap: FrozenSet[str]


@dataclass(frozen=True)
class Instance:
    """A typed merge problem instance.

    licenses: the finite license universe Lambda.
    claims:   the finite claim set Q.
    seeds:    sigma, the independent seed label of each claim.
    rules:    positive conjunctive rules, each with an explicit cap.
    refuted:  R, the directly refuted claims (label forced to bottom).
    """

    licenses: FrozenSet[str]
    claims: FrozenSet[str]
    seeds: Mapping[str, FrozenSet[str]]
    rules: Tuple[Rule, ...]
    refuted: FrozenSet[str] = field(default_factory=frozenset)

    def validate(self) -> "Instance":
        for claim, label in self.seeds.items():
            if claim not in self.claims:
                raise InstanceError(f"seed for unknown claim {claim!r}")
            unknown = set(label) - set(self.licenses)
            if unknown:
                raise InstanceError(f"seed {claim!r} uses unknown licenses {sorted(unknown)}")
        seen = set()
        for rule in self.rules:
            if rule.id in seen:
                raise InstanceError(f"duplicate rule id {rule.id!r}")
            seen.add(rule.id)
            if rule.head not in self.claims:
                raise InstanceError(f"rule {rule.id!r} has unknown head {rule.head!r}")
            if not rule.body:
                raise InstanceError(
                    f"rule {rule.id!r} has an empty body; zero-antecedent rules are seeds"
                )
            for atom in rule.body:
                if atom not in self.claims:
                    raise InstanceError(f"rule {rule.id!r} has unknown body claim {atom!r}")
            unknown = set(rule.cap) - set(self.licenses)
            if unknown:
                raise InstanceError(f"rule {rule.id!r} caps unknown licenses {sorted(unknown)}")
        unknown = set(self.refuted) - set(self.claims)
        if unknown:
            raise InstanceError(f"refuted set names unknown claims {sorted(unknown)}")
        return self

    def seed_of(self, claim: str) -> FrozenSet[str]:
        return self.seeds.get(claim, frozenset())

    @property
    def pair_bound(self) -> int:
        """Theorem 1 bound: at most |Q|*|Lambda| strict claim-license additions."""
        return len(self.claims) * len(self.licenses)


@dataclass(frozen=True)
class Evaluation:
    """Result of evaluating an instance."""

    labels: Mapping[str, FrozenSet[str]]
    rank: Mapping[Tuple[str, str], int]
    rounds: int

    def label(self, claim: str) -> FrozenSet[str]:
        return self.labels.get(claim, frozenset())

    def is_authorized(self, claim: str) -> bool:
        return bool(self.label(claim))

    @property
    def authorized(self) -> FrozenSet[str]:
        return frozenset(c for c, l in self.labels.items() if l)

    @property
    def pairs(self) -> FrozenSet[Tuple[str, str]]:
        return frozenset((c, lic) for c, label in self.labels.items() for lic in label)


def transfer(rule: Rule, labels: Mapping[str, FrozenSet[str]]) -> FrozenSet[str]:
    """tau_r = cap_r & intersection of the body labels."""
    result = set(rule.cap)
    for atom in rule.body:
        result &= labels.get(atom, frozenset())
        if not result:
            return frozenset()
    return frozenset(result)


def least_fixed_point(instance: Instance) -> Evaluation:
    """Iterate F_R from bottom to its least fixed point.

    Terminates by Theorem 1: labels only grow, and there are at most
    |Q|*|Lambda| claim-license pairs, so the iteration count is bounded by
    |Q|*|Lambda| + 1. The bound is asserted rather than used as a cutoff, so a
    violation surfaces as a defect instead of a silently truncated result.
    """
    instance.validate()
    labels: Dict[str, FrozenSet[str]] = {c: frozenset() for c in instance.claims}
    rank: Dict[Tuple[str, str], int] = {}
    by_head: Dict[str, List[Rule]] = {}
    for rule in instance.rules:
        by_head.setdefault(rule.head, []).append(rule)

    rounds = 0
    limit = instance.pair_bound + 1
    while True:
        rounds += 1
        if rounds > limit:  # pragma: no cover - unreachable given monotonicity
            raise InstanceError(
                f"iteration exceeded the Theorem 1 bound of {limit} rounds"
            )
        changed = False
        nxt: Dict[str, FrozenSet[str]] = {}
        for claim in instance.claims:
            if claim in instance.refuted:
                nxt[claim] = frozenset()
                continue
            value = set(instance.seed_of(claim))
            for rule in by_head.get(claim, ()):
                value |= transfer(rule, labels)
            new = frozenset(value)
            if new != labels[claim]:
                changed = True
                for lic in new - labels[claim]:
                    rank[(claim, lic)] = rounds
            nxt[claim] = new
        labels = nxt
        if not changed:
            return Evaluation(labels=labels, rank=rank, rounds=rounds)


def flat_projection(instance: Instance) -> Instance:
    """License-erased projection: collapse Lambda to a single token.

    This is not a second algorithm. It is the same operator over the one-element
    license universe, which is exactly the untyped/boolean reading of the record:
    a claim is flat-authorized when it is derivable at all, with no record of
    which authority carried the derivation.
    """
    seeds = {
        claim: frozenset({FLAT_TOKEN}) if instance.seed_of(claim) else frozenset()
        for claim in instance.claims
    }
    rules = tuple(
        Rule(id=r.id, body=r.body, head=r.head, cap=frozenset({FLAT_TOKEN}))
        for r in instance.rules
    )
    return Instance(
        licenses=frozenset({FLAT_TOKEN}),
        claims=instance.claims,
        seeds=seeds,
        rules=rules,
        refuted=instance.refuted,
    )


def retraction(
    instance: Instance, refuted: Iterable[str]
) -> Tuple[Evaluation, Evaluation, FrozenSet[Tuple[str, str]]]:
    """Theorem 5: Ret(R) = A_pre \\ A_post as claim-license pairs.

    `instance` supplies the pre-falsifier system; `refuted` is the post-falsifier
    refutation set, which is unioned with any refutations already declared.
    """
    post_refuted = frozenset(instance.refuted) | frozenset(refuted)
    pre = least_fixed_point(instance)
    post = least_fixed_point(
        Instance(
            licenses=instance.licenses,
            claims=instance.claims,
            seeds=instance.seeds,
            rules=instance.rules,
            refuted=post_refuted,
        )
    )
    return pre, post, frozenset(pre.pairs - post.pairs)


def proof_tree(
    instance: Instance, evaluation: Evaluation, claim: str, license: str
) -> Optional[dict]:
    """Extract a finite untainted proof tree for `(claim, license)`.

    Theorem 2: a license belongs to the fixed-point label exactly when such a
    tree exists. Well-foundedness is guaranteed by descending strictly in the
    iteration rank at which each pair first appeared, so cyclic rule sets cannot
    produce an infinite tree.
    """
    if license not in evaluation.label(claim):
        return None
    if claim in instance.refuted:  # pragma: no cover - refuted labels are empty
        return None
    if license in instance.seed_of(claim):
        return {"claim": claim, "license": license, "kind": "seed"}
    here = evaluation.rank[(claim, license)]
    for rule in instance.rules:
        if rule.head != claim or license not in rule.cap:
            continue
        if any(
            license not in evaluation.label(a)
            or evaluation.rank[(a, license)] >= here
            for a in rule.body
        ):
            continue
        return {
            "claim": claim,
            "license": license,
            "kind": "rule",
            "rule": rule.id,
            "premises": [proof_tree(instance, evaluation, a, license) for a in rule.body],
        }
    return None  # pragma: no cover - unreachable when the label is well founded
