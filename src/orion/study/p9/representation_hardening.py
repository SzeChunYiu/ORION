"""NR-05: representation hardening of the serialized arm against the frozen format-prior attack class.

The frozen T4 campaign (``papers/orion-19-structured-epistemic-learning/
evidence/P9_U_T3_T4_HOSTILE_ATTACK_RECEIPT_2026-08-21.md``) defeated one narrow
representation claim: the format-prior component ``FP-2`` moved 32 of 128
protected answers of ``TYPED_SERIALIZED_BAG`` under one bijective renaming of
the value alphabet, so the manuscript sentence about explicit relational
comparison making those fields more useful cannot rest on the
typed-minus-serialized margin.

**Root cause, attributed to one stage.** The serialized arm's *feature map*
emits value-identity keys (``token:root.left.preconditions[]=<atom>``).
``DictVectorizer`` orders columns by the alphabetical sort of key strings and
drops out-of-vocabulary keys, and the frozen grid's tree and random-forest
learners -- and the ``(-dev_accuracy, ...)`` selection -- break ties as a
function of column order. A bijective renaming of the train atoms re-rolls that
order and thereby re-rolls the fitted function; the protected split is a
held-out *domain* that shares zero value atoms with train, so its answers ride
on structural tokens plus the train-side fit and move with it. The property the
attack exploits is the absence of a canonical form quotienting the atom
alphabet by its renaming group. The six arms whose features are functions of
equality, presence and cardinality are orbit-invariant for exactly this reason;
the serialized arm is the one arm that names values, and it is the one arm that
moved.

**The lever.** ``SERIALIZED_CANONICAL``: the serialized token bag with every
string leaf value replaced by the canonical symbol of its occurrence-footprint
class. The footprint of an atom is the sorted multiset of
``{split}:{index}:{path}`` entries over every occurrence of that atom in the
corpus's serialized streams. Renaming moves no occurrence -- positions, splits
and paths are untouched, and the rebuild's sorted-set normalization permutes
element order within a coordinate but cannot change the multiset of
(position, path) occurrences -- so footprint(v(a)) = footprint(a) for every
bijection v, hence sigma(v(a)) = sigma(a), hence the canonical stream of the
transformed corpus is byte-identical to that of the base corpus, hence the
fitted model is the same object. The hardened feature map factors through the
quotient of the value alphabet by its renaming group: the frozen attack class
is not merely survived, it is unrepresentable in the hardened feature space.

**Impossibility boundary, stated before the run.** No orbit-invariant
canonical form can separate atoms with identical occurrence footprints; any
separating rule must read the value itself and is orbit-sensitive. The quotient
therefore merges atoms that are provably always co-present (identical
footprints imply identical presence in every row), which no row's key-pattern
can distinguish. V2-PC-4 measures the co-presence, V2-PC-5 reports the round
trip in quotient form: singleton classes restore byte-exactly, multi-member
classes restore to the exact class set.

**Honest measurement.** The frozen ``FP-2`` instrument reads structural
invariance as ``CANNOT_CHECK`` (its denominator sits after the feature map), so
this study registers its own guard C-1 whose denominator sits *before*
canonicalization: opportunities are corpus instances whose raw serialized
stream changed under a registered bijection -- the attack demonstrably reached
the representation -- and violations are instances whose canonicalized stream
changed. Two positive controls validate the instrument itself (C-2): the frozen
``FP-2`` must still reproduce its FAIL on ``TYPED_SERIALIZED_BAG``, and the
C-1 guard must still flag ``SERIALIZED_INDEXED``, whose per-instance sorted-value
indexing is a canonicalization design that does not annihilate the orbit. If
either control fails to fire the instrument is invalid and the run certifies
nothing.

Protocol: ``papers/orion-19-structured-epistemic-learning/protocol/
P9_NR05_REPRESENTATION_HARDENING_FREEZE_2026-08-23.md`` and its JSON twin. The
runner recomputes the twin's parameter digest from its own constants and
refuses to run on a mismatch, and it reports no arm number at all if a
construction precondition fails.

Claim scope is ``BOUNDED_D1_ONLY`` and ``P9-U-T4`` stays BLOCKED whatever this
returns; the protected negative ``LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED``
is out of scope and untouched. Nothing here edits a frozen P9 result, receipt,
protocol or evidence artifact: the frozen T4 instrument is imported, never
edited.

Run it::

    python -m orion.study.p9.representation_hardening --repo-root . \
        --output <result>.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from contextlib import nullcontext
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from orion.programme.comparator_response import measure_contrast_margin, score_comparator
from orion.programme.guard_exercise import GuardExercise, assess_guard
from orion.programme.records import Outcome
from orion.transfer.v2.canonical import content_digest

from . import d1 as _d1
from . import d1_runtime as _runtime  # noqa: F401  (installs the v1.2 execution adapters)
from . import hostile_representation_attacks as hra
from .d1 import D1Dataset, D1Instance

RESULT_SCHEMA_VERSION = "orion.p9.nr05-representation-hardening-result.v1"

FREEZE_DOCUMENT = (
    "papers/orion-19-structured-epistemic-learning/protocol/"
    "P9_NR05_REPRESENTATION_HARDENING_FREEZE_2026-08-23.md"
)
FREEZE_TWIN = (
    "papers/orion-19-structured-epistemic-learning/protocol/"
    "P9_NR05_REPRESENTATION_HARDENING_FREEZE_2026-08-23.json"
)

REVIVAL_LANE = "NR-05"
RESULT_DATE = "2026-08-23"

NEGATIVE_REVIVED = (
    "T4_ATTACK_SUCCEEDED: the frozen format-prior component FP-2 landed on "
    "TYPED_SERIALIZED_BAG (32 of 128 protected answers moved under one bijective renaming "
    "of the value alphabet), narrowing the typed-minus-serialized margin"
)

ROOT_CAUSE_STAGE = (
    "representation stage: the serialized arm's feature map emits value-identity keys, and "
    "the frozen learner stack makes the fitted function a function of vocabulary order "
    "(alphabetical DictVectorizer columns, tree/RF tie-breaking, OOV key dropping on a "
    "held-out domain sharing zero value atoms with train)"
)

LEVER = (
    "footprint-class quotient canonicalization: replace every string leaf value by the "
    "canonical symbol of its occurrence-footprint class, computed corpus-wide; the hardened "
    "feature map factors through the quotient of the value alphabet by its renaming group"
)

PROTECTED_NEGATIVE_UNTOUCHED = (
    "LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED is a different claim under a different "
    "receipt's authority boundary; this study does not touch, re-run or repair it and uses "
    "no language model"
)

# --- frozen constants (hashed into the twin) -------------------------------

CANONICAL_SALT = "p9-nr05-canonical-2026-08-23"
CANONICAL_PREFIX = "#"
CANONICAL_WIDTH = 12

BIJECTION_SALTS: dict[str, str] = {
    "BIJECTION_1": "p9-nr05-bijection-2026-08-23|1",
    "BIJECTION_2": "p9-nr05-bijection-2026-08-23|2",
    "BIJECTION_3": "p9-nr05-bijection-2026-08-23|3",
}

ORBIT_FROZEN_ID = "ORBIT_FROZEN"
BIJECTION_ORDER: tuple[str, ...] = (ORBIT_FROZEN_ID, *BIJECTION_SALTS)

ARM_CANONICAL = "SERIALIZED_CANONICAL"
STUDY_ARMS: tuple[str, ...] = (
    hra.ARM_TYPED,
    hra.ARM_SERIALIZED,
    hra.ARM_SERIALIZED_INDEXED,
    ARM_CANONICAL,
)

CANONICAL_RESPONSE_DEFINITION = (
    "the same canonical path=value token bag as TYPED_SERIALIZED_BAG with every string "
    "leaf value replaced by the corpus-wide occurrence-footprint class symbol of its atom; "
    "a quotient by the renaming group, with no comparison operator added"
)

VERDICT_CONSTRUCTION_FAILED = "T4V2_CONSTRUCTION_FAILED"
VERDICT_GUARD_INVALID = "T4V2_GUARD_INVALID"
VERDICT_INVARIANCE_BROKEN = "T4V2_INVARIANCE_BROKEN"
VERDICT_MARGIN_NOT_SUPPORTED = "T4V2_MARGIN_NOT_SUPPORTED"
VERDICT_MARGIN_UNMEASURABLE = "T4V2_MARGIN_UNMEASURABLE"
VERDICT_HARDENED = "T4V2_REPRESENTATION_HARDENED_ON_D1"

FROZEN_PARAMETERS: dict[str, Any] = {
    "record": "P9_NR05_REPRESENTATION_HARDENING_FREEZE",
    "freeze_document": FREEZE_DOCUMENT,
    "revival_lane": REVIVAL_LANE,
    "negative_revived": NEGATIVE_REVIVED,
    "root_cause_stage": ROOT_CAUSE_STAGE,
    "lever": LEVER,
    "claim_scope": hra.CLAIM_SCOPE,
    "terminal_disposition": hra.TERMINAL_DISPOSITION,
    "protected_negative_untouched": PROTECTED_NEGATIVE_UNTOUCHED,
    "attacked_result": {
        "artifact": hra.SHIPPED_D1_RESULT,
        "dataset_manifest_digest": hra.SHIPPED_DATASET_MANIFEST_DIGEST,
        "seed": hra.D1_SEED,
        "protected_cases": hra.PROTECTED_CASES,
        "frozen_fp2_violations_on_serialized_bag": 32,
        "frozen_fp2_opportunities": hra.PROTECTED_CASES,
    },
    "canonical": {
        "salt": CANONICAL_SALT,
        "prefix": CANONICAL_PREFIX,
        "width": CANONICAL_WIDTH,
        "footprint_entry_format": "{split}:{index_within_split}:{token_path}",
        "footprint_scope": "corpus-wide, canonical traversal train then dev then test, instances in stored split order",
        "symbol_rule": "prefix + sha256(salt + '|' + ';'.join(sorted footprint multiset))[:width]; atoms with identical footprints share one symbol",
        "atoms_rule": "the frozen string_atoms rule: LEN markers, <NONE> markers and integer leaves are structure, not values",
    },
    "arms": list(STUDY_ARMS),
    "bijections": {
        "frozen_orbit": hra.ORBIT_SALT,
        "fresh_draws": dict(BIJECTION_SALTS),
        "construction": "identical to build_orbit_map: v_ prefix, sha256, width 12, applied to the frozen REMINTED_COORDINATES, injectivity checked",
        "class": "one global bijection on the value alphabet (the frozen T4 attack class); no new attack type",
    },
    "thresholds": {
        "case_resolution": hra.CASE_RESOLUTION,
        "reformat_gap_fraction": hra.REFORMAT_GAP_FRACTION,
        "reformat_min_base_gap": hra.REFORMAT_MIN_BASE_GAP,
        "max_violation_rate": hra.MAX_ORBIT_VIOLATION_RATE,
        "inherited_from": "the frozen T4 parameter block, verbatim",
    },
    "preconditions": [
        "V2-PC-1 DATASET FIDELITY: the regenerated dataset reproduces the shipped manifest digest",
        "V2-PC-2 GOLD PRESERVATION: every bijection variant reproduces every gold label, position for position (512 per variant)",
        "V2-PC-3 BIJECTIVITY OF EVERY REMINT: each registered bijection is injective on the atom alphabet",
        "V2-PC-4 QUOTIENT CO-PRESENCE: every multi-member footprint class has identical per-member occurrence multisets (recomputed) and no partial presence anywhere in the corpus",
        "V2-PC-5 ROUND TRIP IN QUOTIENT FORM: singleton-class tokens restore byte-exactly via the per-corpus class table; class tokens restore to the exact class; counts reported over all 512 instances",
        "V2-PC-6 LABEL VARIETY: the protected split's gold takes more than one value",
    ],
    "components": {
        "C-1_QUOTIENT_INVARIANCE": (
            "opportunities = corpus instances whose raw serialized stream changed under a "
            "registered bijection; violations = instances whose canonicalized stream changed; "
            "GuardExercise pooled over the four bijections at max_violation_rate 0.0; the refit "
            "consequence (identical config, train features, protected predictions, accuracy) is "
            "recorded alongside"
        ),
        "C-2_POSITIVE_CONTROLS": (
            "(i) the frozen FP-2 component re-run verbatim on TYPED_SERIALIZED_BAG under the "
            "frozen orbit must reproduce FAIL; (ii) the C-1 guard applied to SERIALIZED_INDEXED "
            "under the frozen orbit must flag it; if either does not fire the instrument is invalid"
        ),
        "C-3_MARGIN_SURVIVAL": (
            "on BASE: g = acc(TYPED_RELATIONAL) - acc(TYPED_SERIALIZED_BAG), gc = "
            "acc(TYPED_RELATIONAL) - acc(SERIALIZED_CANONICAL); supported iff the canonical arm "
            "is non-constant, measure_contrast_margin passes, g >= 4 cases and gc > 0.5 * g"
        ),
        "C-4_FROZEN_FP2_READING": (
            "the frozen FP-2 component verbatim on SERIALIZED_CANONICAL under the frozen orbit; "
            "expected CANNOT_CHECK / NEVER_EXERCISED by structural invariance, recorded as "
            "exactly that and never as a pass"
        ),
    },
    "verdicts": {
        "construction_failed": VERDICT_CONSTRUCTION_FAILED,
        "guard_invalid": VERDICT_GUARD_INVALID,
        "invariance_broken": VERDICT_INVARIANCE_BROKEN,
        "margin_not_supported": VERDICT_MARGIN_NOT_SUPPORTED,
        "margin_unmeasurable": VERDICT_MARGIN_UNMEASURABLE,
        "hardened": VERDICT_HARDENED,
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
# Quotient canonicalization
# ---------------------------------------------------------------------------

SPLIT_ORDER: tuple[str, ...] = ("train", "dev", "test")


def _is_atom_token(path: str, value: str) -> bool:
    """The frozen atom rule, asked of one token: structure is not a value."""

    if path.endswith(hra.LEN_MARKER[:-1]):
        return False
    if value == hra.NONE_MARKER:
        return False
    if value.lstrip("-").isdigit():
        return False
    return True


@dataclass(frozen=True)
class FootprintClass:
    """One equivalence class of the quotient: atoms with identical footprints."""

    symbol: str
    footprint_key: str
    atoms: tuple[str, ...]

    @property
    def is_singleton(self) -> bool:
        return len(self.atoms) == 1


@dataclass(frozen=True)
class QuotientTable:
    """The per-corpus canonical table: classes, symbol lookup and inverse."""

    classes: tuple[FootprintClass, ...]
    symbol_of: dict[str, str]
    class_by_symbol: dict[str, FootprintClass]

    @property
    def multi_member_classes(self) -> tuple[FootprintClass, ...]:
        return tuple(cls for cls in self.classes if not cls.is_singleton)


def dataset_streams(dataset: D1Dataset) -> dict[tuple[str, int], tuple[str, ...]]:
    """Every instance's serialized token stream, keyed by canonical position."""

    streams: dict[tuple[str, int], tuple[str, ...]] = {}
    for split in SPLIT_ORDER:
        for index, instance in enumerate(getattr(dataset, split)):
            streams[(split, index)] = hra.serialized_tokens(instance)
    return streams


