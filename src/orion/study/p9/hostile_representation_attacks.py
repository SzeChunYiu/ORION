"""Running P9's two named hostile alternatives against D1 (P9-U-T4).

``P9-U-T4`` says *"representation-length and format-prior attacks fail"*. Its
ledger blocker says the attacks "are named as hostile alternatives but have not
been run", and its unblock says to run "equal-token/length controls,
semantic-orbit controls, symbol and order reminting, and same-information
round-trip validation **as gates rather than as robustness appendices**".

The attacks are named in exactly one place --
``papers/paper-09-structured-epistemic-learning/successor/P9_U_MANUSCRIPT.tex``
-- and nowhere in the repository is any of them implemented, fixtured or run.
This module runs them.

**What they cannot reach.** The successor experiment the attacks were written
for (the frozen Qwen2.5 0.5B/1.5B/3B run of issue #618) has no outcome, no
checkpoint in this repository, and no reachable provider from this environment.
The attacks are therefore run against the one representation contrast P9 does
publish: D1 v1.2, whose result is shipped at
``research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json``.
The claim scope is ``BOUNDED_D1_ONLY`` and ``P9-U-T4`` stays BLOCKED whatever
this returns; see §2 of the freeze.

**Why the verdict is per contrast.**
``research/failures/2026-08-unresponsive-comparator-prior-valued-margin/``
already establishes that ``TRANSCRIPT_BAG`` and ``TYPED_SERIALIZED_BAG`` each
answered all 128 protected cases with a single label, so ``+0.75`` and ``+0.50``
are label priors and are ``CANNOT_CHECK`` under
:func:`orion.programme.comparator_response.measure_contrast_margin`. An attack
cannot fail against a margin that was never measured: a hostile alternative is a
competing explanation of an effect, and where there is no measured effect there
is nothing for it to explain. So each contrast is re-measured first, and a
contrast whose comparator was constant is reported ``CANNOT_CHECK`` for the
attack too rather than being scored as "the attack failed".

Protocol: ``papers/paper-09-structured-epistemic-learning/protocol/
P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE_2026-08-21.md`` and its JSON twin.
The runner recomputes the twin's parameter digest from its own constants and
refuses to run on a mismatch, and it reports no arm number at all if a
construction precondition fails.

Nothing here edits a frozen P9 result, receipt, protocol or evidence artifact.

Run it::

    python -m orion.study.p9.hostile_representation_attacks --repo-root . \
        --output <result>.json
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterator

from orion.programme.comparator_response import (
    ComparatorResponse,
    ContrastMargin,
    measure_contrast_margin,
    score_comparator,
)
from orion.programme.guard_exercise import GuardExercise, assess_guard
from orion.programme.records import Outcome
from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.p1_method_realization import MethodRealization, build_method_realization

from . import d1 as _d1
from . import d1_runtime as _runtime  # noqa: F401  (installs the v1.2 execution adapters)
from . import d1_experiment as _experiment
from .d1 import (
    COMPARISON_COORDINATES,
    D1Dataset,
    D1Instance,
    D1View,
)
from .d1_data_runtime import generate_d1_dataset

RESULT_SCHEMA_VERSION = "orion.p9.ut4-hostile-representation-attack-result.v1"

FREEZE_DOCUMENT = (
    "papers/paper-09-structured-epistemic-learning/protocol/"
    "P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE_2026-08-21.md"
)
FREEZE_TWIN = (
    "papers/paper-09-structured-epistemic-learning/protocol/"
    "P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE_2026-08-21.json"
)

GATE_SERVED = "P9-U-T4"

SHIPPED_D1_RESULT = (
    "research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json"
)
SHIPPED_DATASET_MANIFEST_DIGEST = (
    "sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c"
)

D1_SEED = "p9-d1-method-transfer-v1"

CLAIM_SCOPE = (
    "BOUNDED_D1_ONLY. Whatever this study returns is a statement about the D1 v1.2 "
    "classical-learner benchmark on its 128-case held-out-domain protected split and about "
    "nothing else. It licenses no statement about any language model, any scale, any second "
    "model family, or the successor experiment of issue #618."
)

TERMINAL_DISPOSITION = (
    "P9-U-T4 stays BLOCKED whatever this returns. The gate guards the successor direct-LLM "
    "result, which has no outcome. This work can only subtract: if an attack succeeds, the D1 "
    "representation reading is narrowed or withdrawn; if none succeeds, the sentence earned is "
    "only that on D1 these two alternatives do not account for the margin against the one "
    "comparator that answered."
)

ENVIRONMENT_BOUNDARY = {
    "successor_llm_run_exists": False,
    "open_weight_checkpoint_present": False,
    "outbound_provider_access": "proxy returns 403 to CONNECT for external providers",
    "attacks_run_against": "D1 v1.2, the only representation contrast P9 publishes",
}

# --- frozen constants (hashed into the twin) -------------------------------

ORBIT_SALT = "p9-t4-orbit-2026-08-21"
ORBIT_PREFIX = "v_"
ORBIT_WIDTH = 12

#: Coordinates whose atomic string values the semantic orbit remints. These are
#: exactly the coordinates that reach any arm's features; ``mechanics`` is left
#: alone so that the dependency topology signature is untouched.
REMINTED_COORDINATES: tuple[str, ...] = (
    "preconditions",
    "invariants",
    "effects",
    "failure_modes",
    "progress_measure",
    "terminal_condition",
    "reconstruction_map",
)

SEQUENCE_COORDINATES: tuple[str, ...] = (
    "preconditions",
    "invariants",
    "effects",
    "failure_modes",
)

PROTECTED_CASES = 128
CASE_RESOLUTION = 1.0 / PROTECTED_CASES

#: RL-3: "essentially nothing changed" bar for the typed arm on the control.
EQUAL_LENGTH_UNCHANGED_FLOOR = 0.95
#: FP-1: the fraction of the base gap a pure reformat must leave for the attack
#: to fail. At or below this, the reformat accounts for more of the published gap
#: than the relational operator it is attributed to.
REFORMAT_GAP_FRACTION = 0.5
#: FP-1 vacuity floor: below four protected cases a halving is not separable from
#: tie-breaking noise.
REFORMAT_MIN_BASE_GAP = 4 * CASE_RESOLUTION

MAX_ORBIT_VIOLATION_RATE = 0.0

NONE_MARKER = "<NONE>"
STRING_MARKER = "<STR>"
LEN_MARKER = ":LEN="

ARM_TRANSCRIPT = "TRANSCRIPT_BAG"
ARM_UNTYPED = "UNTYPED_PAIR"
ARM_TYPED = "TYPED_RELATIONAL"
ARM_SERIALIZED = "TYPED_SERIALIZED_BAG"
ARM_LENGTH_ONLY = "LENGTH_ONLY"
ARM_LENGTH_RELATIONAL = "LENGTH_RELATIONAL"
ARM_SERIALIZED_INDEXED = "SERIALIZED_INDEXED"
ARM_SERIALIZED_PATHONLY = "SERIALIZED_PATHONLY"

ARM_ORDER: tuple[str, ...] = (
    ARM_TRANSCRIPT,
    ARM_UNTYPED,
    ARM_TYPED,
    ARM_SERIALIZED,
    ARM_LENGTH_ONLY,
    ARM_LENGTH_RELATIONAL,
    ARM_SERIALIZED_INDEXED,
    ARM_SERIALIZED_PATHONLY,
)

DATASET_BASE = "BASE"
DATASET_EQUAL_LENGTH = "EQUAL_LENGTH"
DATASET_ORBIT = "SEMANTIC_ORBIT"
DATASET_ORDER = "ORDER_PERMUTATION"

VERDICT_CONSTRUCTION_FAILED = "T4_CONSTRUCTION_FAILED"
VERDICT_NO_MEASURABLE_CONTRAST = "T4_NO_MEASURABLE_CONTRAST"
VERDICT_ATTACK_SUCCEEDED = "T4_ATTACK_SUCCEEDED"
VERDICT_ATTACKS_UNEXERCISED = "T4_ATTACKS_UNEXERCISED"
VERDICT_ATTACKS_DID_NOT_SUCCEED = "T4_ATTACKS_DID_NOT_SUCCEED_ON_D1"

RESPONSE_DEFINITIONS: Mapping[str, str] = {
    ARM_TRANSCRIPT: (
        "reminted surface action tokens and their counts for both sides of the pair; the tokens "
        "are minted from the split seed and are disjoint between train and the protected domain"
    ),
    ARM_UNTYPED: (
        "per-coordinate presence, unknown flag and cardinality for both sides, plus whether the "
        "dependency topologies agree"
    ),
    ARM_TYPED: (
        "per-coordinate value equality and unknown flag across the two sides, plus each side's "
        "coordinate cardinality"
    ),
    ARM_SERIALIZED: (
        "a bag of canonical path=value tokens over the same typed payload, with held-out-domain "
        "values verbatim"
    ),
    ARM_LENGTH_ONLY: (
        "per-coordinate presence and cardinality for each side separately, with no value "
        "identity, no cross-side comparison and no unknown flag"
    ),
    ARM_LENGTH_RELATIONAL: (
        "cross-side agreement of presence and of cardinality only, with no value identity, no "
        "absolute cardinality and no unknown flag"
    ),
    ARM_SERIALIZED_INDEXED: (
        "the same canonical path=value token bag with every string value replaced by its index in "
        "that instance's sorted atom alphabet; reversible, adds no comparison operator"
    ),
    ARM_SERIALIZED_PATHONLY: (
        "the same canonical token bag with every string value replaced by one constant marker; "
        "strictly less information than the serialized arm and a domain-independent vocabulary"
    ),
}


# ---------------------------------------------------------------------------
# Freeze twin
# ---------------------------------------------------------------------------

FROZEN_PARAMETERS: dict[str, Any] = {
    "record": "P9_U_T4_HOSTILE_REPRESENTATION_ATTACK_FREEZE",
    "freeze_document": FREEZE_DOCUMENT,
    "gate_served": GATE_SERVED,
    "claim_scope": CLAIM_SCOPE,
    "attacked_result": {
        "artifact": SHIPPED_D1_RESULT,
        "dataset_manifest_digest": SHIPPED_DATASET_MANIFEST_DIGEST,
        "seed": D1_SEED,
        "protected_cases": PROTECTED_CASES,
    },
    "arms": list(ARM_ORDER),
    "dataset_variants": [DATASET_BASE, DATASET_EQUAL_LENGTH, DATASET_ORBIT, DATASET_ORDER],
    "orbit": {
        "salt": ORBIT_SALT,
        "prefix": ORBIT_PREFIX,
        "width": ORBIT_WIDTH,
        "coordinates": list(REMINTED_COORDINATES),
        "must_be_injective": True,
    },
    "equal_length_rule": (
        "a sequence coordinate is corrupted by replacing its last-in-canonical-order element with "
        "the mutation token instead of appending it; scalar coordinates and dependency reversal "
        "already preserve cardinality and are unchanged"
    ),
    "order_permutation_rule": "reverse every sequence-valued comparison coordinate before rebuilding",
    "indexing_rule": (
        "replace each string leaf value by '#i', i being its position in the sorted list of "
        "distinct string atoms occurring in that instance's serialized token list; LEN tokens, "
        "<NONE> markers and integer leaves are untouched"
    ),
    "thresholds": {
        "case_resolution": CASE_RESOLUTION,
        "equal_length_unchanged_floor": EQUAL_LENGTH_UNCHANGED_FLOOR,
        "reformat_gap_fraction": REFORMAT_GAP_FRACTION,
        "reformat_min_base_gap": REFORMAT_MIN_BASE_GAP,
        "max_orbit_violation_rate": MAX_ORBIT_VIOLATION_RATE,
    },
    "preconditions": [
        "PC-1 DATASET FIDELITY: the regenerated dataset reproduces the shipped manifest digest",
        "PC-2 GOLD PRESERVATION: every derived variant reproduces every gold label, position for position",
        "PC-3 CARDINALITY MATCH: the equal-length control preserves cardinality and presence on every coordinate and side",
        "PC-4 ORBIT BIJECTIVITY: the symbol remint is injective on the atom alphabet",
        "PC-5 INDEX REVERSIBILITY: the reversible-indexed serialization decodes back to the original token list",
        "PC-6 LABEL VARIETY: the protected split's gold takes more than one value",
    ],
    "verdicts": {
        "construction_failed": VERDICT_CONSTRUCTION_FAILED,
        "no_measurable_contrast": VERDICT_NO_MEASURABLE_CONTRAST,
        "attack_succeeded": VERDICT_ATTACK_SUCCEEDED,
        "attacks_unexercised": VERDICT_ATTACKS_UNEXERCISED,
        "attacks_did_not_succeed": VERDICT_ATTACKS_DID_NOT_SUCCEED,
    },
    "model_grid": "frozen d1_experiment.model_specs(); selection by (-dev_accuracy, complexity_rank, config_id)",
}


def frozen_digest() -> str:
    return content_digest(FROZEN_PARAMETERS)


class FreezeViolation(RuntimeError):
    """Raised when the runner's constants no longer match the frozen record."""


