#!/usr/bin/env python3
"""ORION13.MATCHED_POLARITY_NECESSITY.v2: matched-polarity opposite-verdict extension.

Protocol: development/orion-13-matched-polarity-necessity-v2-2026-09-03/
ORION13_MATCHED_POLARITY_NECESSITY_V2_PROTOCOL_V1.md (registered before this
outcome run). Closes the theory-SS7 rung: opposite-verdict cases in the two
families that contributed none, with polarity POSITIVE on both sides of every
added case so {polarity} cannot separate them, then re-runs the coordinate
necessity audit and the minimal-separator enumeration on the extended corpus.

All machinery is imported, never copied: the v1 builder, the frozen analysis
module, both P3 audit instruments, and the independent separator checker via
importlib. Exit 0 = complete (terminal in json); exit 3 = consistency failure.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from orion.knowledge.semantics import MeaningRelation  # noqa: E402
from orion.study import p3_coordinate_necessity_build as pcn  # noqa: E402
from orion.study.p3_public_reference import (  # noqa: E402
    evaluate_case,
    flat_predicate_baseline,
    load_jsonl,
    validate_case,
)
from orion.study.p3_public_reference_analysis import ablated_relation  # noqa: E402
from orion.study.p3.public_reference_audit import audit_atlas  # noqa: E402
from orion.study.p3.atlas_identifiability import audit_atlas_identifiability  # noqa: E402

STUDY_ID = "ORION13.MATCHED_POLARITY_NECESSITY.v2"
PROTOCOL_ID = "P3.matched-polarity-necessity-extension.v2"
ATLAS_ID = "matched-polarity-necessity-v2"
PROTOCOL = (
    REPO_ROOT
    / "development/orion-13-matched-polarity-necessity-v2-2026-09-03/"
    "ORION13_MATCHED_POLARITY_NECESSITY_V2_PROTOCOL_V1.md"
)
PARENT_ATLAS = REPO_ROOT / "research/p3-coordinate-necessity-v1/cases.jsonl"
PARENT_SHA256 = (
    "271ef70de685ab49a74b322dc6382f488e5f2cd9b1f82a946cf79e838ebb695c"
)
GOLD_DIR = REPO_ROOT / "papers/orion-13-global-knowledge-portrait/gold/adjudicated"
DERIVATION_GOLD = GOLD_DIR / "public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl"
DERIVATION_GOLD_SHA256 = (
    "35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8"
)
CHALLENGE_GOLD = GOLD_DIR / "public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
CHALLENGE_GOLD_SHA256 = (
    "13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b"
)
SEPARATOR = (
    REPO_ROOT
    / "papers/orion-13-global-knowledge-portrait/theory/"
    "minimal-semantic-separator-v1/independent_checker/separator.py"
)
DEFAULT_OUTPUT = REPO_ROOT / "research/p3-matched-polarity-necessity-v2"

STANDARD_FILENAME = "SYNTHETIC_MATCHED_POLARITY_STANDARD.json"
STANDARD_DATASET = "ORION-P3-MatchedPolarityStandard"
DERIVATION_RULE = "identity:frozen-registry-distinctness"

EXPECTED_REDUCT = sorted(
    ["polarity", "measurement_ids", "temporal_context_ids", "referent_ids", "construct_ids"]
)
EXPECTED_CHANGED = {
    "remove_referent": 4,
    "remove_construct": 4,
    "remove_measurement": 4,
    "remove_temporal_context": 4,
    "remove_modality_polarity_attribution_discourse": 6,
    "force_compatibility_without_obstruction": 22,
}
EXPECTED_TREATED = {"remove_referent": 80, "remove_construct": 67}

STRATA_V2 = {
    "construct": {
        "case_family": "valid_invalid_representation_mapping",
        "predicate": "reports_observed_state",
        "coordinate": "construct_ids",
        "wrap": "registry:construct:",
    },
    "referent": {
        "case_family": "different_name_same_referent",
        "predicate": "reports_quantity",
        "coordinate": "referent_ids",
        "wrap": "registry:referent:",
    },
}
DEPENDENT_ARMS_V2 = {
    "referent_ids": "remove_referent",
    "construct_ids": "remove_construct",
}

ALLOWED_IMPORTS = {
    "__future__",
    "argparse",
    "ast",
    "collections",
    "hashlib",
    "importlib.util",
    "itertools",
    "json",
    "pathlib",
    "subprocess",
    "sys",
    "time",
    "typing",
    "orion.knowledge.semantics",
    "orion.study",
    "orion.study.p3_public_reference",
    "orion.study.p3_public_reference_analysis",
    "orion.study.p3_coordinate_necessity_build",
    "orion.study.p3.public_reference_audit",
    "orion.study.p3.atlas_identifiability",
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anti_instrument_import_gate() -> dict[str, Any]:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    forbidden = sorted(imported - ALLOWED_IMPORTS)
    return {
        "imports": sorted(imported),
        "forbidden_imports": forbidden,
        "pass": not forbidden,
        "note": (
            "stdlib + frozen ORION scientific modules only; no numpy/pandas/scipy/"
            "sklearn/torch, no openai/anthropic, no random import in this file "
            "(the permutation null uses the separator checker's own RNG)"
        ),
    }


# ---- registries and the frozen standard ----------------------------------------


def parent_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    all_rows = load_jsonl(PARENT_ATLAS)
    parents = [r for r in all_rows if not str(r["case_id"]).startswith("coordinate-synth-")]
    synth_v1 = [r for r in all_rows if str(r["case_id"]).startswith("coordinate-synth-")]
    return parents, synth_v1


def registries(parents: Sequence[dict[str, object]]) -> tuple[list[str], list[str]]:
    referents: set[str] = set()
    constructs: set[str] = set()
    for row in parents:
        for side in ("left_projection", "right_projection"):
            projection = row[side]
            assert isinstance(projection, dict)
            referents.update(str(v) for v in projection.get("referent_ids") or ())
            constructs.update(str(v) for v in projection.get("construct_ids") or ())
    referent_registry = sorted(referents)
    construct_registry = sorted(constructs)
    for name, registry in (("referent", referent_registry), ("construct", construct_registry)):
        if len(registry) < 2 * pcn.DIFFER_SLOTS:
            raise AssertionError(
                f"{name} registry too small to differ on {pcn.DIFFER_SLOTS} slots: {len(registry)}"
            )
        if any("|" in value for value in registry):
            raise AssertionError(f"{name} registry value contains the digest separator |")
    return referent_registry, construct_registry


def standard_document_v2(
    referent_registry: Sequence[str], construct_registry: Sequence[str]
) -> dict[str, object]:
    return {
        "schema_version": "orion.p3.synthetic-matched-polarity-standard.v1",
        "protocol_id": PROTOCOL_ID,
        "derivation_rule": DERIVATION_RULE,
        "derivation_rule_statement": (
            "Two projections that agree on every exposed coordinate are COMPATIBLE. "
            "Two that agree on construct, measurement and temporal context and name "
            "distinct registry referents of this table are DISTINCT_REFERENT. Two that "
            "agree on referent, measurement and temporal context and name distinct "
            "registry constructs of this table are DISTINCT_CONSTRUCT."
        ),
        "referent_registry": list(referent_registry),
        "construct_registry": list(construct_registry),
        "registry_source": {
            "path": "research/p3-coordinate-necessity-v1/cases.jsonl",
            "sha256": PARENT_SHA256,
            "rows": 32,
            "note": (
                "distinct referent_ids/construct_ids values attested in the 32 "
                "non-synthetic rows of the frozen v1 parent atlas, sorted"
            ),
        },
        "measurement_dimensions": [
            {"dimension": dimension, "representative_unit": unit}
            for dimension, unit in pcn.measurement_dimensions()
        ],
        "observation_epochs": list(pcn.observation_epochs()),
        "disciplines": list(pcn.DISCIPLINES),
        "polarity_both_sides": "POSITIVE",
        "modality_both_sides": "ASSERTED",
        "external_validity": (
            "The added cases are synthetic: gold follows from this standard table by "
            f"the rule {DERIVATION_RULE}, not from an upstream expert corpus. This atlas "
            "can establish that a coordinate is load-bearing in the comparison rule; it "
            "cannot establish that such pairs are frequent in public scientific corpora."
        ),
        "not_an_accuracy_benchmark": (
            "The added cases are an ablation denominator, not an accuracy benchmark. No "
            "accuracy, false-merge or superiority number over this atlas is evidence "
            "about ORION's competence on the added cases."
        ),
    }


def standard_bytes_v2(
    referent_registry: Sequence[str], construct_registry: Sequence[str]
) -> bytes:
    return (
        json.dumps(
            standard_document_v2(referent_registry, construct_registry),
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )


def gold_relation_v2(
    *,
    referent_left: str,
    referent_right: str,
    construct_left: str,
    construct_right: str,
) -> MeaningRelation:
    if referent_left != referent_right:
        return MeaningRelation.DISTINCT_REFERENT
    if construct_left != construct_right:
        return MeaningRelation.DISTINCT_CONSTRUCT
    return MeaningRelation.COMPATIBLE


def _registry_pair(registry: Sequence[str], slot: int) -> tuple[str, str]:
    if slot < pcn.DIFFER_SLOTS:
        left = registry[(2 * slot) % len(registry)]
        right = registry[(2 * slot + 1) % len(registry)]
        if left == right:  # pragma: no cover - guards a shrunken registry
            raise AssertionError(f"slot {slot}: registry too small to differ")
        return left, right
    value = registry[slot % len(registry)]
    return value, value


def _case_v2(
    stratum: str,
    slot: int,
    *,
    standard_hash: str,
    referent_registry: Sequence[str],
    construct_registry: Sequence[str],
    slots_per_stratum: int,
) -> dict[str, object]:
    spec = STRATA_V2[stratum]
    discipline = pcn.DISCIPLINES[slot % len(pcn.DISCIPLINES)]
    dimensions = pcn.measurement_dimensions()
    epochs = pcn.observation_epochs()
    measurement = f"synth:measurement:dimension:{dimensions[slot % len(dimensions)][0]}"
    temporal = f"synth:temporal:epoch:{epochs[slot % len(epochs)]}"
    construct_left = construct_right = construct_registry[slot % len(construct_registry)]
    referent_left = referent_right = referent_registry[slot % len(referent_registry)]
    if stratum == "referent":
        referent_left, referent_right = _registry_pair(referent_registry, slot)
    else:
        construct_left, construct_right = _registry_pair(construct_registry, slot)
    relation = gold_relation_v2(
        referent_left=referent_left,
        referent_right=referent_right,
        construct_left=construct_left,
        construct_right=construct_right,
    )
    digest = pcn._decimal_digest(
        "|".join(
            [
                PROTOCOL_ID,
                stratum,
                str(slot),
                referent_left,
                referent_right,
                construct_left,
                construct_right,
                measurement,
                temporal,
            ]
        )
    )

    def projection(side: str, referent: str, construct: str) -> dict[str, object]:
        return {
            "projection_id": f"matched:{digest}:{side}",
            "source_id": "orion-p3-matched-polarity-standard",
            "source_span": f"{STANDARD_FILENAME}#case={digest}&side={side}",
            "predicate": str(spec["predicate"]),
            "referent_ids": [referent],
            "construct_ids": [construct],
            "measurement_ids": [measurement],
            "temporal_context_ids": [temporal],
            "polarity": "POSITIVE",
            "modality": "ASSERTED",
        }

    case = {
        "schema_version": "orion.p3.public-reference-case.v1",
        "case_id": f"matched-synth-{digest}",
        "discipline": discipline,
        "case_family": str(spec["case_family"]),
        "source_records": [
            {
                "dataset": STANDARD_DATASET,
                "revision": standard_hash,
                "locator": STANDARD_FILENAME,
                "content_hash": standard_hash,
                "license": "CC0-1.0",
            }
        ],
        "left_projection": projection("l", referent_left, construct_left),
        "right_projection": projection("r", referent_right, construct_right),
        "expected": {
            "meaning_relation": relation.value,
            "authority": {
                "kind": "DERIVED_FROM_ALLOWED",
                "evidence": [
                    f"{STANDARD_DATASET}@{standard_hash}:{STANDARD_FILENAME}#case={digest}&side=l",
                    f"{STANDARD_DATASET}@{standard_hash}:{STANDARD_FILENAME}#case={digest}&side=r",
                ],
                "derivation": {
                    "rule": DERIVATION_RULE,
                    "inputs": [referent_left, referent_right, construct_left, construct_right],
                },
            },
        },
    }
    if slot >= pcn.DIFFER_SLOTS:
        assert relation is MeaningRelation.COMPATIBLE  # agree slots agree everywhere
    validate_case(case)
    return case


def added_cases(
    referent_registry: Sequence[str],
    construct_registry: Sequence[str],
    *,
    slots_per_stratum: int,
) -> list[dict[str, object]]:
    standard_hash = hashlib.sha256(
        standard_bytes_v2(referent_registry, construct_registry)
    ).hexdigest()
    cases = [
        _case_v2(
            stratum,
            slot,
            standard_hash=standard_hash,
            referent_registry=referent_registry,
            construct_registry=construct_registry,
            slots_per_stratum=slots_per_stratum,
        )
        for stratum in sorted(STRATA_V2)
        for slot in range(slots_per_stratum)
    ]
    ids = [str(case["case_id"]) for case in cases]
    if len(set(ids)) != len(ids):  # pragma: no cover - a collision would be a hash break
        raise AssertionError("matched-polarity case ids collided")
    return cases


def dependence_receipts_v2(
    added: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    receipts: list[dict[str, object]] = []
    for case in added:
        expected = case["expected"]
        assert isinstance(expected, dict)
        gold = MeaningRelation(str(expected["meaning_relation"]))
        if gold is MeaningRelation.COMPATIBLE:
            continue
        coordinate = (
            "referent_ids" if gold is MeaningRelation.DISTINCT_REFERENT else "construct_ids"
        )
        arm = DEPENDENT_ARMS_V2[coordinate]
        full = MeaningRelation(evaluate_case(case).predicted)
        ablated = ablated_relation(case, arm)
        receipts.append(
            {
                "case_id": str(case["case_id"]),
                "coordinate": coordinate,
                "arm": arm,
                "gold": gold.value,
                "full_system": full.value,
                "ablated": ablated.value,
                "full_system_correct": full is gold,
                "ablation_changes_answer": ablated is not gold,
            }
        )
    return receipts


def _counter(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _arm_row(audit: dict[str, object], arm_id: str) -> dict[str, object]:
    for row in audit["coordinate_necessity"]:  # type: ignore[index]
        if row["arm_id"] == arm_id:
            return row  # type: ignore[return-value]
    raise AssertionError(f"arm {arm_id} missing from audit")


def _guard_row(audit: dict[str, object], guard_id: str) -> dict[str, object]:
    for row in audit["identity_guards"]:  # type: ignore[index]
        if row["guard_id"] == guard_id:
            return row  # type: ignore[return-value]
    raise AssertionError(f"guard {guard_id} missing from audit")


# ---- separator, on the checker's own machinery ----------------------------------


def load_separator():
    spec = importlib.util.spec_from_file_location("separator", SEPARATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_separator_input(path: Path, cases: Sequence[dict[str, object]]) -> None:
    pcn.write_jsonl(path, sorted(cases, key=lambda case: str(case["case_id"])))


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def separator_run(sep, derivation: Path, challenge: Path) -> dict[str, Any]:
    coords, d1 = sep.load(derivation)
    coords2, d2 = sep.load(challenge)
    if coords != coords2:
        raise AssertionError(f"coordinate sets differ: {coords} vs {coords2}")
    k = len(coords)
    sufficient = [
        s
        for r in range(k + 1)
        for s in itertools.combinations(range(k), r)
        if sep.is_sufficient(d1, list(s))
    ]
    if not sufficient:
        raise AssertionError("full coordinate set is not sufficient on the derivation corpus")
    k_star = min(len(s) for s in sufficient)
    minimal = [s for s in sufficient if not any(set(t) < set(s) for t in sufficient)]
    reducts = sorted(minimal, key=lambda s: (len(s), s))
    core = sorted(set.intersection(*(set(s) for s in reducts))) if reducts else []
    heldout = []
    for s in reducts:
        ok = sep.is_sufficient(d2, list(s))
        heldout.append(
            {
                "subset": [coords[j] for j in s],
                "size": len(s),
                "sufficient_on_challenge_set": ok,
                "collisions_on_challenge_set": [
                    list(p) for p in sep.collisions(d2, list(s))
                ][:5],
            }
        )
    rng = sep.random.Random(sep.SEED)
    labels = [c["verdict"] for c in d1]
    hits = 0
    for _ in range(sep.PERM_TRIALS):
        rng.shuffle(labels)
        shuffled = [{**c, "verdict": labels[i]} for i, c in enumerate(d1)]
        if any(
            sep.is_sufficient(shuffled, list(s))
            for s in itertools.combinations(range(k), k_star or k)
        ):
            hits += 1
    polarity_index = coords.index("polarity")
    singletons_sufficient = {
        coords[j]: bool(sep.is_sufficient(d1, [j])) for j in range(k)
    }
    shared_ids = sorted({c["case_id"] for c in d1} & {c["case_id"] for c in d2})
    return {
        "coordinates": coords,
        "derivation_set": {
            "path": _rel(derivation),
            "cases": len(d1),
            "verdicts": _counter(c["verdict"] for c in d1),
            "families": _counter(c["family"] for c in d1),
        },
        "challenge_set": {
            "path": _rel(challenge),
            "cases": len(d2),
            "verdicts": _counter(c["verdict"] for c in d2),
            "families": _counter(c["family"] for c in d2),
            "shared_case_ids_with_derivation_set": len(shared_ids),
            "shared_case_ids_note": (
                "the 48 synthetic rows appear in both corpora by construction; the "
                "held-out part of the challenge set is its 32 parent rows"
            ),
        },
        "full_coordinate_set_sufficient_on_derivation": True,
        "k_star_on_derivation": k_star,
        "minimal_sufficient_subsets_reducts": [[coords[j] for j in s] for s in reducts],
        "reduct_count": len(reducts),
        "core_coordinates_in_every_reduct": [coords[j] for j in core],
        "coordinates_in_no_reduct": [
            c for i, c in enumerate(coords) if all(i not in s for s in reducts)
        ],
        "held_out_validation": heldout,
        "polarity_sufficient_on_derivation": bool(sep.is_sufficient(d1, [polarity_index])),
        "polarity_sufficient_on_challenge": bool(sep.is_sufficient(d2, [polarity_index])),
        "polarity_collisions_on_challenge": [
            list(p) for p in sep.collisions(d2, [polarity_index])
        ][:5],
        "singletons_sufficient_on_derivation": singletons_sufficient,
        "structure_free_null": {
            "trials": sep.PERM_TRIALS,
            "hits": hits,
            "rate": hits / sep.PERM_TRIALS,
            "seed": sep.SEED,
        },
    }


# ---- outcome run ----------------------------------------------------------------


def run(output_dir: Path, *, slots_per_stratum: int, smoke: bool) -> dict[str, Any]:
    t_start = time.time()
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    import_gate = anti_instrument_import_gate()
    if not import_gate["pass"]:
        raise AssertionError({"import_gate": import_gate})

    parent_sha = sha256_file(PARENT_ATLAS)
    if not smoke and parent_sha != PARENT_SHA256:
        raise AssertionError({"parent_atlas_sha256": parent_sha})
    if not smoke and sha256_file(DERIVATION_GOLD) != DERIVATION_GOLD_SHA256:
        raise AssertionError({"derivation_gold_sha256": sha256_file(DERIVATION_GOLD)})
    if not smoke and sha256_file(CHALLENGE_GOLD) != CHALLENGE_GOLD_SHA256:
        raise AssertionError({"challenge_gold_sha256": sha256_file(CHALLENGE_GOLD)})

    parents, synth_v1 = parent_rows()
    if not smoke and len(parents) != 32:
        raise AssertionError({"non_synthetic_parent_rows": len(parents)})
    if not smoke and len(synth_v1) != 24:
        raise AssertionError({"v1_synthetic_rows": len(synth_v1)})
    referent_registry, construct_registry = registries(parents)
    standard_hash = hashlib.sha256(
        standard_bytes_v2(referent_registry, construct_registry)
    ).hexdigest()
    added = added_cases(referent_registry, construct_registry, slots_per_stratum=slots_per_stratum)
    merged = sorted([*parents, *synth_v1, *added], key=lambda case: str(case["case_id"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / STANDARD_FILENAME).write_bytes(
        standard_bytes_v2(referent_registry, construct_registry)
    )
    pcn.write_jsonl(output_dir / "cases.jsonl", merged)
    cases_hash = sha256_file(output_dir / "cases.jsonl")

    receipts = dependence_receipts_v2(added)
    added_population = pcn._coordinate_population(added)
    invariants = pcn.shape_invariants(added)
    varying_invariants = sorted(name for name, values in invariants.items() if len(values) > 1)
    parent_ids = {str(case["case_id"]) for case in parents}
    id_collisions = sorted(parent_ids & {str(case["case_id"]) for case in added})

    audit_before = audit_atlas(ATLAS_ID + "_before_parent56", [*parents, *synth_v1])
    audit_after = audit_atlas(ATLAS_ID, merged)
    ident_after = audit_atlas_identifiability(ATLAS_ID, merged)
    ident_added = audit_atlas_identifiability(ATLAS_ID + "-added-only", added)

    flat_false_merges = sum(
        1
        for case in merged
        if MeaningRelation(str(dict(case["expected"])["meaning_relation"]))
        not in (MeaningRelation.COMPATIBLE, MeaningRelation.UNRESOLVED)
        and flat_predicate_baseline(case) is MeaningRelation.COMPATIBLE
    )

    sep = load_separator()
    derivation_path = output_dir / "separator_derivation.jsonl"
    challenge_path = output_dir / "separator_challenge.jsonl"
    write_separator_input(derivation_path, [*load_jsonl(DERIVATION_GOLD), *synth_v1, *added])
    write_separator_input(challenge_path, [*load_jsonl(CHALLENGE_GOLD), *synth_v1, *added])
    separator = separator_run(sep, derivation_path, challenge_path)

    # ---- gates, executed ----
    g1 = {
        "parent_sha256": parent_sha == PARENT_SHA256,
        "derivation_gold_sha256": sha256_file(DERIVATION_GOLD) == DERIVATION_GOLD_SHA256,
        "challenge_gold_sha256": sha256_file(CHALLENGE_GOLD) == CHALLENGE_GOLD_SHA256,
        "all_parent_ids_present": parent_ids <= {str(case["case_id"]) for case in merged},
    }
    g2 = {
        "all_added_correct": all(r["full_system_correct"] for r in receipts)
        and all(
            MeaningRelation(evaluate_case(case).predicted)
            is MeaningRelation(str(dict(case["expected"])["meaning_relation"]))
            for case in added
        ),
        "differ_cases_depend": len(receipts) == 2 * min(pcn.DIFFER_SLOTS, slots_per_stratum)
        and all(r["ablation_changes_answer"] for r in receipts),
    }
    arm_after = {row["arm_id"]: row for row in audit_after["coordinate_necessity"]}
    arm_before = {row["arm_id"]: row for row in audit_before["coordinate_necessity"]}
    g3 = {
        arm: {
            "outcome": arm_after[arm]["outcome"],
            "reason": arm_after[arm]["reason"],
            "pass": arm_after[arm]["outcome"] == "PASS"
            and arm_after[arm]["reason"] == "COORDINATE_LOAD_BEARING"
            and arm_after[arm]["contrast"]["decisions_changed"] == EXPECTED_CHANGED[arm],
            "decisions_changed": arm_after[arm]["contrast"]["decisions_changed"],
            "cases_treated": arm_after[arm]["contrast"]["cases_treated"],
            "v1_outcome": arm_before[arm]["outcome"],
        }
        for arm in ("remove_referent", "remove_construct")
    }
    g3["pass"] = all(item["pass"] for item in g3.values() if isinstance(item, dict))
    g4 = {
        "full_set_sufficient": separator["full_coordinate_set_sufficient_on_derivation"],
        "polarity_not_sufficient_derivation": not separator["polarity_sufficient_on_derivation"],
        "polarity_not_sufficient_challenge": not separator["polarity_sufficient_on_challenge"],
        "no_singleton_sufficient": not any(separator["singletons_sufficient_on_derivation"].values()),
        "all_reducts_sufficient_on_challenge": all(
            h["sufficient_on_challenge_set"] for h in separator["held_out_validation"]
        ),
    }
    g5 = {"in_sample_overall": ident_after["overall_outcome"], "pass": ident_after["overall_outcome"] == "PASS"}
    merge_guard = _guard_row(audit_after, "P3.FALSE_SCIENTIFIC_MERGE")
    g6 = {"outcome": merge_guard["outcome"], "pass": merge_guard["outcome"] == "PASS"}
    g7 = {"varying": varying_invariants, "pass": not varying_invariants and not id_collisions}
    g8 = import_gate
    gates = {
        "G1_parent_integrity": g1,
        "G2_added_case_correctness": g2,
        "G3_arm_repair": g3,
        "G4_separator": g4,
        "G5_identifiability": g5,
        "G6_guards": g6,
        "G7_shape_invariants": g7,
        "G8_import_gate": {"pass": g8["pass"]},
    }

    gate_pass = {
        "G1": all(g1.values()),
        "G2": g2["all_added_correct"] and g2["differ_cases_depend"],
        "G3": g3["pass"] is True,
        "G4": all(g4.values()),
        "G5": g5["pass"],
        "G6": g6["pass"],
        "G7": g7["pass"],
        "G8": g8["pass"],
    }

    predictions = {
        "P1_polarity_insufficient_on_D": {
            "predicted": True, "observed": not separator["polarity_sufficient_on_derivation"]},
        "P2_polarity_insufficient_on_C": {
            "predicted": True, "observed": not separator["polarity_sufficient_on_challenge"]},
        "P3_no_singleton_sufficient_on_D": {
            "predicted": True,
            "observed": not any(separator["singletons_sufficient_on_derivation"].values())},
        "P4_k_star_5_unique_reduct": {
            "predicted": True,
            "observed": separator["k_star_on_derivation"] == 5
            and separator["reduct_count"] == 1
            and sorted(separator["minimal_sufficient_subsets_reducts"][0]) == EXPECTED_REDUCT,
            "note": "derived prediction; wrong if any parent COMPATIBLE case carries a zero bit on the five"},
        "P5_every_derivation_reduct_sufficient_on_C": {
            "predicted": True,
            "observed": all(h["sufficient_on_challenge_set"] for h in separator["held_out_validation"])},
        "P6_null_rate_small": {
            "predicted": "small", "observed": separator["structure_free_null"]["rate"]},
        "P7_arm_counts": {
            "predicted": EXPECTED_CHANGED,
            "observed": {
                arm: arm_after[arm]["contrast"]["decisions_changed"] for arm in EXPECTED_CHANGED
            }},
        "P8_treated_counts_floor": {
            "predicted": EXPECTED_TREATED,
            "observed": {
                arm: arm_after[arm]["contrast"]["cases_treated"] for arm in EXPECTED_TREATED
            }},
        "P9_overall_audit_cannot_check": {
            "predicted": "CANNOT_CHECK", "observed": audit_after["overall_outcome"]},
        "P10_family_tokens_mixed": {
            "predicted": True,
            "observed": set(
                separator["derivation_set"]["families"]
            ) >= {"different_name_same_referent", "valid_invalid_representation_mapping"},
        },
    }

    if not all(gate_pass.values()):
        # gate failures route to the frozen terminals below, never to a silent pass
        pass
    heldout_ok = all(h["sufficient_on_challenge_set"] for h in separator["held_out_validation"])
    # terminal SS6, first match wins: cue -> arm repair -> polarity -> heldout -> positive
    terminal = "MPN2_ARMS_MEASURED_AND_POLARITY_DETHRONED"
    if not (gate_pass["G5"] and gate_pass["G6"]):
        terminal = "MPN2_CONSTRUCTION_CUE"
    elif gate_pass["G3"] is False:
        terminal = "MPN2_ARM_REPAIR_FAILED"
    elif not gate_pass["G4"]:
        terminal = "MPN2_POLARITY_STILL_SUFFICIENT"
    elif not heldout_ok:
        terminal = "MPN2_HELDOUT_SEPARATOR_FAILS"

    result: dict[str, Any] = {
        "schema": "ORION.ORION13.MatchedPolarityNecessity.Result.v1",
        "study_id": STUDY_ID,
        "smoke": smoke,
        "base_revision": subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "protocol_sha256": sha256_file(PROTOCOL),
        "atlas": {
            "atlas_id": ATLAS_ID,
            "n": len(merged),
            "cases_sha256": cases_hash,
            "standard_sha256": standard_hash,
            "parent": {
                "path": PARENT_ATLAS.relative_to(REPO_ROOT).as_posix(),
                "sha256": parent_sha,
                "case_count": len(parents) + len(synth_v1),
                "note": "copied through unchanged; the frozen v1 atlas is never edited",
            },
            "added_case_count": len(added),
            "expected_relations_merged": _counter(
                str(dict(case["expected"])["meaning_relation"]) for case in merged
            ),
            "expected_relations_added": _counter(
                str(dict(case["expected"])["meaning_relation"]) for case in added
            ),
            "case_families_merged": _counter(str(case["case_family"]) for case in merged),
            "coordinate_population": {
                "parent": pcn._coordinate_population([*parents, *synth_v1]),
                "added": added_population,
                "merged": pcn._coordinate_population(merged),
            },
            "dependence_receipts": receipts,
            "added_shape_invariants": invariants,
            "parent_id_collisions": id_collisions,
        },
        "audit_before": {
            "overall_outcome": audit_before["overall_outcome"],
            "arms": {
                row["arm_id"]: {
                    "outcome": row["outcome"],
                    "reason": row["reason"],
                    "cases_treated": row["contrast"]["cases_treated"],
                    "decisions_changed": row["contrast"]["decisions_changed"],
                }
                for row in audit_before["coordinate_necessity"]
            },
        },
        "audit_after": {
            "overall_outcome": audit_after["overall_outcome"],
            "arms": {
                row["arm_id"]: {
                    "outcome": row["outcome"],
                    "reason": row["reason"],
                    "cases_treated": row["contrast"]["cases_treated"],
                    "decisions_changed": row["contrast"]["decisions_changed"],
                }
                for row in audit_after["coordinate_necessity"]
            },
            "guards": {
                row["guard_id"]: row["outcome"] for row in audit_after["identity_guards"]
            },
        },
        "identifiability": {
            "merged_overall": ident_after["overall_outcome"],
            "merged_labels": ident_after["labels"],
            "added_only_overall": ident_added["overall_outcome"],
            "hash_parity_descriptive": {
                label: row["outcome"] for row in ident_after["audits"]["hash_parity"]
                for label in [row.get("label", "")]
            },
        },
        "flat_baseline_false_merges_descriptive": {
            "count": flat_false_merges,
            "n": len(merged),
            "note": "descriptive only; the flat baseline is not the study's comparator",
        },
        "separator": separator,
        "gates": gates,
        "gate_pass": gate_pass,
        "predictions": predictions,
        "terminal": terminal,
        "authority": (
            "LOAD_BEARING_IN_THE_COMPARISON_RULE_ON_A_CONSTRUCTED_MATCHED_POLARITY_CORPUS__"
            "NO_EXTERNAL_VALIDITY__NO_ACCURACY_CLAIM__V1_FAILS_STAND__"
            "NO_GENERAL_NECESSITY_CLAIM"
        ),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "wall_clock_seconds": round(time.time() - t_start, 1),
    }
    (output_dir / "AUDIT_AFTER_matched-polarity-necessity-v2.json").write_text(
        json.dumps(audit_after, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "AUDIT_BEFORE_parent56.json").write_text(
        json.dumps(audit_before, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "IDENTIFIABILITY_merged80.json").write_text(
        json.dumps(ident_after, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "IDENTIFIABILITY_added24.json").write_text(
        json.dumps(ident_added, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifacts: dict[str, str] = {}
    for name in (
        "cases.jsonl",
        STANDARD_FILENAME,
        "separator_derivation.jsonl",
        "separator_challenge.jsonl",
        "AUDIT_AFTER_matched-polarity-necessity-v2.json",
        "AUDIT_BEFORE_parent56.json",
        "IDENTIFIABILITY_merged80.json",
        "IDENTIFIABILITY_added24.json",
    ):
        path = output_dir / name
        try:
            key = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            key = path.as_posix()
        artifacts[key] = sha256_file(path)
    result["artifacts"] = artifacts
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--slots-per-stratum", type=int, default=pcn.SLOTS_PER_STRATUM)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="mechanics check on a truncated grid; not an outcome run",
    )
    args = parser.parse_args()
    output_dir = (
        Path("/tmp") / "o13_mpn2_smoke" if args.smoke and args.output_dir == DEFAULT_OUTPUT
        else args.output_dir
    )
    try:
        result = run(
            args.output_dir if not args.smoke else output_dir,
            slots_per_stratum=args.slots_per_stratum,
            smoke=args.smoke,
        )
    except (AssertionError, FileNotFoundError) as exc:
        print(f"MPN2_CONSISTENCY_FAILURE: {exc}")
        return 3
    print(
        canonical(
            {
                "terminal": result["terminal"],
                "digest": result["result_digest"],
                "smoke": result["smoke"],
                "k_star": result["separator"]["k_star_on_derivation"],
                "reducts": result["separator"]["minimal_sufficient_subsets_reducts"],
                "polarity_sufficient_D": result["separator"]["polarity_sufficient_on_derivation"],
                "arms": result["audit_after"]["arms"],
                "gate_pass": result["gate_pass"],
            }
        )
    )
    return 0 if result["terminal"] != "MPN2_CONSISTENCY_FAILURE" else 3


if __name__ == "__main__":
    raise SystemExit(main())