def build_quotient_table(dataset: D1Dataset) -> QuotientTable:
    """Compute the occurrence-footprint classes of one corpus and its symbols."""

    occurrences: dict[str, list[str]] = defaultdict(list)
    for split in SPLIT_ORDER:
        for index, instance in enumerate(getattr(dataset, split)):
            for token in hra.serialized_tokens(instance):
                path, value = hra.split_token(token)
                if _is_atom_token(path, value):
                    occurrences[value].append(f"{split}:{index}:{path}")
    by_footprint: dict[str, list[str]] = defaultdict(list)
    for atom, entries in occurrences.items():
        by_footprint[";".join(sorted(entries))].append(atom)
    classes: list[FootprintClass] = []
    symbol_of: dict[str, str] = {}
    class_by_symbol: dict[str, FootprintClass] = {}
    for footprint_key, atoms in sorted(by_footprint.items()):
        digest = sha256(f"{CANONICAL_SALT}|{footprint_key}".encode("utf-8")).hexdigest()
        symbol = CANONICAL_PREFIX + digest[:CANONICAL_WIDTH]
        cls = FootprintClass(symbol=symbol, footprint_key=footprint_key, atoms=tuple(sorted(atoms)))
        classes.append(cls)
        class_by_symbol[symbol] = cls
        for atom in cls.atoms:
            symbol_of[atom] = symbol
    if len(class_by_symbol) != len(classes):
        raise ValueError("canonical symbol collision between footprint classes")
    return QuotientTable(
        classes=tuple(classes), symbol_of=symbol_of, class_by_symbol=class_by_symbol
    )