def verify_against_twin(repo_root: Path) -> dict[str, Any]:
    twin_path = repo_root / FREEZE_TWIN
    if not twin_path.exists():
        raise FreezeViolation(f"freeze twin missing: {twin_path}")
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    recorded = twin.get("parameters_sha256")
    computed = frozen_digest()
    if recorded != computed:
        raise FreezeViolation(
            "runner parameters do not match the frozen record: "
            f"recorded {recorded}, computed {computed}"
        )
    return {"parameters_sha256": computed, "freeze_twin": FREEZE_TWIN}


# ---------------------------------------------------------------------------
# Serialization helpers shared by the format-prior arms and the round-trip gate
# ---------------------------------------------------------------------------

_LIST_STRING_KEYS = ("effects", "failure_modes", "invariants", "preconditions", "unknown_coordinates")
_SCALAR_KEYS = ("progress_measure", "reconstruction_map", "terminal_condition")


def split_token(token: str) -> tuple[str, str]:
    """Split one serialized token into its path part and its value part."""

    path, _, value = token.partition("=")
    return path, value


def string_atoms(tokens: Sequence[str]) -> tuple[str, ...]:
    """The distinct string leaf values of a serialized token list, sorted.

    ``LEN`` markers, ``<NONE>`` markers and integer leaves are not atoms: they
    are structure, not values.
    """

    atoms: set[str] = set()
    for token in tokens:
        path, value = split_token(token)
        if path.endswith(LEN_MARKER[:-1]):
            continue
        if value == NONE_MARKER:
            continue
        if value.lstrip("-").isdigit():
            continue
        atoms.add(value)
    return tuple(sorted(atoms))


