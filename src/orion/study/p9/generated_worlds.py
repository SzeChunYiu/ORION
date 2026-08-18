"""Deterministic exact-world generators for P9 structural-learning experiments.

The generator creates *paired* hostile worlds.  Within each pair a deliberately
restricted model view is identical while evaluator gold differs, giving an exact
information-sufficiency test before any learner is trained.

Family, split, and gold metadata are evaluator-side.  Model-visible identities
and human-readable labels are opaque content-derived tokens.  No object here can
grant scientific/adoption authority.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Iterable

from orion.transfer.v2.canonical import content_digest

from .structural_world import (
    AffineTransport,
    Atom,
    AtomType,
    FailureRecord,
    GluingVerdict,
    GoldKind,
    GoldTarget,
    MechanicView,
    P9StructuralWorld,
    Relation,
    RelationType,
    ViewMode,
    classify_cycle_gluing,
)


class HostileFamily(str, Enum):
    RELATION_SEMANTICS = "RELATION_SEMANTICS"
    TRANSPORT_GLUING = "TRANSPORT_GLUING"
    FAILURE_HISTORY = "FAILURE_HISTORY"


class CorpusSplit(str, Enum):
    TRAIN = "TRAIN"
    DEV = "DEV"
    TEST = "TEST"


def _opaque(prefix: str, material: str, *, length: int = 16) -> str:
    if len(prefix) != 1 or not prefix.isalpha() or not prefix.islower():
        raise ValueError("opaque-token prefix must be one lowercase letter")
    if not material:
        raise ValueError("opaque-token material is required")
    digest = sha256(material.encode("utf-8")).hexdigest()
    return prefix + digest[:length]


def _token(seed: str, namespace: str, slot: str, *, prefix: str) -> str:
    return _opaque(prefix, f"{seed}|{namespace}|{slot}")


def _bounded_int(seed: str, slot: str, lower: int, upper: int) -> int:
    if lower > upper:
        raise ValueError("invalid integer bounds")
    digest = sha256(f"{seed}|number|{slot}".encode("utf-8")).hexdigest()
    return lower + (int(digest[:16], 16) % (upper - lower + 1))


def _all_identity_tokens(world: P9StructuralWorld) -> set[str]:
    tokens = {world.world_id}
    tokens.update(atom.atom_id for atom in world.atoms)
    tokens.update(relation.relation_id for relation in world.relations)
    tokens.update(transport.transport_id for transport in world.transports)
    tokens.update(mechanic.mechanic_id for mechanic in world.mechanics)
    tokens.update(record.record_id for record in world.history)
    return tokens


@dataclass(frozen=True)
class GeneratedPair:
    """Evaluator-side record for one exact hostile pair."""

    family: HostileFamily
    pair_id: str
    worlds: tuple[P9StructuralWorld, P9StructuralWorld]

    def verify(self) -> None:
        if not self.pair_id:
            raise ValueError("pair id is required")
        if len(self.worlds) != 2:
            raise ValueError("generated pair must contain exactly two worlds")
        left, right = self.worlds
        left.verify()
        right.verify()
        if left.world_id == right.world_id:
            raise ValueError("pair worlds must have distinct evaluator identities")
        if left.gold == right.gold:
            raise ValueError("hostile pair must require different gold")

        if self.family is HostileFamily.RELATION_SEMANTICS:
            if left.fingerprint(ViewMode.SURFACE) != right.fingerprint(ViewMode.SURFACE):
                raise ValueError("relation pair surface view must collide")
            if left.fingerprint(ViewMode.TOPOLOGY) != right.fingerprint(ViewMode.TOPOLOGY):
                raise ValueError("relation pair topology view must collide")
            if left.fingerprint(ViewMode.TYPED) == right.fingerprint(ViewMode.TYPED):
                raise ValueError("relation pair typed view must separate")
        elif self.family is HostileFamily.TRANSPORT_GLUING:
            if left.fingerprint(ViewMode.TYPED) != right.fingerprint(ViewMode.TYPED):
                raise ValueError("transport pair typed view must collide")
            if left.fingerprint(ViewMode.CURRENT) == right.fingerprint(ViewMode.CURRENT):
                raise ValueError("transport pair current view must separate")
            cycle = tuple(atom.atom_id for atom in left.atoms) + (left.atoms[0].atom_id,)
            if classify_cycle_gluing(left, cycle) is not GluingVerdict.GLUE:
                raise ValueError("first transport world must glue")
            if classify_cycle_gluing(right, cycle) is not GluingVerdict.OBSTRUCTION:
                raise ValueError("second transport world must obstruct")
        elif self.family is HostileFamily.FAILURE_HISTORY:
            if left.fingerprint(ViewMode.CURRENT) != right.fingerprint(ViewMode.CURRENT):
                raise ValueError("history pair current view must collide")
            if left.fingerprint(ViewMode.SEMANTIC) == right.fingerprint(ViewMode.SEMANTIC):
                raise ValueError("history pair semantic view must separate")
        else:  # pragma: no cover - enum extension guard
            raise ValueError(f"unsupported hostile family: {self.family}")

    @property
    def identity_tokens(self) -> frozenset[str]:
        tokens = {self.pair_id}
        for world in self.worlds:
            tokens.update(_all_identity_tokens(world))
        return frozenset(tokens)

    @property
    def pair_digest(self) -> str:
        self.verify()
        return content_digest(self.manifest_entry())

    def manifest_entry(self) -> dict[str, object]:
        """Evaluator manifest entry; contains gold/family and is never a model input."""

        return {
            "schema": "P9.GeneratedPair.v0",
            "family": self.family.value,
            "pair_id": self.pair_id,
            "worlds": [
                {
                    "world_id": world.world_id,
                    "semantic_fingerprint": world.fingerprint(ViewMode.SEMANTIC),
                    "gold": {
                        "kind": world.gold.kind.value,
                        "value": world.gold.value,
                    },
                }
                for world in self.worlds
            ],
            "authority_scope": "EVALUATOR_ONLY_NO_SCIENTIFIC_AUTHORITY",
        }


def _base_seed(family: HostileFamily, seed: str) -> str:
    if not seed:
        raise ValueError("generator seed is required")
    return content_digest(
        {
            "schema": "P9.GeneratedPairSeed.v0",
            "family": family.value,
            "seed": seed,
        }
    )


def _relation_pair(seed: str) -> GeneratedPair:
    material = _base_seed(HostileFamily.RELATION_SEMANTICS, seed)
    claim_id = _token(material, "atom", "0", prefix="a")
    evidence_id = _token(material, "atom", "1", prefix="a")
    relation_id = _token(material, "edge", "0", prefix="r")
    assimilate_id = _token(material, "mechanic", "0", prefix="m")
    reopen_id = _token(material, "mechanic", "1", prefix="m")

    atoms = (
        Atom(claim_id, AtomType.CLAIM, _token(material, "surface", "0", prefix="s")),
        Atom(evidence_id, AtomType.EVIDENCE, _token(material, "surface", "1", prefix="s")),
    )
    mechanics = (
        MechanicView(
            mechanic_id=assimilate_id,
            surface_label=_token(material, "surface", "2", prefix="s"),
            read_atom_ids=(claim_id, evidence_id),
            write_atom_ids=(claim_id,),
            preconditions=("EVIDENCE_RELEVANT",),
            effects=("ASSIMILATE_EVIDENCE",),
            failure_modes=("MAPPING_INVALID",),
            cost=1.0,
        ),
        MechanicView(
            mechanic_id=reopen_id,
            surface_label=_token(material, "surface", "3", prefix="s"),
            read_atom_ids=(claim_id, evidence_id),
            write_atom_ids=(claim_id,),
            preconditions=("EVIDENCE_RELEVANT",),
            effects=("REOPEN_CLAIM",),
            failure_modes=("DEFEATER_NOT_MATERIAL",),
            cost=1.0,
        ),
    )
    relation_surface = _token(material, "surface", "4", prefix="s")
    support = P9StructuralWorld(
        world_id=_token(material, "world", "0", prefix="w"),
        atoms=atoms,
        relations=(
            Relation(
                relation_id,
                evidence_id,
                claim_id,
                RelationType.SUPPORTS,
                relation_surface,
            ),
        ),
        transports=(),
        mechanics=mechanics,
        history=(),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, assimilate_id),
    )
    defeat = P9StructuralWorld(
        world_id=_token(material, "world", "1", prefix="w"),
        atoms=atoms,
        relations=(
            Relation(
                relation_id,
                evidence_id,
                claim_id,
                RelationType.DEFEATS,
                relation_surface,
            ),
        ),
        transports=(),
        mechanics=mechanics,
        history=(),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, reopen_id),
    )
    pair = GeneratedPair(
        family=HostileFamily.RELATION_SEMANTICS,
        pair_id=_token(material, "pair", "0", prefix="p"),
        worlds=(support, defeat),
    )
    pair.verify()
    return pair


def _transport_pair(seed: str) -> GeneratedPair:
    material = _base_seed(HostileFamily.TRANSPORT_GLUING, seed)
    chart_ids = tuple(
        _token(material, "atom", str(index), prefix="a") for index in range(3)
    )
    atoms = tuple(
        Atom(
            atom_id,
            AtomType.REPRESENTATION,
            _token(material, "surface", str(index), prefix="s"),
        )
        for index, atom_id in enumerate(chart_ids)
    )
    relation_ids = tuple(
        _token(material, "edge", str(index), prefix="r") for index in range(3)
    )
    endpoints = (
        (chart_ids[0], chart_ids[1]),
        (chart_ids[1], chart_ids[2]),
        (chart_ids[2], chart_ids[0]),
    )
    relations = tuple(
        Relation(
            relation_id,
            source,
            target,
            RelationType.MAPS_TO,
            _token(material, "surface", str(index + 3), prefix="s"),
        )
        for index, (relation_id, (source, target)) in enumerate(
            zip(relation_ids, endpoints, strict=True)
        )
    )

    exponent_1 = _bounded_int(material, "scale-1", -2, 2)
    exponent_2 = _bounded_int(material, "scale-2", -2, 2)
    scale_1 = 2.0**exponent_1
    scale_2 = 2.0**exponent_2
    offset_1 = float(_bounded_int(material, "offset-1", -4, 4))
    offset_2 = float(_bounded_int(material, "offset-2", -4, 4))
    composed_scale = scale_2 * scale_1
    composed_offset = scale_2 * offset_1 + offset_2
    inverse_scale = 1.0 / composed_scale
    inverse_offset = -composed_offset / composed_scale
    perturbation = 1.0 if _bounded_int(material, "perturb", 0, 1) else -1.0

    transport_ids = tuple(
        _token(material, "transport", str(index), prefix="t") for index in range(3)
    )
    compatible_transports = (
        AffineTransport(transport_ids[0], *endpoints[0], scale_1, offset_1),
        AffineTransport(transport_ids[1], *endpoints[1], scale_2, offset_2),
        AffineTransport(
            transport_ids[2],
            *endpoints[2],
            inverse_scale,
            inverse_offset,
        ),
    )
    obstructed_transports = (
        compatible_transports[0],
        compatible_transports[1],
        AffineTransport(
            transport_ids[2],
            *endpoints[2],
            inverse_scale,
            inverse_offset + perturbation,
        ),
    )
    compatible = P9StructuralWorld(
        world_id=_token(material, "world", "0", prefix="w"),
        atoms=atoms,
        relations=relations,
        transports=compatible_transports,
        mechanics=(),
        history=(),
        gold=GoldTarget(GoldKind.GLUING, GluingVerdict.GLUE.value),
    )
    obstructed = P9StructuralWorld(
        world_id=_token(material, "world", "1", prefix="w"),
        atoms=atoms,
        relations=relations,
        transports=obstructed_transports,
        mechanics=(),
        history=(),
        gold=GoldTarget(GoldKind.GLUING, GluingVerdict.OBSTRUCTION.value),
    )
    pair = GeneratedPair(
        family=HostileFamily.TRANSPORT_GLUING,
        pair_id=_token(material, "pair", "0", prefix="p"),
        worlds=(compatible, obstructed),
    )
    pair.verify()
    return pair


def _failure_pair(seed: str) -> GeneratedPair:
    material = _base_seed(HostileFamily.FAILURE_HISTORY, seed)
    claim_id = _token(material, "atom", "0", prefix="a")
    observation_id = _token(material, "atom", "1", prefix="a")
    primary_id = _token(material, "mechanic", "0", prefix="m")
    alternate_id = _token(material, "mechanic", "1", prefix="m")
    atoms = (
        Atom(claim_id, AtomType.CLAIM, _token(material, "surface", "0", prefix="s")),
        Atom(
            observation_id,
            AtomType.OBSERVATION,
            _token(material, "surface", "1", prefix="s"),
        ),
    )
    mechanics = (
        MechanicView(
            mechanic_id=primary_id,
            surface_label=_token(material, "surface", "2", prefix="s"),
            read_atom_ids=(claim_id, observation_id),
            write_atom_ids=(claim_id,),
            preconditions=("LOCAL_PRECONDITION",),
            effects=("CANDIDATE_PROGRESS",),
            failure_modes=("PRECONDITION_FAILED",),
            cost=1.0,
        ),
        MechanicView(
            mechanic_id=alternate_id,
            surface_label=_token(material, "surface", "3", prefix="s"),
            read_atom_ids=(claim_id, observation_id),
            write_atom_ids=(claim_id,),
            preconditions=("ALTERNATE_SUPPORTED",),
            effects=("CANDIDATE_PROGRESS",),
            failure_modes=("ALTERNATE_FAILED",),
            cost=1.2,
        ),
    )
    relations = (
        Relation(
            _token(material, "edge", "0", prefix="r"),
            observation_id,
            claim_id,
            RelationType.DEPENDS_ON,
            _token(material, "surface", "4", prefix="s"),
        ),
    )
    clean = P9StructuralWorld(
        world_id=_token(material, "world", "0", prefix="w"),
        atoms=atoms,
        relations=relations,
        transports=(),
        mechanics=mechanics,
        history=(),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, primary_id),
    )
    negative = P9StructuralWorld(
        world_id=_token(material, "world", "1", prefix="w"),
        atoms=atoms,
        relations=relations,
        transports=(),
        mechanics=mechanics,
        history=(
            FailureRecord(
                _token(material, "failure", "0", prefix="f"),
                primary_id,
                "PRECONDITION_FAILED",
                (claim_id, observation_id),
            ),
        ),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, alternate_id),
    )
    pair = GeneratedPair(
        family=HostileFamily.FAILURE_HISTORY,
        pair_id=_token(material, "pair", "0", prefix="p"),
        worlds=(clean, negative),
    )
    pair.verify()
    return pair


def generate_pair(family: HostileFamily, seed: str) -> GeneratedPair:
    """Generate one deterministic hostile pair with opaque model-visible identity."""

    if family is HostileFamily.RELATION_SEMANTICS:
        return _relation_pair(seed)
    if family is HostileFamily.TRANSPORT_GLUING:
        return _transport_pair(seed)
    if family is HostileFamily.FAILURE_HISTORY:
        return _failure_pair(seed)
    raise ValueError(f"unsupported hostile family: {family}")


@dataclass(frozen=True)
class GeneratedSplit:
    split: CorpusSplit
    generation_seed_digest: str
    pairs: tuple[GeneratedPair, ...]

    @property
    def worlds(self) -> tuple[P9StructuralWorld, ...]:
        return tuple(world for pair in self.pairs for world in pair.worlds)

    @property
    def identity_tokens(self) -> frozenset[str]:
        tokens: set[str] = set()
        for pair in self.pairs:
            tokens.update(pair.identity_tokens)
        return frozenset(tokens)

    def verify(self) -> None:
        if not self.pairs:
            raise ValueError("generated split must contain at least one pair")
        if not self.generation_seed_digest.startswith("sha256:"):
            raise ValueError("split seed digest must be content-bound")

        seen_pair_ids: set[str] = set()
        seen_pair_tokens: set[str] = set()
        for pair in self.pairs:
            pair.verify()
            if pair.pair_id in seen_pair_ids:
                raise ValueError(f"duplicate pair id: {pair.pair_id}")
            seen_pair_ids.add(pair.pair_id)
            overlap = seen_pair_tokens & set(pair.identity_tokens)
            if overlap:
                raise ValueError(
                    "identity token reused across generated pairs: "
                    + ",".join(sorted(overlap))
                )
            seen_pair_tokens.update(pair.identity_tokens)

    def family_counts(self) -> dict[HostileFamily, int]:
        return dict(Counter(pair.family for pair in self.pairs))

    def model_manifest(self) -> dict[str, object]:
        """Integrity manifest safe to hand to loaders; no family or evaluator gold."""

        self.verify()
        return {
            "schema": "P9.GeneratedSplitModelManifest.v0",
            "split": self.split.value,
            "generation_seed_digest": self.generation_seed_digest,
            "worlds": [
                {
                    "world_id": world.world_id,
                    "state_digest": world.fingerprint(ViewMode.SEMANTIC),
                }
                for world in self.worlds
            ],
            "authority_scope": "DATA_IDENTITY_ONLY",
        }

    def manifest(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "P9.GeneratedSplit.v0",
            "split": self.split.value,
            "generation_seed_digest": self.generation_seed_digest,
            "pair_count": len(self.pairs),
            "world_count": len(self.worlds),
            "pairs": [pair.manifest_entry() for pair in self.pairs],
            "model_manifest_digest": content_digest(self.model_manifest()),
            "authority_scope": "EVALUATOR_DATA_ONLY",
        }

    @property
    def manifest_digest(self) -> str:
        return content_digest(self.manifest())


def generate_balanced_split(
    *,
    seed: str,
    split: CorpusSplit,
    pairs_per_family: int,
) -> GeneratedSplit:
    if not seed:
        raise ValueError("corpus seed is required")
    if pairs_per_family <= 0:
        raise ValueError("pairs_per_family must be positive")

    seed_digest = content_digest(
        {
            "schema": "P9.GeneratedSplitSeed.v0",
            "seed": seed,
            "split": split.value,
            "pairs_per_family": pairs_per_family,
        }
    )
    pairs = tuple(
        generate_pair(
            family,
            f"{seed}|{split.value}|{family.value}|{index}",
        )
        for family in HostileFamily
        for index in range(pairs_per_family)
    )
    out = GeneratedSplit(
        split=split,
        generation_seed_digest=seed_digest,
        pairs=pairs,
    )
    out.verify()
    return out


@dataclass(frozen=True)
class GeneratedCorpus:
    generation_seed_digest: str
    train: GeneratedSplit
    dev: GeneratedSplit
    test: GeneratedSplit

    def verify(self) -> None:
        if not self.generation_seed_digest.startswith("sha256:"):
            raise ValueError("corpus seed digest must be content-bound")
        if self.train.split is not CorpusSplit.TRAIN:
            raise ValueError("train split has wrong split identity")
        if self.dev.split is not CorpusSplit.DEV:
            raise ValueError("dev split has wrong split identity")
        if self.test.split is not CorpusSplit.TEST:
            raise ValueError("test split has wrong split identity")
        self.train.verify()
        self.dev.verify()
        self.test.verify()

        split_tokens = (
            ("train", self.train.identity_tokens),
            ("dev", self.dev.identity_tokens),
            ("test", self.test.identity_tokens),
        )
        for index, (left_name, left_tokens) in enumerate(split_tokens):
            for right_name, right_tokens in split_tokens[index + 1 :]:
                overlap = left_tokens & right_tokens
                if overlap:
                    raise ValueError(
                        f"identity overlap across {left_name}/{right_name}: "
                        + ",".join(sorted(overlap))
                    )

    def manifest(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "P9.GeneratedCorpus.v0",
            "generation_seed_digest": self.generation_seed_digest,
            "splits": {
                "train": self.train.manifest(),
                "dev": self.dev.manifest(),
                "test": self.test.manifest(),
            },
            "authority_scope": "EVALUATOR_DATA_ONLY_NO_SCIENTIFIC_AUTHORITY",
        }

    @property
    def manifest_digest(self) -> str:
        return content_digest(self.manifest())


def generate_corpus(
    *,
    seed: str,
    train_pairs_per_family: int,
    dev_pairs_per_family: int,
    test_pairs_per_family: int,
) -> GeneratedCorpus:
    if not seed:
        raise ValueError("corpus seed is required")
    for name, value in (
        ("train_pairs_per_family", train_pairs_per_family),
        ("dev_pairs_per_family", dev_pairs_per_family),
        ("test_pairs_per_family", test_pairs_per_family),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive")

    corpus_seed_digest = content_digest(
        {
            "schema": "P9.GeneratedCorpusSeed.v0",
            "seed": seed,
            "counts": {
                "train": train_pairs_per_family,
                "dev": dev_pairs_per_family,
                "test": test_pairs_per_family,
            },
        }
    )
    corpus = GeneratedCorpus(
        generation_seed_digest=corpus_seed_digest,
        train=generate_balanced_split(
            seed=seed,
            split=CorpusSplit.TRAIN,
            pairs_per_family=train_pairs_per_family,
        ),
        dev=generate_balanced_split(
            seed=seed,
            split=CorpusSplit.DEV,
            pairs_per_family=dev_pairs_per_family,
        ),
        test=generate_balanced_split(
            seed=seed,
            split=CorpusSplit.TEST,
            pairs_per_family=test_pairs_per_family,
        ),
    )
    corpus.verify()
    return corpus


__all__ = [
    "CorpusSplit",
    "GeneratedCorpus",
    "GeneratedPair",
    "GeneratedSplit",
    "HostileFamily",
    "generate_balanced_split",
    "generate_corpus",
    "generate_pair",
]