def canonicalize_tokens(
    tokens: Sequence[str], symbol_of: Mapping[str, str]
) -> tuple[str, ...]:
    """Replace every string leaf value by the canonical symbol of its class."""

    out: list[str] = []
    for token in tokens:
        path, value = hra.split_token(token)
        symbol = symbol_of.get(value)
        out.append(f"{path}={symbol}" if symbol is not None else token)
    return tuple(out)


def canonical_feature_fn(
    symbol_of: Mapping[str, str]
) -> Callable[[D1Instance], dict[str, object]]:
    """The hardened arm: the frozen serialized bag over canonical tokens."""

    def features(instance: D1Instance) -> dict[str, object]:
        return hra._bag(canonicalize_tokens(hra.serialized_tokens(instance), symbol_of))

    return features


# ---------------------------------------------------------------------------
# Registered bijections (instances of the frozen attack class only)
# ---------------------------------------------------------------------------


def build_bijection_map(dataset: D1Dataset, salt: str) -> dict[str, str]:
    """One global bijection on the value alphabet, checked injective.

    The construction is the frozen orbit's (prefix, sha256, width, reminted
    coordinates) with this study's registered salt; the frozen orbit itself is
    obtained by calling the frozen ``build_orbit_map`` verbatim.
    """

    mapping = {
        atom: hra.ORBIT_PREFIX
        + sha256(f"{salt}|{atom}".encode("utf-8")).hexdigest()[:hra.ORBIT_WIDTH]
        for atom in hra._dataset_atoms(dataset)
    }
    if len(set(mapping.values())) != len(mapping):
        raise ValueError(f"bijection {salt} is not injective on the atom alphabet")
    return mapping