def index_serialization(tokens: Sequence[str]) -> tuple[tuple[str, ...], dict[str, str]]:
    """Reversible per-instance indexing of a serialized token list."""

    atoms = string_atoms(tokens)
    table = {f"#{position}": atom for position, atom in enumerate(atoms)}
    inverse = {atom: key for key, atom in table.items()}
    out: list[str] = []
    for token in tokens:
        path, value = split_token(token)
        if value in inverse:
            out.append(f"{path}={inverse[value]}")
        else:
            out.append(token)
    return tuple(out), table


def restore_serialization(tokens: Sequence[str], table: Mapping[str, str]) -> tuple[str, ...]:
    """Invert :func:`index_serialization` using only its per-instance table."""

    out: list[str] = []
    for token in tokens:
        path, value = split_token(token)
        if value in table:
            out.append(f"{path}={table[value]}")
        else:
            out.append(token)
    return tuple(out)


def pathonly_serialization(tokens: Sequence[str]) -> tuple[str, ...]:
    """Erase every string value, keeping paths, cardinalities and absence."""

    out: list[str] = []
    for token in tokens:
        path, value = split_token(token)
        if path.endswith(LEN_MARKER[:-1]) or value == NONE_MARKER or value.lstrip("-").isdigit():
            out.append(token)
        else:
            out.append(f"{path}={STRING_MARKER}")
    return tuple(out)


@dataclass(frozen=True)
class _Record:
    path: str
    is_length: bool
    value: str


def _records(tokens: Sequence[str]) -> tuple[_Record, ...]:
    out: list[_Record] = []
    for token in tokens:
        path, value = split_token(token)
        if path.endswith(LEN_MARKER[:-1]):
            out.append(_Record(path[: -len(LEN_MARKER[:-1])], True, value))
        else:
            out.append(_Record(path, False, value))
    return tuple(out)


def _decode(records: Sequence[_Record], position: int, path: str) -> tuple[Any, int]:
    record = records[position]
    if record.path == path:
        if record.is_length:
            count = int(record.value)
            position += 1
            items: list[Any] = []
            for _ in range(count):
                item, position = _decode(records, position, path + "[]")
                items.append(item)
            return items, position
        return (None if record.value == NONE_MARKER else record.value), position + 1
    prefix = path + "."
    mapping: dict[str, Any] = {}
    while position < len(records) and records[position].path.startswith(prefix):
        rest = records[position].path[len(prefix) :]
        key = rest.split(".", 1)[0].split("[", 1)[0]
        value, position = _decode(records, position, prefix + key)
        mapping[key] = value
    return mapping, position


def decode_typed_serialization(tokens: Sequence[str]) -> dict[str, Any]:
    """Rebuild the typed payload from its serialized token list.

    The token stream is a pre-order traversal, so it decodes without a schema
    except for one thing the encoder erases: every leaf is written as text. The
    D1 typed payload's only integer leaves are the dependency-topology indices,
    so those are restored by name. This is the "exact information check" the
    unblock asks for, run as a gate over every instance rather than asserted.
    """

    decoded, consumed = _decode(_records(tokens), 0, "root")
    if consumed != len(tokens):
        raise ValueError(f"serialized stream not fully consumed: {consumed} of {len(tokens)}")
    if not isinstance(decoded, dict):
        raise ValueError("serialized stream did not decode to a mapping")
    for side in ("left", "right"):
        payload = decoded.get(side)
        if not isinstance(payload, dict):
            raise ValueError(f"serialized stream is missing its {side} side")
        payload["dependencies"] = [
            [int(index) for index in edge] for edge in payload.get("dependencies", [])
        ]
    return decoded


# ---------------------------------------------------------------------------
# Feature families
# ---------------------------------------------------------------------------


def _untyped_sides(instance: D1Instance) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    payload = instance.model_payload(D1View.UNTYPED)
    left = payload["left"]
    right = payload["right"]
    assert isinstance(left, Mapping) and isinstance(right, Mapping)
    return left, right


def length_only_features(instance: D1Instance) -> dict[str, object]:
    """`H_LEN` as an arm: cardinality and presence, one side at a time."""

    left, right = _untyped_sides(instance)
    features: dict[str, object] = {}
    for side_name, side in (("left", left), ("right", right)):
        coordinates = side["coordinates"]
        assert isinstance(coordinates, Mapping)
        for coordinate in COMPARISON_COORDINATES:
            shape = coordinates[coordinate]
            assert isinstance(shape, Mapping)
            features[f"{coordinate}:{side_name}_present"] = bool(shape["present"])
            if "length" in shape:
                features[f"{coordinate}:{side_name}_length"] = int(shape["length"])
    return features


def length_relational_features(instance: D1Instance) -> dict[str, object]:
    """`H_LEN` with the relational operator kept and the values removed."""

    left, right = _untyped_sides(instance)
    left_coordinates = left["coordinates"]
    right_coordinates = right["coordinates"]
    assert isinstance(left_coordinates, Mapping) and isinstance(right_coordinates, Mapping)
    features: dict[str, object] = {}
    for coordinate in COMPARISON_COORDINATES:
        left_shape = left_coordinates[coordinate]
        right_shape = right_coordinates[coordinate]
        assert isinstance(left_shape, Mapping) and isinstance(right_shape, Mapping)
        features[f"{coordinate}:present_agree"] = bool(left_shape["present"]) == bool(
            right_shape["present"]
        )
        if "length" in left_shape and "length" in right_shape:
            left_length = int(left_shape["length"])
            right_length = int(right_shape["length"])
            features[f"{coordinate}:same_length"] = left_length == right_length
            features[f"{coordinate}:length_diff"] = left_length - right_length
    return features


def serialized_tokens(instance: D1Instance) -> tuple[str, ...]:
    payload = instance.model_payload(D1View.TYPED_SERIALIZED)
    sequence = payload["sequence"]
    assert isinstance(sequence, list)
    return tuple(str(token) for token in sequence)


def _bag(tokens: Sequence[str]) -> dict[str, object]:
    features: dict[str, object] = {"sequence_length": len(tokens)}
    for token in tokens:
        features[f"token:{token}"] = 1.0
    return features


def serialized_indexed_features(instance: D1Instance) -> dict[str, object]:
    indexed, _table = index_serialization(serialized_tokens(instance))
    return _bag(indexed)


def serialized_pathonly_features(instance: D1Instance) -> dict[str, object]:
    return _bag(pathonly_serialization(serialized_tokens(instance)))


def _base_feature(family: _experiment.D1FeatureFamily) -> Callable[[D1Instance], dict[str, object]]:
    def extract(instance: D1Instance) -> dict[str, object]:
        return _experiment.features(instance, family)

    return extract


