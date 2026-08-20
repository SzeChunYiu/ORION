"""Exact RSSI pilot benchmark.

Research-only deterministic generator/scorer. Candidate policies receive only public
cases. Protected gold is held separately by the scorer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import random
from typing import Callable, Iterable


class Standing(str, Enum):
    SUPPORTED = "SUPPORTED"
    VERIFIED = "VERIFIED"
    AUTHORIZED = "AUTHORIZED"
    REOPENED = "REOPENED"
    INVALIDATED = "INVALIDATED"
    UNKNOWN = "UNKNOWN"


class Disposition(str, Enum):
    PRESERVE = "PRESERVE"
    TRANSPORT = "TRANSPORT"
    REOPEN = "REOPEN"
    INVALIDATE = "INVALIDATE"
    LEAVE_UNKNOWN = "LEAVE_UNKNOWN"


@dataclass(frozen=True)
class PublicObject:
    object_id: str
    object_kind: str
    standing: Standing
    semantic_view_id: str
    evidence_ids: tuple[str, ...] = ()
    authority_receipt_ids: tuple[str, ...] = ()
    failure_cause: str = ""

    def payload(self) -> dict:
        return {
            "object_id": self.object_id,
            "object_kind": self.object_kind,
            "standing": self.standing.value,
            "semantic_view_id": self.semantic_view_id,
            "evidence_ids": list(self.evidence_ids),
            "authority_receipt_ids": list(self.authority_receipt_ids),
            "failure_cause": self.failure_cause,
        }


@dataclass(frozen=True)
class PublicDelta:
    from_framework: str
    to_framework: str
    semantic_relations: tuple[tuple[str, str, str], ...] = ()
    semantic_transport_witnesses: tuple[tuple[str, str, str], ...] = ()
    added_operators: tuple[str, ...] = ()
    stale_authority_receipts: tuple[str, ...] = ()
    fresh_authority_object_ids: tuple[str, ...] = ()

    def payload(self) -> dict:
        return {
            "from_framework": self.from_framework,
            "to_framework": self.to_framework,
            "semantic_relations": [list(x) for x in self.semantic_relations],
            "semantic_transport_witnesses": [list(x) for x in self.semantic_transport_witnesses],
            "added_operators": list(self.added_operators),
            "stale_authority_receipts": list(self.stale_authority_receipts),
            "fresh_authority_object_ids": list(self.fresh_authority_object_ids),
        }


@dataclass(frozen=True)
class PublicCase:
    case_id: str
    family_id: str
    task_answer: str
    objects: tuple[PublicObject, ...]
    delta: PublicDelta

    def payload(self) -> dict:
        # family_id is intentionally excluded from candidate-visible payload.
        return {
            "case_id": self.case_id,
            "task_answer": self.task_answer,
            "objects": [x.payload() for x in self.objects],
            "delta": self.delta.payload(),
        }


@dataclass(frozen=True)
class Migration:
    object_id: str
    from_standing: Standing
    to_standing: Standing
    disposition: Disposition

    def payload(self) -> dict:
        return {
            "object_id": self.object_id,
            "from_standing": self.from_standing.value,
            "to_standing": self.to_standing.value,
            "disposition": self.disposition.value,
        }


@dataclass(frozen=True)
class ProtectedGold:
    case_id: str
    correct_task_answer: str
    affected_object_ids: tuple[str, ...]
    migrations: tuple[Migration, ...]

    def payload(self) -> dict:
        return {
            "case_id": self.case_id,
            "correct_task_answer": self.correct_task_answer,
            "affected_object_ids": list(self.affected_object_ids),
            "migrations": [x.payload() for x in self.migrations],
        }


@dataclass(frozen=True)
class PilotCase:
    public: PublicCase
    gold: ProtectedGold


@dataclass(frozen=True)
class PolicyOutput:
    task_answer: str
    migrations: tuple[Migration, ...]
    protected_surface_violation: bool = False

    def payload(self) -> dict:
        return {
            "task_answer": self.task_answer,
            "migrations": [x.payload() for x in self.migrations],
            "protected_surface_violation": self.protected_surface_violation,
        }


@dataclass(frozen=True)
class Score:
    task_correct: bool
    migration_exact: bool
    all_affected_objects_accounted_for: bool
    invalid_promotion_count: int
    protected_surface_violation_count: int

    @property
    def all_gates_pass(self) -> bool:
        return (
            self.task_correct
            and self.migration_exact
            and self.all_affected_objects_accounted_for
            and self.invalid_promotion_count == 0
            and self.protected_surface_violation_count == 0
        )

    def payload(self) -> dict:
        return {
            "task_correct": self.task_correct,
            "migration_exact": self.migration_exact,
            "all_affected_objects_accounted_for": self.all_affected_objects_accounted_for,
            "invalid_promotion_count": self.invalid_promotion_count,
            "protected_surface_violation_count": self.protected_surface_violation_count,
            "all_gates_pass": self.all_gates_pass,
        }


def _opaque(seed: int, tag: str) -> str:
    return hashlib.sha256(f"{seed}:{tag}".encode()).hexdigest()[:16]


def _case_id(seed: int, family: str, index: int) -> str:
    return f"rssi-{_opaque(seed, family + ':' + str(index))}"


def _stale_certificate(seed: int, index: int) -> PilotCase:
    cid = _case_id(seed, "semantic", index)
    obj = f"obj-{_opaque(seed + index, 'object')}"
    receipt = f"rec-{_opaque(seed + index, 'receipt')}"
    s0, s1 = f"sv-{_opaque(seed, 's0')}", f"sv-{_opaque(seed, 's1')}"
    public = PublicCase(
        case_id=cid,
        family_id="semantic_stale_certificate",
        task_answer="A",
        objects=(PublicObject(obj, "CLAIM", Standing.AUTHORIZED, s0, ("e1",), (receipt,)),),
        delta=PublicDelta(
            from_framework="F0",
            to_framework="F1",
            semantic_relations=((s0, s1, "LOAD_BEARING_DIFFERENCE"),),
        ),
    )
    migration = Migration(obj, Standing.AUTHORIZED, Standing.REOPENED, Disposition.REOPEN)
    return PilotCase(public, ProtectedGold(cid, "A", (obj,), (migration,)))


def _operator_reopens_negative(seed: int, index: int) -> PilotCase:
    cid = _case_id(seed, "negative", index)
    neg = f"neg-{_opaque(seed + index, 'negative')}"
    op = f"op-{_opaque(seed + index, 'operator')}"
    public = PublicCase(
        case_id=cid,
        family_id="operator_reopens_negative",
        task_answer="B",
        objects=(
            PublicObject(
                neg,
                "NEGATIVE_KNOWLEDGE",
                Standing.VERIFIED,
                "failure-context-v0",
                ("e-failure",),
                (),
                f"MISSING_OPERATOR:{op}",
            ),
        ),
        delta=PublicDelta("F0", "F1", added_operators=(op,)),
    )
    migration = Migration(neg, Standing.VERIFIED, Standing.REOPENED, Disposition.REOPEN)
    return PilotCase(public, ProtectedGold(cid, "B", (neg,), (migration,)))


def _same_answer_standing_pair(seed: int, index: int, stale: bool) -> PilotCase:
    cid = _case_id(seed, "standing-stale" if stale else "standing-live", index)
    obj = f"obj-{_opaque(seed + index, 'pair-object')}"
    receipt = f"rec-{_opaque(seed + index, 'pair-receipt')}"
    public = PublicCase(
        case_id=cid,
        family_id="same_answer_stale" if stale else "same_answer_live",
        task_answer="SAME",
        objects=(PublicObject(obj, "CLAIM", Standing.AUTHORIZED, "stable-view", ("e2",), (receipt,)),),
        delta=PublicDelta(
            "F0",
            "F1",
            stale_authority_receipts=(receipt,) if stale else (),
        ),
    )
    migration = (
        Migration(obj, Standing.AUTHORIZED, Standing.REOPENED, Disposition.REOPEN)
        if stale
        else Migration(obj, Standing.AUTHORIZED, Standing.AUTHORIZED, Disposition.PRESERVE)
    )
    return PilotCase(public, ProtectedGold(cid, "SAME", (obj,), (migration,)))


def _transported_semantic_authority(seed: int, index: int) -> PilotCase:
    """Semantic change with explicit full transport and fresh authority.

    A warning-union policy reopens because it sees a load-bearing semantic change.
    The protected gold instead requires TRANSPORT: correspondence/obligation
    transport is explicit and authority is freshly re-established for the object.
    """
    cid = _case_id(seed, "transported-authority", index)
    obj = f"obj-{_opaque(seed + index, 'transport-object')}"
    receipt = f"rec-{_opaque(seed + index, 'old-authority')}"
    s0 = f"sv-{_opaque(seed + index, 'transport-s0')}"
    s1 = f"sv-{_opaque(seed + index, 'transport-s1')}"
    witness = f"tw-{_opaque(seed + index, 'transport-witness')}"
    public = PublicCase(
        case_id=cid,
        family_id="semantic_transport_with_fresh_authority",
        task_answer="T",
        objects=(PublicObject(obj, "CLAIM", Standing.AUTHORIZED, s0, ("e-transport",), (receipt,)),),
        delta=PublicDelta(
            from_framework="F0",
            to_framework="F1",
            semantic_relations=((s0, s1, "LOAD_BEARING_DIFFERENCE"),),
            semantic_transport_witnesses=((s0, s1, witness),),
            fresh_authority_object_ids=(obj,),
        ),
    )
    migration = Migration(obj, Standing.AUTHORIZED, Standing.AUTHORIZED, Disposition.TRANSPORT)
    return PilotCase(public, ProtectedGold(cid, "T", (obj,), (migration,)))


def generate_interaction_pilot(seed: int = 20260820, per_family: int = 4) -> tuple[PilotCase, ...]:
    cases = list(generate_pilot(seed=seed, per_family=per_family))
    for i in range(per_family):
        cases.append(_transported_semantic_authority(seed, i))
    rng = random.Random(seed ^ 0x5A17)
    rng.shuffle(cases)
    return tuple(cases)


def generate_pilot(seed: int = 20260820, per_family: int = 4) -> tuple[PilotCase, ...]:
    rng = random.Random(seed)
    offsets = list(range(per_family))
    rng.shuffle(offsets)
    cases: list[PilotCase] = []
    for i in offsets:
        cases.append(_stale_certificate(seed, i))
        cases.append(_operator_reopens_negative(seed, i))
        cases.append(_same_answer_standing_pair(seed, i, False))
        cases.append(_same_answer_standing_pair(seed, i, True))
    rng.shuffle(cases)
    return tuple(cases)


def public_jsonl(cases: Iterable[PilotCase]) -> str:
    return "".join(
        json.dumps(case.public.payload(), sort_keys=True, separators=(",", ":")) + "\n"
        for case in cases
    )


def gold_jsonl(cases: Iterable[PilotCase]) -> str:
    return "".join(
        json.dumps(case.gold.payload(), sort_keys=True, separators=(",", ":")) + "\n"
        for case in cases
    )


def score(case: PilotCase, out: PolicyOutput) -> Score:
    expected = {m.object_id: m for m in case.gold.migrations}
    got = {m.object_id: m for m in out.migrations}
    accounted = set(case.gold.affected_object_ids).issubset(got)
    migration_exact = accounted and all(got[obj] == exp for obj, exp in expected.items()) and set(got) == set(expected)
    invalid_promotion = sum(
        1
        for obj_id, expected_migration in expected.items()
        if obj_id in got
        and expected_migration.to_standing in {Standing.REOPENED, Standing.INVALIDATED, Standing.UNKNOWN}
        and got[obj_id].to_standing in {Standing.VERIFIED, Standing.AUTHORIZED}
    )
    return Score(
        task_correct=out.task_answer == case.gold.correct_task_answer,
        migration_exact=migration_exact,
        all_affected_objects_accounted_for=accounted,
        invalid_promotion_count=invalid_promotion,
        protected_surface_violation_count=int(out.protected_surface_violation),
    )


Policy = Callable[[PublicCase], PolicyOutput]


def rule_policy(case: PublicCase) -> PolicyOutput:
    relations = {(a, b): rel for a, b, rel in case.delta.semantic_relations}
    migrations: list[Migration] = []
    stale_receipts = set(case.delta.stale_authority_receipts)
    added_ops = set(case.delta.added_operators)
    for obj in case.objects:
        relation_changed = any(
            a == obj.semantic_view_id and rel == "LOAD_BEARING_DIFFERENCE"
            for (a, _b), rel in relations.items()
        )
        negative_reopened = (
            obj.object_kind == "NEGATIVE_KNOWLEDGE"
            and obj.failure_cause.startswith("MISSING_OPERATOR:")
            and obj.failure_cause.split(":", 1)[1] in added_ops
        )
        authority_stale = bool(set(obj.authority_receipt_ids) & stale_receipts)
        if relation_changed or negative_reopened or authority_stale:
            migrations.append(Migration(obj.object_id, obj.standing, Standing.REOPENED, Disposition.REOPEN))
        else:
            migrations.append(Migration(obj.object_id, obj.standing, obj.standing, Disposition.PRESERVE))
    return PolicyOutput(case.task_answer, tuple(migrations))


def interaction_policy(case: PublicCase) -> PolicyOutput:
    """Coordinated standing migration for the pilot interaction contract."""
    relations = {(a, b): rel for a, b, rel in case.delta.semantic_relations}
    transport_pairs = {(a, b) for a, b, _w in case.delta.semantic_transport_witnesses}
    migrations: list[Migration] = []
    stale_receipts = set(case.delta.stale_authority_receipts)
    added_ops = set(case.delta.added_operators)
    fresh_authority = set(case.delta.fresh_authority_object_ids)
    for obj in case.objects:
        changed_targets = [
            b for (a, b), rel in relations.items()
            if a == obj.semantic_view_id and rel == "LOAD_BEARING_DIFFERENCE"
        ]
        has_full_transport = any(
            (obj.semantic_view_id, target) in transport_pairs
            for target in changed_targets
        )
        negative_reopened = (
            obj.object_kind == "NEGATIVE_KNOWLEDGE"
            and obj.failure_cause.startswith("MISSING_OPERATOR:")
            and obj.failure_cause.split(":", 1)[1] in added_ops
        )
        authority_stale = bool(set(obj.authority_receipt_ids) & stale_receipts)
        if changed_targets and has_full_transport and obj.object_id in fresh_authority and not authority_stale:
            migrations.append(
                Migration(obj.object_id, obj.standing, obj.standing, Disposition.TRANSPORT)
            )
        elif changed_targets or negative_reopened or authority_stale:
            migrations.append(
                Migration(obj.object_id, obj.standing, Standing.REOPENED, Disposition.REOPEN)
            )
        else:
            migrations.append(
                Migration(obj.object_id, obj.standing, obj.standing, Disposition.PRESERVE)
            )
    return PolicyOutput(case.task_answer, tuple(migrations))


def semantic_change_parent(case: PublicCase) -> PolicyOutput:
    relations = {(a, b): rel for a, b, rel in case.delta.semantic_relations}
    migrations = []
    for obj in case.objects:
        changed = any(
            a == obj.semantic_view_id and rel == "LOAD_BEARING_DIFFERENCE"
            for (a, _b), rel in relations.items()
        )
        migrations.append(
            Migration(
                obj.object_id,
                obj.standing,
                Standing.REOPENED if changed else obj.standing,
                Disposition.REOPEN if changed else Disposition.PRESERVE,
            )
        )
    return PolicyOutput(case.task_answer, tuple(migrations))


def negative_applicability_parent(case: PublicCase) -> PolicyOutput:
    added_ops = set(case.delta.added_operators)
    migrations = []
    for obj in case.objects:
        reopened = (
            obj.object_kind == "NEGATIVE_KNOWLEDGE"
            and obj.failure_cause.startswith("MISSING_OPERATOR:")
            and obj.failure_cause.split(":", 1)[1] in added_ops
        )
        migrations.append(
            Migration(
                obj.object_id,
                obj.standing,
                Standing.REOPENED if reopened else obj.standing,
                Disposition.REOPEN if reopened else Disposition.PRESERVE,
            )
        )
    return PolicyOutput(case.task_answer, tuple(migrations))


def authority_drift_parent(case: PublicCase) -> PolicyOutput:
    stale = set(case.delta.stale_authority_receipts)
    migrations = []
    for obj in case.objects:
        reopened = bool(set(obj.authority_receipt_ids) & stale)
        migrations.append(
            Migration(
                obj.object_id,
                obj.standing,
                Standing.REOPENED if reopened else obj.standing,
                Disposition.REOPEN if reopened else Disposition.PRESERVE,
            )
        )
    return PolicyOutput(case.task_answer, tuple(migrations))


def donor_union_policy(case: PublicCase) -> PolicyOutput:
    """Strongest simple donor product for the V0 pilot.

    Reopens an object if *any* current parent detects its own invalidation.
    This intentionally shows that the first pilot families do not establish an
    ORION-specific interaction residual.
    """
    parent_outputs = (
        semantic_change_parent(case),
        negative_applicability_parent(case),
        authority_drift_parent(case),
    )
    by_parent = [
        {m.object_id: m for m in output.migrations}
        for output in parent_outputs
    ]
    migrations = []
    for obj in case.objects:
        candidates = [mapping[obj.object_id] for mapping in by_parent]
        if any(m.disposition is Disposition.REOPEN for m in candidates):
            migrations.append(Migration(obj.object_id, obj.standing, Standing.REOPENED, Disposition.REOPEN))
        else:
            migrations.append(Migration(obj.object_id, obj.standing, obj.standing, Disposition.PRESERVE))
    return PolicyOutput(case.task_answer, tuple(migrations))


def always_preserve(case: PublicCase) -> PolicyOutput:
    return PolicyOutput(
        case.task_answer,
        tuple(Migration(o.object_id, o.standing, o.standing, Disposition.PRESERVE) for o in case.objects),
    )


def always_reopen(case: PublicCase) -> PolicyOutput:
    return PolicyOutput(
        case.task_answer,
        tuple(Migration(o.object_id, o.standing, Standing.REOPENED, Disposition.REOPEN) for o in case.objects),
    )


def answer_only(case: PublicCase) -> PolicyOutput:
    return PolicyOutput(case.task_answer, ())


def evaluate(cases: Iterable[PilotCase], policy: Policy) -> dict:
    scores = [score(c, policy(c.public)) for c in cases]
    return {
        "n": len(scores),
        "task_correct": sum(s.task_correct for s in scores),
        "migration_exact": sum(s.migration_exact for s in scores),
        "accounted": sum(s.all_affected_objects_accounted_for for s in scores),
        "invalid_promotions": sum(s.invalid_promotion_count for s in scores),
        "protected_violations": sum(s.protected_surface_violation_count for s in scores),
        "all_gates_pass": all(s.all_gates_pass for s in scores),
    }