def build_study_datasets() -> tuple[D1Dataset, dict[str, D1Dataset]]:
    """The frozen base, the frozen orbit, and the three fresh bijection variants."""

    frozen = hra.build_datasets()
    base = frozen[hra.DATASET_BASE]
    variants: dict[str, D1Dataset] = {ORBIT_FROZEN_ID: frozen[hra.DATASET_ORBIT]}
    for name, salt in BIJECTION_SALTS.items():
        mapping = build_bijection_map(base, salt)
        variants[name] = hra._transform_dataset(
            base, lambda method, mapping=mapping: hra._orbit_method(method, mapping)
        )
    return base, variants

# ---------------------------------------------------------------------------
# V2 preconditions
# ---------------------------------------------------------------------------


def check_v2_preconditions(
    base: D1Dataset,
    variants: Mapping[str, D1Dataset],
    bijections: Mapping[str, Mapping[str, str]],
    quotient: QuotientTable,
) -> dict[str, Any]:
    """Every construction check, run before a single arm of this study is fitted."""

    base_streams = dataset_streams(base)
    checks: dict[str, Any] = {}

    checks["V2-PC-1_DATASET_FIDELITY"] = {
        "passed": base.manifest_digest == hra.SHIPPED_DATASET_MANIFEST_DIGEST,
        "expected": hra.SHIPPED_DATASET_MANIFEST_DIGEST,
        "observed": base.manifest_digest,
        "detail": "the regenerated dataset must be the one P9 shipped, not a local lookalike",
    }

    gold_rows = []
    for name in BIJECTION_ORDER:
        variant = variants[name]
        changed = 0
        compared = 0
        for split in SPLIT_ORDER:
            for original, derived in zip(
                getattr(base, split), getattr(variant, split), strict=True
            ):
                compared += 1
                if original.label is not derived.label:
                    changed += 1
                if _d1.classify_methods(derived.left, derived.right) is not derived.label:
                    changed += 1
        gold_rows.append(
            {"variant": name, "instances_compared": compared, "labels_changed": changed}
        )
    checks["V2-PC-2_GOLD_PRESERVATION"] = {
        "passed": all(row["labels_changed"] == 0 for row in gold_rows)
        and all(row["instances_compared"] > 0 for row in gold_rows),
        "rows": gold_rows,
        "detail": "a bijection that moves a label is a different benchmark, not a control",
    }

    bijection_rows = [
        {
            "bijection": name,
            "atoms": len(mapping),
            "distinct_images": len(set(mapping.values())),
        }
        for name, mapping in bijections.items()
    ]
    checks["V2-PC-3_BIJECTIVITY_OF_EVERY_REMINT"] = {
        "passed": all(
            row["atoms"] > 0 and row["atoms"] == row["distinct_images"]
            for row in bijection_rows
        ),
        "rows": bijection_rows,
        "detail": "a non-injective remint destroys information and is not an orbit bijection",
    }

    multi_atoms = {atom for cls in quotient.multi_member_classes for atom in cls.atoms}
    occurrences: dict[str, list[str]] = defaultdict(list)
    member_presence: dict[tuple[str, int], set[str]] = {}
    for key, stream in base_streams.items():
        present: set[str] = set()
        for token in stream:
            path, value = hra.split_token(token)
            if not _is_atom_token(path, value):
                continue
            occurrences[value].append(f"{key[0]}:{key[1]}:{path}")
            if value in multi_atoms:
                present.add(value)
        if present:
            member_presence[key] = present
    footprint_mismatches = 0
    for cls in quotient.multi_member_classes:
        reference = sorted(occurrences[cls.atoms[0]])
        for atom in cls.atoms[1:]:
            if sorted(occurrences[atom]) != reference:
                footprint_mismatches += 1
    partial_presence = 0
    for cls in quotient.multi_member_classes:
        members = set(cls.atoms)
        for present in member_presence.values():
            overlap = present & members
            if overlap and overlap != members:
                partial_presence += 1
    checks["V2-PC-4_QUOTIENT_CO_PRESENCE"] = {
        "passed": footprint_mismatches == 0 and partial_presence == 0,
        "multi_member_classes": len(quotient.multi_member_classes),
        "member_footprint_mismatches": footprint_mismatches,
        "partial_presence_instances": partial_presence,
        "class_sizes": sorted(len(cls.atoms) for cls in quotient.multi_member_classes),
        "detail": (
            "the quotient merges only atoms whose bag keys are provably always co-present; "
            "any partial presence would make the merge lossy for some row"
        ),
    }

    instances_checked = 0
    tokens_checked = 0
    singleton_restores_exact = 0
    class_member_restores = 0
    structure_tokens_untouched = 0
    for key, raw in base_streams.items():
        instances_checked += 1
        canon = canonicalize_tokens(raw, quotient.symbol_of)
        for raw_token, canon_token in zip(raw, canon, strict=True):
            tokens_checked += 1
            raw_path, raw_value = hra.split_token(raw_token)
            canon_path, canon_value = hra.split_token(canon_token)
            cls = quotient.class_by_symbol.get(canon_value)
            if cls is None:
                structure_tokens_untouched += int(raw_token == canon_token)
            elif cls.is_singleton:
                singleton_restores_exact += int(
                    raw_value == cls.atoms[0] and raw_path == canon_path
                )
            else:
                class_member_restores += int(
                    raw_value in cls.atoms and raw_path == canon_path
                )
    restore_failures = tokens_checked - (
        singleton_restores_exact + class_member_restores + structure_tokens_untouched
    )
    checks["V2-PC-5_ROUND_TRIP_IN_QUOTIENT_FORM"] = {
        "passed": restore_failures == 0 and instances_checked > 0,
        "instances_checked": instances_checked,
        "tokens_checked": tokens_checked,
        "singleton_class_tokens_restored_byte_exact": singleton_restores_exact,
        "multi_member_class_tokens_restored_to_exact_class": class_member_restores,
        "structure_tokens_untouched": structure_tokens_untouched,
        "restore_failures": restore_failures,
        "detail": (
            "the disclosed information boundary: singleton classes restore byte-exactly, "
            "multi-member classes restore to the exact class set, structure tokens are untouched"
        ),
    }

    labels = {instance.label.value for instance in base.test}
    checks["V2-PC-6_LABEL_VARIETY"] = {
        "passed": len(labels) > 1,
        "protected_cases": len(base.test),
        "distinct_gold_labels": sorted(labels),
        "detail": "a split whose gold never varies cannot separate any two arms",
    }

    return checks