FEATURE_FUNCTIONS: Mapping[str, Callable[[D1Instance], dict[str, object]]] = {
    ARM_TRANSCRIPT: _base_feature(_experiment.D1FeatureFamily.TRANSCRIPT_BAG),
    ARM_UNTYPED: _base_feature(_experiment.D1FeatureFamily.UNTYPED_PAIR),
    ARM_TYPED: _base_feature(_experiment.D1FeatureFamily.TYPED_RELATIONAL),
    ARM_SERIALIZED: _base_feature(_experiment.D1FeatureFamily.TYPED_SERIALIZED_BAG),
    ARM_LENGTH_ONLY: length_only_features,
    ARM_LENGTH_RELATIONAL: length_relational_features,
    ARM_SERIALIZED_INDEXED: serialized_indexed_features,
    ARM_SERIALIZED_PATHONLY: serialized_pathonly_features,
}


# ---------------------------------------------------------------------------
# Dataset variants
# ---------------------------------------------------------------------------


def equal_length_mutated_value(
    method: MethodRealization,
    coordinate: str,
    salt: str,
    *,
    fallback: Callable[[MethodRealization, str, str], object],
) -> object:
    """Cardinality-preserving corruption: replace an element, never append one.

    ``fallback`` is the frozen v1.2 corruption, used verbatim for the scalar
    coordinates and for the dependency reversal, both of which already preserve
    cardinality and presence.
    """

    token = "x_" + sha256(f"{salt}|{coordinate}".encode("utf-8")).hexdigest()[:12]
    if coordinate in SEQUENCE_COORDINATES:
        original = tuple(getattr(method, coordinate))
        if not original:
            raise ValueError(
                f"equal-length control cannot corrupt an empty {coordinate} without changing its "
                "cardinality"
            )
        kept = tuple(sorted(original))[:-1]
        replaced = tuple(sorted((*kept, token)))
        if len(replaced) != len(original):
            raise ValueError(
                f"equal-length control changed the cardinality of {coordinate}: "
                f"{len(original)} -> {len(replaced)}"
            )
        return replaced
    return fallback(method, coordinate, salt)


@contextmanager
def _equal_length_generator() -> Iterator[None]:
    """Swap in the cardinality-preserving corruption for one generation.

    The swap is the mechanism ``d1_data_runtime`` already uses to install the
    protocol v1.2 corrections, and it is restored on exit so that no other
    caller ever sees the control's rule.
    """

    original = _d1._mutated_value

    def _replace(method: MethodRealization, coordinate: str, salt: str) -> object:
        return equal_length_mutated_value(method, coordinate, salt, fallback=original)

    _d1._mutated_value = _replace
    try:
        yield
    finally:
        _d1._mutated_value = original


def _rebuild_with(method: MethodRealization, **changes: object) -> MethodRealization:
    values: dict[str, object] = {
        "method_id": method.method_id,
        "source_digest": method.source_digest,
        "source_version": method.source_version,
        "target_role": method.target_role,
        "preconditions": method.preconditions,
        "assumptions": method.assumptions,
        "resources": method.resources,
        "representation_in": method.representation_in,
        "representation_out": method.representation_out,
        "mechanics": method.mechanics,
        "dependencies": method.dependencies,
        "invariants": method.invariants,
        "progress_measure": method.progress_measure,
        "effects": method.effects,
        "terminal_condition": method.terminal_condition,
        "reconstruction_map": method.reconstruction_map,
        "failure_modes": method.failure_modes,
        "lineage": method.lineage,
        "authority_boundary": method.authority_boundary,
        "unknown_coordinates": method.unknown_coordinates,
    }
    values.update(changes)
    return build_method_realization(**values)  # type: ignore[arg-type]


def _dataset_atoms(dataset: D1Dataset) -> tuple[str, ...]:
    atoms: set[str] = set()
    for instance in (*dataset.train, *dataset.dev, *dataset.test):
        for method in (instance.left, instance.right):
            for coordinate in REMINTED_COORDINATES:
                value = getattr(method, coordinate)
                if value is None:
                    continue
                if isinstance(value, tuple):
                    atoms.update(str(item) for item in value)
                else:
                    atoms.add(str(value))
    return tuple(sorted(atoms))


def build_orbit_map(dataset: D1Dataset) -> dict[str, str]:
    """One global bijection on the value alphabet, checked injective."""

    mapping = {
        atom: ORBIT_PREFIX
        + sha256(f"{ORBIT_SALT}|{atom}".encode("utf-8")).hexdigest()[:ORBIT_WIDTH]
        for atom in _dataset_atoms(dataset)
    }
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("semantic orbit remint is not injective on the atom alphabet")
    return mapping


def _orbit_method(method: MethodRealization, mapping: Mapping[str, str]) -> MethodRealization:
    changes: dict[str, object] = {}
    for coordinate in REMINTED_COORDINATES:
        value = getattr(method, coordinate)
        if value is None:
            continue
        if isinstance(value, tuple):
            changes[coordinate] = tuple(mapping[str(item)] for item in value)
        else:
            changes[coordinate] = mapping[str(value)]
    return _rebuild_with(method, **changes)


def _reordered_method(method: MethodRealization) -> MethodRealization:
    changes: dict[str, object] = {
        coordinate: tuple(reversed(getattr(method, coordinate)))
        for coordinate in SEQUENCE_COORDINATES
    }
    return _rebuild_with(method, **changes)


def _transform_instance(
    instance: D1Instance, transform: Callable[[MethodRealization], MethodRealization]
) -> D1Instance:
    transformed = D1Instance(
        instance_id=instance.instance_id,
        domain=instance.domain,
        split=instance.split,
        left=transform(instance.left),
        right=transform(instance.right),
        label=instance.label,
        mutation_coordinates=instance.mutation_coordinates,
        surface_left=instance.surface_left,
        surface_right=instance.surface_right,
        surface_role_left=instance.surface_role_left,
        surface_role_right=instance.surface_role_right,
    )
    transformed.verify()
    return transformed


def _transform_dataset(
    dataset: D1Dataset, transform: Callable[[MethodRealization], MethodRealization]
) -> D1Dataset:
    train = tuple(_transform_instance(row, transform) for row in dataset.train)
    dev = tuple(_transform_instance(row, transform) for row in dataset.dev)
    test = tuple(_transform_instance(row, transform) for row in dataset.test)
    provisional = {
        "schema": "P9.D1Dataset.v1",
        "seed_digest": content_digest(dataset.seed),
        "train": [row.manifest_entry() for row in train],
        "dev": [row.manifest_entry() for row in dev],
        "test": [row.manifest_entry() for row in test],
        "authority": "EVALUATOR_ONLY_NO_SCIENTIFIC_AUTHORITY",
    }
    return D1Dataset(dataset.seed, train, dev, test, content_digest(provisional))


def build_datasets() -> dict[str, D1Dataset]:
    """The frozen dataset and its three gold-preserving variants."""

    base = generate_d1_dataset(seed=D1_SEED)
    with _equal_length_generator():
        equal_length = generate_d1_dataset(seed=D1_SEED)
    orbit_map = build_orbit_map(base)
    orbit = _transform_dataset(base, lambda method: _orbit_method(method, orbit_map))
    order = _transform_dataset(base, _reordered_method)
    return {
        DATASET_BASE: base,
        DATASET_EQUAL_LENGTH: equal_length,
        DATASET_ORBIT: orbit,
        DATASET_ORDER: order,
    }


# ---------------------------------------------------------------------------
# Preconditions
# ---------------------------------------------------------------------------


def _coordinate_shape(instance: D1Instance, side: str) -> dict[str, tuple[bool, int | None]]:
    left, right = _untyped_sides(instance)
    coordinates = (left if side == "left" else right)["coordinates"]
    assert isinstance(coordinates, Mapping)
    out: dict[str, tuple[bool, int | None]] = {}
    for coordinate in COMPARISON_COORDINATES:
        shape = coordinates[coordinate]
        assert isinstance(shape, Mapping)
        length = int(shape["length"]) if "length" in shape else None
        out[coordinate] = (bool(shape["present"]), length)
    return out


def check_preconditions(datasets: Mapping[str, D1Dataset]) -> dict[str, Any]:
    """Every construction check, run before a single arm is fitted."""

    base = datasets[DATASET_BASE]
    checks: dict[str, Any] = {}

    checks["PC-1_DATASET_FIDELITY"] = {
        "passed": base.manifest_digest == SHIPPED_DATASET_MANIFEST_DIGEST,
        "expected": SHIPPED_DATASET_MANIFEST_DIGEST,
        "observed": base.manifest_digest,
        "detail": "the regenerated dataset must be the one P9 shipped, not a local lookalike",
    }

    gold_rows = []
    for name in (DATASET_EQUAL_LENGTH, DATASET_ORBIT, DATASET_ORDER):
        variant = datasets[name]
        changed = 0
        compared = 0
        for split in ("train", "dev", "test"):
            for original, derived in zip(
                getattr(base, split), getattr(variant, split), strict=True
            ):
                compared += 1
                if original.label is not derived.label:
                    changed += 1
                if _d1.classify_methods(derived.left, derived.right) is not derived.label:
                    changed += 1
        gold_rows.append({"variant": name, "instances_compared": compared, "labels_changed": changed})
    checks["PC-2_GOLD_PRESERVATION"] = {
        "passed": all(row["labels_changed"] == 0 for row in gold_rows)
        and all(row["instances_compared"] > 0 for row in gold_rows),
        "rows": gold_rows,
        "detail": "a transform that moves a label is a different benchmark, not a control",
    }

    control = datasets[DATASET_EQUAL_LENGTH]
    mismatches = 0
    compared_shapes = 0
    corrupted_instances = 0
    for instance in (*control.train, *control.dev, *control.test):
        if not instance.mutation_coordinates:
            continue
        corrupted_instances += 1
        left_shape = _coordinate_shape(instance, "left")
        right_shape = _coordinate_shape(instance, "right")
        for coordinate in COMPARISON_COORDINATES:
            compared_shapes += 1
            if left_shape[coordinate] != right_shape[coordinate]:
                mismatches += 1
    checks["PC-3_CARDINALITY_MATCH"] = {
        "passed": mismatches == 0 and corrupted_instances > 0,
        "corrupted_instances": corrupted_instances,
        "coordinate_side_comparisons": compared_shapes,
        "cardinality_or_presence_mismatches": mismatches,
        "detail": (
            "on the equal-length control every corrupted instance must present the same presence "
            "and cardinality on both sides of every coordinate"
        ),
    }

    orbit_map = build_orbit_map(base)
    checks["PC-4_ORBIT_BIJECTIVITY"] = {
        "passed": len(set(orbit_map.values())) == len(orbit_map) and len(orbit_map) > 0,
        "atoms": len(orbit_map),
        "distinct_images": len(set(orbit_map.values())),
        "detail": "a non-injective remint destroys information and is not a semantic orbit",
    }

    reversible_failures = 0
    roundtrip_failures = 0
    instances_checked = 0
    for instance in (*base.train, *base.dev, *base.test):
        instances_checked += 1
        tokens = serialized_tokens(instance)
        indexed, table = index_serialization(tokens)
        if restore_serialization(indexed, table) != tokens:
            reversible_failures += 1
        typed = instance.model_payload(D1View.TYPED)
        if decode_typed_serialization(tokens) != typed:
            roundtrip_failures += 1
    checks["PC-5_INDEX_REVERSIBILITY"] = {
        "passed": reversible_failures == 0 and instances_checked > 0,
        "instances_checked": instances_checked,
        "failures": reversible_failures,
        "detail": "the reformat must be shown to add and to remove nothing",
    }
    checks["RT_SAME_INFORMATION_ROUND_TRIP"] = {
        "passed": roundtrip_failures == 0 and instances_checked > 0,
        "instances_checked": instances_checked,
        "failures": roundtrip_failures,
        "detail": (
            "the serialized view is claimed to carry the same information as the typed view; this "
            "decodes every instance's token list back to the typed payload and compares it"
        ),
    }

    labels = {instance.label.value for instance in base.test}
    checks["PC-6_LABEL_VARIETY"] = {
        "passed": len(labels) > 1,
        "protected_cases": len(base.test),
        "distinct_gold_labels": sorted(labels),
        "detail": "a split whose gold never varies cannot separate any two arms",
    }

    return checks


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmRun:
    """One arm fitted on one dataset variant and scored on its protected split."""

    dataset: str
    arm_id: str
    config_id: str
    dev_accuracy: float
    predictions: tuple[str, ...]
    gold: tuple[str, ...]
    train_features: tuple[tuple[tuple[str, object], ...], ...]
    dev_features: tuple[tuple[tuple[str, object], ...], ...]
    test_features: tuple[tuple[tuple[str, object], ...], ...]

    @property
    def accuracy(self) -> float:
        return sum(
            1 for gold, prediction in zip(self.gold, self.predictions, strict=True) if gold == prediction
        ) / len(self.gold)

    def response(self) -> ComparatorResponse:
        return score_comparator(
            self.arm_id,
            gold=self.gold,
            predicted=self.predictions,
            response_definition=RESPONSE_DEFINITIONS[self.arm_id],
        )


def _freeze_features(rows: Sequence[dict[str, object]]) -> tuple[tuple[tuple[str, object], ...], ...]:
    return tuple(tuple(sorted(row.items())) for row in rows)


def run_arm(
    dataset: D1Dataset,
    dataset_id: str,
    arm_id: str,
    feature_fn: Callable[[D1Instance], dict[str, object]],
) -> ArmRun:
    """Fit one arm with the frozen model grid and the frozen selection rule."""

    train_rows = [feature_fn(row) for row in dataset.train]
    dev_rows = [feature_fn(row) for row in dataset.dev]
    test_rows = [feature_fn(row) for row in dataset.test]
    train_labels = [row.label.value for row in dataset.train]
    dev_labels = [row.label.value for row in dataset.dev]

    scored: list[tuple[float, int, str, Any]] = []
    for spec in _experiment.model_specs():
        model = _experiment._estimator(spec)
        model.fit(train_rows, train_labels)
        dev_predictions = [str(value) for value in model.predict(dev_rows)]
        accuracy = sum(
            1 for gold, prediction in zip(dev_labels, dev_predictions, strict=True) if gold == prediction
        ) / len(dev_labels)
        scored.append((-accuracy, spec.complexity_rank, spec.config_id, spec))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    negative_accuracy, _rank, config_id, selected = scored[0]

    model = _experiment._estimator(selected)
    model.fit(train_rows, train_labels)
    predictions = tuple(str(value) for value in model.predict(test_rows))

    return ArmRun(
        dataset=dataset_id,
        arm_id=arm_id,
        config_id=config_id,
        dev_accuracy=-negative_accuracy,
        predictions=predictions,
        gold=tuple(row.label.value for row in dataset.test),
        train_features=_freeze_features(train_rows),
        dev_features=_freeze_features(dev_rows),
        test_features=_freeze_features(test_rows),
    )