def quotient_table_stats(quotient: QuotientTable, base: D1Dataset) -> dict[str, Any]:
    """The construction census of the quotient, recomputed and recorded."""

    protected_atoms = set()
    for instance in base.test:
        for token in hra.serialized_tokens(instance):
            path, value = hra.split_token(token)
            if _is_atom_token(path, value):
                protected_atoms.add(value)
    protected_class_sizes = sorted(
        len(quotient.class_by_symbol[quotient.symbol_of[atom]].atoms)
        for atom in protected_atoms
    )
    return {
        "atoms": len(quotient.symbol_of),
        "classes": len(quotient.classes),
        "multi_member_classes": [
            {"symbol": cls.symbol, "atoms": list(cls.atoms)} for cls in quotient.multi_member_classes
        ],
        "protected_atoms": len(protected_atoms),
        "protected_class_sizes_all_singleton": all(size == 1 for size in protected_class_sizes),
    }


# ---------------------------------------------------------------------------
# C-1: the quotient-invariance guard, denominator before canonicalization
# ---------------------------------------------------------------------------


def quotient_invariance_component(
    *,
    base: D1Dataset,
    variants: Mapping[str, D1Dataset],
    canonical_runs: Mapping[str, hra.ArmRun],
    base_canonical_run: hra.ArmRun,
) -> hra.AttackComponent:
    """C-1: the hardened representation must not move under any registered bijection."""

    base_streams = dataset_streams(base)
    base_table = build_quotient_table(base)
    base_canonical = {
        key: canonicalize_tokens(stream, base_table.symbol_of)
        for key, stream in base_streams.items()
    }
    per_bijection: list[dict[str, Any]] = []
    pooled_opportunities = 0
    pooled_violations = 0
    stray_canonical_changes = 0
    for name in BIJECTION_ORDER:
        variant_streams = dataset_streams(variants[name])
        variant_table = build_quotient_table(variants[name])
        opportunities = 0
        violations = 0
        stray = 0
        for key, stream in variant_streams.items():
            raw_changed = stream != base_streams[key]
            canon_changed = (
                canonicalize_tokens(stream, variant_table.symbol_of) != base_canonical[key]
            )
            if raw_changed:
                opportunities += 1
                violations += int(canon_changed)
            elif canon_changed:
                stray += 1
        variant_run = canonical_runs[name]
        refit = {
            "config_id_identical": variant_run.config_id == base_canonical_run.config_id,
            "train_features_identical": variant_run.train_features == base_canonical_run.train_features,
            "dev_features_identical": variant_run.dev_features == base_canonical_run.dev_features,
            "test_features_identical": variant_run.test_features == base_canonical_run.test_features,
            "protected_predictions_identical": variant_run.predictions == base_canonical_run.predictions,
            "accuracy_identical": variant_run.accuracy == base_canonical_run.accuracy,
        }
        per_bijection.append(
            {
                "bijection": name,
                "instances_compared": len(variant_streams),
                "raw_stream_changed": opportunities,
                "canonical_stream_changed_among_those": violations,
                "canonical_stream_changed_outside_opportunities": stray,
                "refit_consequence": refit,
            }
        )
        pooled_opportunities += opportunities
        pooled_violations += violations
        stray_canonical_changes += stray

    opportunity_definition = (
        "corpus instances (512 per bijection) whose raw serialized stream changed under a "
        "registered bijection, pooled over the four registered bijections; violations are "
        "instances of those whose canonicalized stream changed"
    )
    exercise = GuardExercise(
        guard_id="C-1_QUOTIENT_INVARIANCE",
        arm_id=ARM_CANONICAL,
        opportunities=pooled_opportunities,
        violations=pooled_violations,
        opportunity_definition=opportunity_definition,
    )
    assessment = assess_guard(exercise, max_violation_rate=hra.MAX_ORBIT_VIOLATION_RATE)
    if stray_canonical_changes:
        outcome = Outcome.FAIL
        succeeded = True
        detail = (
            f"{stray_canonical_changes} canonical streams changed on instances whose raw stream "
            "did not change under the bijection; the canonicalization stage is not a function of "
            "the orbit quotient as registered"
        )
    else:
        outcome = assessment.outcome
        succeeded = outcome is Outcome.FAIL
        detail = assessment.detail
    return hra.AttackComponent(
        component_id="C-1_QUOTIENT_INVARIANCE",
        hypothesis="H_FMT",
        statement=(
            f"{ARM_CANONICAL}'s canonicalized corpus moves under a registered value-alphabet "
            "bijection, so the hardening does not factor through the renaming group"
        ),
        outcome=outcome,
        succeeded=succeeded,
        denominator=f"{pooled_opportunities} opportunities ({opportunity_definition})",
        detail=detail,
        numbers={
            "pooled_opportunities": pooled_opportunities,
            "pooled_violations": pooled_violations,
            "stray_canonical_changes": stray_canonical_changes,
            "per_bijection": per_bijection,
            "assessment": assessment.as_json(),
        },
    )