def run_all_arms(datasets: Mapping[str, D1Dataset]) -> dict[str, dict[str, ArmRun]]:
    return {
        dataset_id: {
            arm_id: run_arm(dataset, dataset_id, arm_id, FEATURE_FUNCTIONS[arm_id])
            for arm_id in ARM_ORDER
        }
        for dataset_id, dataset in datasets.items()
    }


# ---------------------------------------------------------------------------
# Attack components
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AttackComponent:
    """One hostile component's three-valued verdict, with its denominator."""

    component_id: str
    hypothesis: str
    statement: str
    outcome: Outcome
    succeeded: bool
    denominator: str
    detail: str
    numbers: dict[str, Any]

    def __post_init__(self) -> None:
        if self.succeeded and self.outcome is not Outcome.FAIL:
            raise ValueError(
                f"{self.component_id}: a successful attack is a FAIL for the gate it attacks"
            )
        if self.outcome is Outcome.PASS and self.succeeded:
            raise ValueError(f"{self.component_id}: PASS cannot carry a successful attack")

    def as_json(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "hypothesis": self.hypothesis,
            "statement": self.statement,
            "outcome": self.outcome.value,
            "attack_succeeded": self.succeeded,
            "denominator": self.denominator,
            "detail": self.detail,
            "numbers": self.numbers,
        }


def sufficiency_component(
    *, component_id: str, challenger: ArmRun, typed: ArmRun, challenger_label: str
) -> AttackComponent:
    """`H_LEN`: does a length-only view reach the typed arm's accuracy?"""

    typed_accuracy = typed.accuracy
    challenger_accuracy = challenger.accuracy
    cases = len(typed.gold)
    response = challenger.response()
    floor = response.trivial_floor
    if cases == 0:
        return AttackComponent(
            component_id=component_id,
            hypothesis="H_LEN",
            statement=f"{challenger_label} reaches TYPED_RELATIONAL accuracy within one case",
            outcome=Outcome.CANNOT_CHECK,
            succeeded=False,
            denominator="0 protected cases",
            detail="no protected case was scored",
            numbers={},
        )
    succeeded = challenger_accuracy >= typed_accuracy - CASE_RESOLUTION
    explained = None
    if floor is not None and typed_accuracy > floor:
        explained = (challenger_accuracy - floor) / (typed_accuracy - floor)
    return AttackComponent(
        component_id=component_id,
        hypothesis="H_LEN",
        statement=f"{challenger_label} reaches TYPED_RELATIONAL accuracy within one case",
        outcome=Outcome.FAIL if succeeded else Outcome.PASS,
        succeeded=succeeded,
        denominator=f"{cases} protected cases",
        detail=(
            f"{challenger_label} {challenger_accuracy} vs TYPED_RELATIONAL {typed_accuracy} "
            f"(tolerance {CASE_RESOLUTION}); "
            + ("length reproduces the typed arm" if succeeded else "length does not reach it")
        ),
        numbers={
            "challenger_accuracy": challenger_accuracy,
            "typed_accuracy": typed_accuracy,
            "tolerance": CASE_RESOLUTION,
            "trivial_floor": floor,
            "challenger_distinct_predictions": response.distinct_predictions,
            "challenger_informedness": response.informedness,
            "fraction_of_typed_above_floor_reached_by_length": explained,
        },
    )


def equal_length_component(*, base_typed: ArmRun, control_typed: ArmRun) -> AttackComponent:
    """`H_LEN`: does the typed arm survive a cardinality-matched corruption?"""

    response = control_typed.response()
    floor = response.trivial_floor
    accuracy = control_typed.accuracy
    cases = len(control_typed.gold)
    if cases == 0 or floor is None:
        return AttackComponent(
            component_id="RL-3_EQUAL_LENGTH_CONTROL",
            hypothesis="H_LEN",
            statement="the typed arm collapses when corruption no longer changes cardinality",
            outcome=Outcome.CANNOT_CHECK,
            succeeded=False,
            denominator="0 protected cases",
            detail="the control split scored nothing",
            numbers={},
        )
    if accuracy <= floor:
        outcome, succeeded = Outcome.FAIL, True
        detail = (
            f"TYPED_RELATIONAL falls to {accuracy} on the equal-length control, at or below the "
            f"trivial floor {floor}: on this control its score is a label prior"
        )
    elif accuracy >= EQUAL_LENGTH_UNCHANGED_FLOOR:
        outcome, succeeded = Outcome.PASS, False
        detail = (
            f"TYPED_RELATIONAL holds {accuracy} on the equal-length control (base "
            f"{base_typed.accuracy}); removing the cardinality cue does not remove its decision"
        )
    else:
        outcome, succeeded = Outcome.CANNOT_CHECK, False
        detail = (
            f"TYPED_RELATIONAL scores {accuracy} on the equal-length control, between the trivial "
            f"floor {floor} and the unchanged bar {EQUAL_LENGTH_UNCHANGED_FLOOR}; a partial "
            "collapse is a partial explanation and this instrument cannot apportion it"
        )
    return AttackComponent(
        component_id="RL-3_EQUAL_LENGTH_CONTROL",
        hypothesis="H_LEN",
        statement="the typed arm collapses when corruption no longer changes cardinality",
        outcome=outcome,
        succeeded=succeeded,
        denominator=f"{cases} protected cases on the equal-length control",
        detail=detail,
        numbers={
            "base_typed_accuracy": base_typed.accuracy,
            "control_typed_accuracy": accuracy,
            "control_trivial_floor": floor,
            "unchanged_floor": EQUAL_LENGTH_UNCHANGED_FLOOR,
            "control_distinct_predictions": response.distinct_predictions,
            "control_informedness": response.informedness,
        },
    )