def indexed_control_component(
    *, base: D1Dataset, orbit: D1Dataset
) -> hra.AttackComponent:
    """C-2(ii): the C-1 guard must flag the indexed canonicalization design."""

    base_streams = dataset_streams(base)
    orbit_streams = dataset_streams(orbit)
    opportunities = 0
    violations = 0
    for key, stream in orbit_streams.items():
        raw_changed = stream != base_streams[key]
        if raw_changed:
            opportunities += 1
            base_indexed = hra.index_serialization(base_streams[key])[0]
            orbit_indexed = hra.index_serialization(stream)[0]
            violations += int(base_indexed != orbit_indexed)
    opportunity_definition = (
        "corpus instances whose raw serialized stream changed under the frozen orbit; violations "
        "are instances of those whose per-instance sorted-order indexed stream changed"
    )
    exercise = GuardExercise(
        guard_id="C-2ii_C1_GUARD_ON_SERIALIZED_INDEXED",
        arm_id=hra.ARM_SERIALIZED_INDEXED,
        opportunities=opportunities,
        violations=violations,
        opportunity_definition=opportunity_definition,
    )
    assessment = assess_guard(exercise, max_violation_rate=hra.MAX_ORBIT_VIOLATION_RATE)
    return hra.AttackComponent(
        component_id="C-2ii_C1_GUARD_ON_SERIALIZED_INDEXED",
        hypothesis="H_FMT",
        statement=(
            "the C-1 guard, applied to the indexed arm's per-instance sorted-order "
            "canonicalization, flags it under the frozen orbit"
        ),
        outcome=assessment.outcome,
        succeeded=assessment.outcome is Outcome.FAIL,
        denominator=f"{opportunities} opportunities ({opportunity_definition})",
        detail=assessment.detail,
        numbers={
            "opportunities": opportunities,
            "violations": violations,
            "assessment": assessment.as_json(),
        },
    )

# ---------------------------------------------------------------------------
# C-3: margin survival — the successor claim
# ---------------------------------------------------------------------------


def margin_survival_component(
    *, typed: hra.ArmRun, serialized: hra.ArmRun, canonical: hra.ArmRun
) -> hra.AttackComponent:
    """C-3: does the typed-minus-serialized margin survive canonicalization?"""

    typed_accuracy = typed.accuracy
    serialized_accuracy = serialized.accuracy
    canonical_accuracy = canonical.accuracy
    base_gap = typed_accuracy - serialized_accuracy
    canonical_gap = typed_accuracy - canonical_accuracy
    canonical_response = score_comparator(
        ARM_CANONICAL,
        gold=canonical.gold,
        predicted=canonical.predictions,
        response_definition=CANONICAL_RESPONSE_DEFINITION,
    )
    margin = measure_contrast_margin(
        "typed_minus_same_information_serialized_canonical",
        treated=typed.response(),
        comparator=canonical_response,
    )
    statement = (
        f"the typed-minus-{hra.ARM_SERIALIZED} margin survives replacing the serialized arm by "
        f"{ARM_CANONICAL}: the canonicalized arm leaves more than half of the base gap unexplained"
    )
    numbers = {
        "typed_accuracy": typed_accuracy,
        "serialized_accuracy": serialized_accuracy,
        "canonical_accuracy": canonical_accuracy,
        "base_gap": base_gap,
        "canonical_gap": canonical_gap,
        "threshold_gap": hra.REFORMAT_GAP_FRACTION * base_gap,
        "min_base_gap": hra.REFORMAT_MIN_BASE_GAP,
        "canonical_distinct_predictions": canonical_response.distinct_predictions,
        "canonical_informedness": canonical_response.informedness,
        "canonical_departures": canonical_response.departures,
        "contrast_margin": margin.as_json(),
    }
    if canonical_response.constant or margin.outcome is not Outcome.PASS:
        reason = (
            "the canonical arm answered one label on every protected case"
            if canonical_response.constant
            else f"the typed-vs-canonical contrast is unmeasurable ({margin.reason.value})"
        )
        return hra.AttackComponent(
            component_id="C-3_MARGIN_SURVIVAL",
            hypothesis="H_FMT",
            statement=statement,
            outcome=Outcome.CANNOT_CHECK,
            succeeded=False,
            denominator=f"{canonical_response.eval_cases} protected cases",
            detail=(
                f"{reason}; a constant or unresponsive comparator cannot carry the successor "
                "claim, and this is recorded as unmeasurable, not as held"
            ),
            numbers=numbers,
        )
    if base_gap < hra.REFORMAT_MIN_BASE_GAP:
        return hra.AttackComponent(
            component_id="C-3_MARGIN_SURVIVAL",
            hypothesis="H_FMT",
            statement=statement,
            outcome=Outcome.CANNOT_CHECK,
            succeeded=False,
            denominator=f"base gap {base_gap} over {len(typed.gold)} protected cases",
            detail=(
                f"the {hra.ARM_SERIALIZED} gap is {base_gap}, below the "
                f"{hra.REFORMAT_MIN_BASE_GAP} floor of four protected cases; halving it is not "
                "separable from tie-breaking noise"
            ),
            numbers=numbers,
        )
    supported = canonical_gap > hra.REFORMAT_GAP_FRACTION * base_gap
    return hra.AttackComponent(
        component_id="C-3_MARGIN_SURVIVAL",
        hypothesis="H_FMT",
        statement=statement,
        outcome=Outcome.FAIL if supported is False else Outcome.PASS,
        succeeded=supported is False,
        denominator=f"{canonical_response.departures} departures over {canonical_response.eval_cases} protected cases",
        detail=(
            f"{hra.ARM_SERIALIZED} gap {base_gap} -> {ARM_CANONICAL} gap {canonical_gap} "
            f"({hra.REFORMAT_GAP_FRACTION} of the base gap is "
            f"{hra.REFORMAT_GAP_FRACTION * base_gap}); "
            + (
                "the margin survives canonicalization on a format-invariant basis"
                if supported
                else "canonicalization closes at least half the gap; the serialized margin was format"
            )
        ),
        numbers=numbers,
    )


# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------


def _arm_json(run: hra.ArmRun, response: Any) -> dict[str, Any]:
    return {
        "dataset": run.dataset,
        "arm_id": run.arm_id,
        "config_id": run.config_id,
        "dev_accuracy": run.dev_accuracy,
        "accuracy": run.accuracy,
        **response.as_json(),
    }


def run_study(repo_root: Path) -> dict[str, Any]:
    """Build the variants, check the preconditions, then measure the hardening."""

    payload: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "record": "P9_NR05_REPRESENTATION_HARDENING_RESULT",
        "date": RESULT_DATE,
        "revival_lane": REVIVAL_LANE,
        "negative_revived": NEGATIVE_REVIVED,
        "root_cause_stage": ROOT_CAUSE_STAGE,
        "lever": LEVER,
        "gate_served": hra.GATE_SERVED,
        "freeze_document": FREEZE_DOCUMENT,
        "freeze_twin": FREEZE_TWIN,
        "parameters_sha256": frozen_digest(),
        "claim_scope": hra.CLAIM_SCOPE,
        "terminal_disposition": hra.TERMINAL_DISPOSITION,
        "protected_negative_untouched": PROTECTED_NEGATIVE_UNTOUCHED,
        "attacked_result": {
            "artifact": hra.SHIPPED_D1_RESULT,
            "dataset_manifest_digest": hra.SHIPPED_DATASET_MANIFEST_DIGEST,
            "frozen_fp2_violations_on_serialized_bag": 32,
            "frozen_fp2_opportunities": hra.PROTECTED_CASES,
        },
        "verdict_inputs": verify_against_twin(repo_root) if repo_root else {},
    }

    try:
        base, variants = build_study_datasets()
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

    bijections: dict[str, dict[str, str]] = {ORBIT_FROZEN_ID: hra.build_orbit_map(base)}
    for name, salt in BIJECTION_SALTS.items():
        bijections[name] = build_bijection_map(base, salt)
    quotient = build_quotient_table(base)

    preconditions = check_v2_preconditions(base, variants, bijections, quotient)
    payload["preconditions"] = preconditions
    payload["quotient"] = quotient_table_stats(quotient, base)
    payload["bijection_census"] = {
        name: {
            "salt": hra.ORBIT_SALT if name == ORBIT_FROZEN_ID else BIJECTION_SALTS[name],
            "atoms": len(mapping),
            "injective": len(set(mapping.values())) == len(mapping),
        }
        for name, mapping in bijections.items()
    }
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

    frozen_arms = (hra.ARM_TYPED, hra.ARM_SERIALIZED, hra.ARM_SERIALIZED_INDEXED)
    base_runs = {
        arm: hra.run_arm(base, hra.DATASET_BASE, arm, hra.FEATURE_FUNCTIONS[arm])
        for arm in frozen_arms
    }
    base_canonical = hra.run_arm(
        base, hra.DATASET_BASE, ARM_CANONICAL, canonical_feature_fn(quotient.symbol_of)
    )
    orbit_serialized = hra.run_arm(
        variants[ORBIT_FROZEN_ID],
        hra.DATASET_ORBIT,
        hra.ARM_SERIALIZED,
        hra.FEATURE_FUNCTIONS[hra.ARM_SERIALIZED],
    )
    canonical_runs: dict[str, hra.ArmRun] = {}
    for name in BIJECTION_ORDER:
        variant_table = build_quotient_table(variants[name])
        canonical_runs[name] = hra.run_arm(
            variants[name],
            name,
            ARM_CANONICAL,
            canonical_feature_fn(variant_table.symbol_of),
        )

    payload["arms"] = {
        hra.DATASET_BASE: {
            hra.ARM_TYPED: _arm_json(base_runs[hra.ARM_TYPED], base_runs[hra.ARM_TYPED].response()),
            hra.ARM_SERIALIZED: _arm_json(
                base_runs[hra.ARM_SERIALIZED], base_runs[hra.ARM_SERIALIZED].response()
            ),
            hra.ARM_SERIALIZED_INDEXED: _arm_json(
                base_runs[hra.ARM_SERIALIZED_INDEXED],
                base_runs[hra.ARM_SERIALIZED_INDEXED].response(),
            ),
            ARM_CANONICAL: _arm_json(
                base_canonical,
                score_comparator(
                    ARM_CANONICAL,
                    gold=base_canonical.gold,
                    predicted=base_canonical.predictions,
                    response_definition=CANONICAL_RESPONSE_DEFINITION,
                ),
            ),
        },
        hra.DATASET_ORBIT: {
            hra.ARM_SERIALIZED: _arm_json(
                orbit_serialized, orbit_serialized.response()
            ),
            ARM_CANONICAL: _arm_json(
                canonical_runs[ORBIT_FROZEN_ID],
                score_comparator(
                    ARM_CANONICAL,
                    gold=canonical_runs[ORBIT_FROZEN_ID].gold,
                    predicted=canonical_runs[ORBIT_FROZEN_ID].predictions,
                    response_definition=CANONICAL_RESPONSE_DEFINITION,
                ),
            ),
        },
        **{
            name: {
                ARM_CANONICAL: _arm_json(
                    canonical_runs[name],
                    score_comparator(
                        ARM_CANONICAL,
                        gold=canonical_runs[name].gold,
                        predicted=canonical_runs[name].predictions,
                        response_definition=CANONICAL_RESPONSE_DEFINITION,
                    ),
                )
            }
            for name in BIJECTION_SALTS
        },
    }

    components = [
        quotient_invariance_component(
            base=base,
            variants=variants,
            canonical_runs=canonical_runs,
            base_canonical_run=base_canonical,
        ),
        hra.invariance_component(
            component_id="C-2i_FROZEN_FP2_ON_SERIALIZED_BAG",
            hypothesis="H_FMT",
            transform="symbol-remint semantic orbit",
            base=base_runs[hra.ARM_SERIALIZED],
            transformed=orbit_serialized,
        ),
        indexed_control_component(base=base, orbit=variants[ORBIT_FROZEN_ID]),
        margin_survival_component(
            typed=base_runs[hra.ARM_TYPED],
            serialized=base_runs[hra.ARM_SERIALIZED],
            canonical=base_canonical,
        ),
        hra.invariance_component(
            component_id="C-4_FROZEN_FP2_ON_SERIALIZED_CANONICAL",
            hypothesis="H_FMT",
            transform="symbol-remint semantic orbit",
            base=base_canonical,
            transformed=canonical_runs[ORBIT_FROZEN_ID],
        ),
    ]
    payload["components"] = [item.as_json() for item in components]
    by_id = {item.component_id: item for item in components}

    if not (
        by_id["C-2i_FROZEN_FP2_ON_SERIALIZED_BAG"].succeeded
        and by_id["C-2ii_C1_GUARD_ON_SERIALIZED_INDEXED"].succeeded
    ):
        payload["verdict"] = VERDICT_GUARD_INVALID
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = (
            "a positive control did not fire: the instrument cannot distinguish a hardened arm "
            "from a broken one, so this run certifies nothing"
        )
        return payload
    if by_id["C-1_QUOTIENT_INVARIANCE"].succeeded:
        payload["verdict"] = VERDICT_INVARIANCE_BROKEN
        payload["outcome"] = Outcome.FAIL.value
        payload["detail"] = by_id["C-1_QUOTIENT_INVARIANCE"].detail
        return payload
    c3 = by_id["C-3_MARGIN_SURVIVAL"]
    if c3.outcome is Outcome.FAIL:
        payload["verdict"] = VERDICT_MARGIN_NOT_SUPPORTED
        payload["outcome"] = Outcome.FAIL.value
        payload["detail"] = c3.detail
        return payload
    if c3.outcome is Outcome.CANNOT_CHECK:
        payload["verdict"] = VERDICT_MARGIN_UNMEASURABLE
        payload["outcome"] = Outcome.CANNOT_CHECK.value
        payload["detail"] = c3.detail
        return payload
    payload["verdict"] = VERDICT_HARDENED
    payload["outcome"] = Outcome.PASS.value
    payload["detail"] = (
        "C-1 held the canonicalized corpus fixed over "
        f"{by_id['C-1_QUOTIENT_INVARIANCE'].numbers['pooled_opportunities']} bijection-reached "
        "instance opportunities with zero violations, both positive controls fired, and the "
        "typed-minus-serialized margin survived canonicalization; the frozen format-prior attack "
        "class is unrepresentable in the hardened feature space on D1"
    )
    payload["successor_claim"] = (
        "on D1 v1.2, a serialized representation whose value alphabet is quotiented by its "
        "renaming group - same information up to the disclosed co-presence merge, no relational "
        "operator added, frozen learner and selection untouched - is unmoved by the frozen "
        "format-prior attack class, and the typed-minus-serialized margin measured against it "
        "survives the frozen reformat threshold; the D1 reading that explicit relational "
        "comparison makes those fields more useful is restored on a format-invariant basis, "
        "superseding the frozen receipt's narrowing in exactly the scope it was narrowed"
    )
    return payload


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run NR-05: representation hardening of the serialized arm against the frozen "
            "format-prior attack class (P9, T4 revival)."
        )
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

    payload = run_study(args.repo_root)
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
    "ARM_CANONICAL",
    "BIJECTION_SALTS",
    "BIJECTION_ORDER",
    "CANONICAL_RESPONSE_DEFINITION",
    "FROZEN_PARAMETERS",
    "ORBIT_FROZEN_ID",
    "QuotientTable",
    "RESULT_SCHEMA_VERSION",
    "REVIVAL_LANE",
    "STUDY_ARMS",
    "VERDICT_CONSTRUCTION_FAILED",
    "VERDICT_GUARD_INVALID",
    "VERDICT_INVARIANCE_BROKEN",
    "VERDICT_MARGIN_NOT_SUPPORTED",
    "VERDICT_MARGIN_UNMEASURABLE",
    "VERDICT_HARDENED",
    "build_bijection_map",
    "build_quotient_table",
    "build_study_datasets",
    "canonical_feature_fn",
    "canonicalize_tokens",
    "check_v2_preconditions",
    "dataset_streams",
    "frozen_digest",
    "indexed_control_component",
    "main",
    "margin_survival_component",
    "quotient_invariance_component",
    "quotient_table_stats",
    "run_study",
    "verify_against_twin",
]