def reformat_component(
    *, component_id: str, typed: ArmRun, base_arm: ArmRun, reformatted: ArmRun
) -> AttackComponent:
    """`H_FMT`: does a pure reformat close the gap the relational operator is credited with?"""

    typed_accuracy = typed.accuracy
    base_gap = typed_accuracy - base_arm.accuracy
    reformat_gap = typed_accuracy - reformatted.accuracy
    response = reformatted.response()
    statement = (
        f"{reformatted.arm_id} closes at least half of the {base_arm.arm_id} gap to "
        "TYPED_RELATIONAL with no comparison operator and no added information"
    )
    if base_gap < REFORMAT_MIN_BASE_GAP:
        return AttackComponent(
            component_id=component_id,
            hypothesis="H_FMT",
            statement=statement,
            outcome=Outcome.CANNOT_CHECK,
            succeeded=False,
            denominator=f"base gap {base_gap} over {len(typed.gold)} protected cases",
            detail=(
                f"the {base_arm.arm_id} gap is {base_gap}, below the {REFORMAT_MIN_BASE_GAP} floor "
                "of four protected cases; halving it is not separable from tie-breaking noise"
            ),
            numbers={"base_gap": base_gap, "reformat_gap": reformat_gap},
        )
    if response.constant:
        return AttackComponent(
            component_id=component_id,
            hypothesis="H_FMT",
            statement=statement,
            outcome=Outcome.CANNOT_CHECK,
            succeeded=False,
            denominator=f"{response.departures} departures from its own modal answer",
            detail=(
                f"{reformatted.arm_id} answered "
                f"{response.prediction_counts[0][0]!r} on all {response.eval_cases} protected "
                "cases; a constant arm's accuracy is a label prior and cannot carry a reformat claim"
            ),
            numbers={
                "base_gap": base_gap,
                "reformat_gap": reformat_gap,
                "reformatted_accuracy": reformatted.accuracy,
            },
        )
    succeeded = reformat_gap <= REFORMAT_GAP_FRACTION * base_gap
    return AttackComponent(
        component_id=component_id,
        hypothesis="H_FMT",
        statement=statement,
        outcome=Outcome.FAIL if succeeded else Outcome.PASS,
        succeeded=succeeded,
        denominator=f"{response.departures} departures over {response.eval_cases} protected cases",
        detail=(
            f"{base_arm.arm_id} gap {base_gap} -> {reformatted.arm_id} gap {reformat_gap} "
            f"({REFORMAT_GAP_FRACTION} of the base gap is "
            f"{REFORMAT_GAP_FRACTION * base_gap}); "
            + (
                "a reformat alone accounts for most of the published gap"
                if succeeded
                else "the reformat does not account for the gap"
            )
        ),
        numbers={
            "typed_accuracy": typed_accuracy,
            "base_arm_accuracy": base_arm.accuracy,
            "reformatted_accuracy": reformatted.accuracy,
            "base_gap": base_gap,
            "reformat_gap": reformat_gap,
            "threshold_gap": REFORMAT_GAP_FRACTION * base_gap,
            "reformatted_distinct_predictions": response.distinct_predictions,
            "reformatted_informedness": response.informedness,
            "reformatted_departures": response.departures,
        },
    )


def invariance_component(
    *, component_id: str, hypothesis: str, transform: str, base: ArmRun, transformed: ArmRun
) -> AttackComponent:
    """`H_FMT`: does the arm read format, i.e. move under a meaning-preserving rewrite?

    The denominator is in the type. If the transform changed nothing the arm can
    see -- neither its protected features nor its training features -- the guard
    had no opportunity and the verdict is ``CANNOT_CHECK``, never "the attack
    failed".
    """

    train_changed = base.train_features != transformed.train_features
    dev_changed = base.dev_features != transformed.dev_features
    test_changed = sum(
        1
        for before, after in zip(base.test_features, transformed.test_features, strict=True)
        if before != after
    )
    if train_changed or dev_changed:
        opportunities = len(base.gold)
        opportunity_definition = (
            f"every protected case, because the {transform} transform changed the arm's fitted "
            "input and the model itself therefore differs"
        )
    else:
        opportunities = test_changed
        opportunity_definition = (
            f"protected cases whose input to {base.arm_id} changed under the {transform} transform"
        )
    violations = sum(
        1
        for before, after in zip(base.predictions, transformed.predictions, strict=True)
        if before != after
    )
    exercise = GuardExercise(
        guard_id=component_id,
        arm_id=base.arm_id,
        opportunities=opportunities,
        violations=violations,
        opportunity_definition=opportunity_definition,
    )
    assessment = assess_guard(exercise, max_violation_rate=MAX_ORBIT_VIOLATION_RATE)
    succeeded = assessment.outcome is Outcome.FAIL
    return AttackComponent(
        component_id=component_id,
        hypothesis=hypothesis,
        statement=(
            f"{base.arm_id}'s protected predictions move under the meaning-preserving "
            f"{transform} rewrite, so its score is partly a property of the format"
        ),
        outcome=assessment.outcome,
        succeeded=succeeded,
        denominator=f"{opportunities} opportunities ({opportunity_definition})",
        detail=assessment.detail,
        numbers={
            "train_features_changed": train_changed,
            "dev_features_changed": dev_changed,
            "protected_feature_dicts_changed": test_changed,
            "protected_predictions_changed": violations,
            "base_accuracy": base.accuracy,
            "transformed_accuracy": transformed.accuracy,
            "assessment": assessment.as_json(),
        },
    )


# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------

CONTRASTS: tuple[tuple[str, str], ...] = (
    ("typed_minus_transcript", ARM_TRANSCRIPT),
    ("typed_minus_same_information_serialized", ARM_SERIALIZED),
    ("typed_minus_untyped", ARM_UNTYPED),
)


def measure_contrasts(arms: Mapping[str, ArmRun]) -> dict[str, ContrastMargin]:
    treated = arms[ARM_TYPED].response()
    return {
        label: measure_contrast_margin(
            label, treated=treated, comparator=arms[comparator].response()
        )
        for label, comparator in CONTRASTS
    }


def run_campaign(repo_root: Path) -> dict[str, Any]:
    """Build every variant, check the preconditions, then run every attack."""

    payload: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "record": "P9_U_T4_HOSTILE_ATTACK_RESULT",
        "date": "2026-08-21",
        "gate_served": GATE_SERVED,
        "freeze_document": FREEZE_DOCUMENT,
        "parameters_sha256": frozen_digest(),
        "claim_scope": CLAIM_SCOPE,
        "environment_boundary": dict(ENVIRONMENT_BOUNDARY),
        "terminal_disposition": TERMINAL_DISPOSITION,
        "attacked_result": {
            "artifact": SHIPPED_D1_RESULT,
            "shipped_dataset_manifest_digest": SHIPPED_DATASET_MANIFEST_DIGEST,
        },
    }

    try:
        datasets = build_datasets()
    except (ValueError, KeyError) as error:
        payload["verdict"] = VERDICT_CONSTRUCTION_FAILED
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["preconditions"] = {
            "CONSTRUCTION": {
                "passed": False,
                "detail": f"a dataset variant could not be built: {error}",
            }
        }
        payload["detail"] = (
            "the variants failed closed during construction, before any arm ran. D1Instance.verify "
            "recomputes the exact gold classifier on every transformed pair, so a transform that "
            "moved a label cannot reach an arm."
        )
        payload["arms"] = {}
        payload["components"] = []
        return payload
    preconditions = check_preconditions(datasets)
    payload["preconditions"] = preconditions
    if not all(item["passed"] for item in preconditions.values()):
        payload["verdict"] = VERDICT_CONSTRUCTION_FAILED
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = (
            "a construction precondition failed, so the variants are not the ones the freeze "
            "specifies. No arm accuracy is reported over them."
        )
        payload["arms"] = {}
        payload["components"] = []
        return payload

    runs = run_all_arms(datasets)
    payload["arms"] = {
        dataset_id: {
            arm_id: {
                "config_id": run.config_id,
                "dev_accuracy": run.dev_accuracy,
                **run.response().as_json(),
            }
            for arm_id, run in sorted(arms.items())
        }
        for dataset_id, arms in sorted(runs.items())
    }

    base = runs[DATASET_BASE]
    contrasts = measure_contrasts(base)
    payload["contrasts"] = {label: margin.as_json() for label, margin in contrasts.items()}
    eligible = [label for label, margin in contrasts.items() if margin.outcome is Outcome.PASS]
    payload["contrast_eligibility"] = {
        "eligible_for_attack": eligible,
        "not_eligible": {
            label: margin.reason.value
            for label, margin in contrasts.items()
            if margin.outcome is not Outcome.PASS
        },
        "rule": (
            "an attack cannot fail against a margin that was never measured; a contrast whose "
            "comparator answered with one label is CANNOT_CHECK for the attack as well"
        ),
    }

    if not eligible:
        payload["verdict"] = VERDICT_NO_MEASURABLE_CONTRAST
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = (
            "no D1 contrast has a comparator that answered, so there is no measured effect for a "
            "hostile alternative to explain and none to be refuted by"
        )
        payload["components"] = []
        return payload

    components: list[AttackComponent] = [
        sufficiency_component(
            component_id="RL-1_LENGTH_ONLY_SUFFICIENT",
            challenger=base[ARM_LENGTH_ONLY],
            typed=base[ARM_TYPED],
            challenger_label=ARM_LENGTH_ONLY,
        ),
        sufficiency_component(
            component_id="RL-2_LENGTH_RELATIONAL_SUFFICIENT",
            challenger=base[ARM_LENGTH_RELATIONAL],
            typed=base[ARM_TYPED],
            challenger_label=ARM_LENGTH_RELATIONAL,
        ),
        equal_length_component(
            base_typed=base[ARM_TYPED],
            control_typed=runs[DATASET_EQUAL_LENGTH][ARM_TYPED],
        ),
        reformat_component(
            component_id="FP-1a_INDEXED_REFORMAT_CLOSES_GAP",
            typed=base[ARM_TYPED],
            base_arm=base[ARM_SERIALIZED],
            reformatted=base[ARM_SERIALIZED_INDEXED],
        ),
        reformat_component(
            component_id="FP-1b_PATHONLY_REFORMAT_CLOSES_GAP",
            typed=base[ARM_TYPED],
            base_arm=base[ARM_SERIALIZED],
            reformatted=base[ARM_SERIALIZED_PATHONLY],
        ),
    ]
    for arm_id in ARM_ORDER:
        components.append(
            invariance_component(
                component_id=f"FP-2_SEMANTIC_ORBIT_INVARIANCE::{arm_id}",
                hypothesis="H_FMT",
                transform="symbol-remint semantic orbit",
                base=base[arm_id],
                transformed=runs[DATASET_ORBIT][arm_id],
            )
        )
    for arm_id in ARM_ORDER:
        components.append(
            invariance_component(
                component_id=f"FP-3_ORDER_REMINT_INVARIANCE::{arm_id}",
                hypothesis="H_FMT",
                transform="sequence-order remint",
                base=base[arm_id],
                transformed=runs[DATASET_ORDER][arm_id],
            )
        )

    payload["components"] = [item.as_json() for item in components]
    succeeded = [item for item in components if item.succeeded]
    unexercised = [item for item in components if item.outcome is Outcome.CANNOT_CHECK]
    payload["component_census"] = {
        "components": len(components),
        "attacks_succeeded": len(succeeded),
        "components_cannot_check": len(unexercised),
        "succeeded_ids": [item.component_id for item in succeeded],
        "cannot_check_ids": [item.component_id for item in unexercised],
    }

    if succeeded:
        payload["verdict"] = VERDICT_ATTACK_SUCCEEDED
        payload["outcome"] = Outcome.FAIL.value
        payload["detail"] = (
            f"{len(succeeded)} hostile components succeeded against D1: "
            + "; ".join(item.detail for item in succeeded)
        )
        return payload
    if unexercised:
        payload["verdict"] = VERDICT_ATTACKS_UNEXERCISED
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = (
            f"no component succeeded, but {len(unexercised)} had no denominator to succeed on: "
            + "; ".join(item.component_id for item in unexercised)
        )
        return payload
    payload["verdict"] = VERDICT_ATTACKS_DID_NOT_SUCCEED
    payload["outcome"] = Outcome.PASS.value
    payload["detail"] = (
        f"all {len(components)} hostile components ran with a non-zero denominator and none "
        "succeeded against the D1 contrasts that were measurable"
    )
    return payload


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run P9's representation-length and format-prior attacks against D1 (P9-U-T4)."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--print-digest",
        action="store_true",
        help="print the runner's frozen parameter digest and exit without running",
    )
    parser.add_argument(
        "--skip-twin-check",
        action="store_true",
        help="skip the freeze-twin digest check (only for minting the twin)",
    )
    args = parser.parse_args(list(argv))

    if args.print_digest:
        print(frozen_digest())
        return 0

    if not args.skip_twin_check:
        verify_against_twin(args.repo_root)

    payload = run_campaign(args.repo_root)
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")

    outcome = Outcome(payload["outcome"])
    if outcome is Outcome.PASS:
        return 0
    return 3 if outcome is Outcome.FAIL else 4


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(__import__("sys").argv[1:]))


__all__ = [
    "ARM_LENGTH_ONLY",
    "ARM_LENGTH_RELATIONAL",
    "ARM_ORDER",
    "ARM_SERIALIZED",
    "ARM_SERIALIZED_INDEXED",
    "ARM_SERIALIZED_PATHONLY",
    "ARM_TRANSCRIPT",
    "ARM_TYPED",
    "ARM_UNTYPED",
    "CASE_RESOLUTION",
    "CLAIM_SCOPE",
    "DATASET_BASE",
    "DATASET_EQUAL_LENGTH",
    "DATASET_ORBIT",
    "DATASET_ORDER",
    "FREEZE_DOCUMENT",
    "FREEZE_TWIN",
    "FROZEN_PARAMETERS",
    "SHIPPED_DATASET_MANIFEST_DIGEST",
    "VERDICT_ATTACKS_DID_NOT_SUCCEED",
    "VERDICT_ATTACKS_UNEXERCISED",
    "VERDICT_ATTACK_SUCCEEDED",
    "VERDICT_CONSTRUCTION_FAILED",
    "VERDICT_NO_MEASURABLE_CONTRAST",
    "ArmRun",
    "AttackComponent",
    "FreezeViolation",
    "build_datasets",
    "build_orbit_map",
    "check_preconditions",
    "decode_typed_serialization",
    "equal_length_component",
    "equal_length_mutated_value",
    "frozen_digest",
    "index_serialization",
    "invariance_component",
    "length_only_features",
    "length_relational_features",
    "main",
    "measure_contrasts",
    "pathonly_serialization",
    "reformat_component",
    "restore_serialization",
    "run_all_arms",
    "run_arm",
    "run_campaign",
    "serialized_indexed_features",
    "serialized_pathonly_features",
    "serialized_tokens",
    "string_atoms",
    "sufficiency_component",
    "verify_against_twin",
]
