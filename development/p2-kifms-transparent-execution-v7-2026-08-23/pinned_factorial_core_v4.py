#!/usr/bin/env python3
"""Execute the frozen P2 SWIFT V4 2x2 component factorization.

This is post-outcome public-development mechanism diagnosis only.  It cannot
promote a controller or support superiority on SWIFT.  Source text is used in
memory but is never emitted to a result artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from itertools import combinations
from pathlib import Path
from typing import Any, Callable

import numpy as np
import openpyxl
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC


ARM_NAMES = ("R0_L0", "R0_L1", "R1_L0", "R1_L1")
METRICS = (
    "recall_at_005",
    "recall_at_010",
    "recall_at_020",
    "fraction_screened_at_95_recall",
    "wss_at_95",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def load_v3_module(source_root: Path) -> Any:
    path = source_root / "run_swift_cross_review_controller_transport_v3.py"
    spec = importlib.util.spec_from_file_location("p2_swift_v3_frozen", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen V3 runner: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_sha256_manifest(source_root: Path) -> dict[str, Any]:
    manifest_path = source_root / "SHA256SUMS"
    files: dict[str, Any] = {}
    for line_number, raw in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            expected, relative = raw.split(maxsplit=1)
        except ValueError as exc:
            raise ValueError(f"Malformed SHA256SUMS line {line_number}") from exc
        relative = relative.lstrip(" *")
        path = source_root / relative
        actual = sha256_file(path) if path.is_file() else None
        actual_bytes = path.stat().st_size if path.is_file() else None
        files[relative] = {
            "bytes": actual_bytes,
            "passed": actual == expected,
            "sha256_actual": actual,
            "sha256_expected": expected,
        }
    return {
        "files": files,
        "manifest_bytes": manifest_path.stat().st_size,
        "manifest_sha256": sha256_file(manifest_path),
        "passed": bool(files) and all(item["passed"] for item in files.values()),
        "verified_file_count": len(files),
    }


def verify_freezes(
    source_root: Path,
    target_root: Path,
    protocol_v4_path: Path,
    implementation_v4_path: Path,
) -> tuple[dict[str, Any], bool]:
    protocol_v4 = json.loads(protocol_v4_path.read_text(encoding="utf-8"))
    implementation_v4 = json.loads(implementation_v4_path.read_text(encoding="utf-8"))
    fixed_files = {
        "protocol_v4": (protocol_v4_path, implementation_v4["protocol_v4_sha256"]),
        "runner_v4": (Path(__file__).resolve(), implementation_v4["runner_v4_sha256"]),
        "result_v3": (source_root / "RESULT_V3.json", protocol_v4["v3_result_sha256"]),
        "protocol_v3": (source_root / "PROTOCOL_FREEZE_V3.json", implementation_v4["protocol_v3_sha256"]),
        "implementation_v3": (
            source_root / "IMPLEMENTATION_FREEZE_V3.json",
            implementation_v4["implementation_v3_sha256"],
        ),
        "runner_v3": (
            source_root / "run_swift_cross_review_controller_transport_v3.py",
            implementation_v4["runner_v3_sha256"],
        ),
        "source_and_rights_v1": (
            source_root / "SOURCE_AND_RIGHTS_FREEZE_V1.json",
            implementation_v4["source_and_rights_v1_sha256"],
        ),
    }
    receipts: dict[str, Any] = {}
    for name, (path, expected) in fixed_files.items():
        actual = sha256_file(path) if path.is_file() else None
        receipts[name] = {
            "bytes": path.stat().st_size if path.is_file() else None,
            "passed": actual == expected,
            "path_role": name,
            "sha256_actual": actual,
            "sha256_expected": expected,
        }
    source_manifest = verify_sha256_manifest(source_root)
    receipt = {
        "fixed_files": receipts,
        "source_handoff_manifest": source_manifest,
        "source_root_not_redistributed": str(source_root),
        "target_root": str(target_root),
    }
    passed = all(item["passed"] for item in receipts.values()) and source_manifest["passed"]
    receipt["passed"] = passed
    return receipt, passed


def candidate_model() -> SGDClassifier:
    return SGDClassifier(
        loss="log_loss",
        class_weight="balanced",
        alpha=1e-5,
        max_iter=2000,
        tol=1e-4,
        random_state=20260823,
    )


def comparator_model() -> LinearSVC:
    return LinearSVC(loss="squared_hinge", C=0.11, random_state=20260823)


def execute_arm(
    v3: Any,
    arm: str,
    matrix: Any,
    labels: np.ndarray,
    seed: list[int],
    batch_size: int,
) -> tuple[list[int], int]:
    learner = arm.split("_")[1]
    if learner == "L0":
        return v3.complete_active_order(
            x=matrix,
            labels=labels,
            seed=seed,
            batch_size=batch_size,
            model_factory=candidate_model,
            score_function=lambda model, pool: model.predict_proba(pool)[:, 1],
        )
    return v3.complete_active_order(
        x=matrix,
        labels=labels,
        seed=seed,
        batch_size=batch_size,
        model_factory=comparator_model,
        score_function=lambda model, pool: model.decision_function(pool),
        weight_ratio=9.8,
    )


def mean(values: list[float]) -> float:
    return float(np.mean(values))


def component_effects(arms: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {
        "interaction": {},
        "learner_balancer_main_effect": {},
        "representation_main_effect": {},
    }
    for metric in METRICS:
        r0l0 = arms["R0_L0"][metric]
        r0l1 = arms["R0_L1"][metric]
        r1l0 = arms["R1_L0"][metric]
        r1l1 = arms["R1_L1"][metric]
        output["representation_main_effect"][metric] = 0.5 * ((r1l0 - r0l0) + (r1l1 - r0l1))
        output["learner_balancer_main_effect"][metric] = 0.5 * ((r0l1 - r0l0) + (r1l1 - r1l0))
        output["interaction"][metric] = (r1l1 - r0l1) - (r1l0 - r0l0)
    return output


def same_sign_count(values: list[float], reference: float) -> int:
    if reference > 0:
        return sum(value > 0 for value in values)
    if reference < 0:
        return sum(value < 0 for value in values)
    return sum(value == 0 for value in values)


def classify(
    effects_by_review: dict[str, dict[str, dict[str, float]]],
    mean_effects: dict[str, dict[str, float]],
    v3_gap: float,
) -> dict[str, Any]:
    threshold = max(0.01, 0.5 * abs(v3_gap))
    checks: dict[str, Any] = {}
    stable_components: list[str] = []
    for component in ("representation_main_effect", "learner_balancer_main_effect"):
        value = mean_effects[component]["recall_at_010"]
        per_review = [effects_by_review[review][component]["recall_at_010"] for review in effects_by_review]
        sign_count = same_sign_count(per_review, value)
        passed = abs(value) >= 0.01 and sign_count >= 4 and abs(value) >= 0.5 * abs(v3_gap)
        checks[component] = {
            "absolute_mean_at_least_0_01": abs(value) >= 0.01,
            "absolute_mean_at_least_half_v3_gap": abs(value) >= 0.5 * abs(v3_gap),
            "absolute_threshold": threshold,
            "mean_recall_at_010": value,
            "passed": passed,
            "same_sign_review_count": sign_count,
        }
        if passed:
            stable_components.append(component)

    interaction = mean_effects["interaction"]["recall_at_010"]
    interaction_values = [
        effects_by_review[review]["interaction"]["recall_at_010"] for review in effects_by_review
    ]
    interaction_sign_count = same_sign_count(interaction_values, interaction)
    interaction_passed = (
        not stable_components and abs(interaction) >= 0.01 and interaction_sign_count >= 4
    )
    checks["interaction"] = {
        "absolute_mean_at_least_0_01": abs(interaction) >= 0.01,
        "eligible_only_when_no_stable_component": not stable_components,
        "mean_recall_at_010": interaction,
        "passed": interaction_passed,
        "same_sign_review_count": interaction_sign_count,
    }
    if stable_components:
        category = "STABLE_COMPONENT"
    elif interaction_passed:
        category = "INTERACTION_DOMINANT"
    else:
        category = "NO_STABLE_ATTRIBUTION"
    return {
        "category": category,
        "checks": checks,
        "selected_components_for_future_freeze_only": stable_components,
        "selection_is_not_promotion": True,
        "v3_full_arm_gap_recall_at_010": v3_gap,
    }


def execute(
    source_root: Path,
    target_root: Path,
    protocol_v4_path: Path,
    implementation_v4_path: Path,
    out_path: Path,
) -> None:
    start = time.monotonic()
    protocol_v4 = json.loads(protocol_v4_path.read_text(encoding="utf-8"))
    implementation_v4 = json.loads(implementation_v4_path.read_text(encoding="utf-8"))
    v3_result = json.loads((source_root / "RESULT_V3.json").read_text(encoding="utf-8"))
    v3_protocol = json.loads((source_root / "PROTOCOL_FREEZE_V3.json").read_text(encoding="utf-8"))
    freeze_receipt, freeze_ok = verify_freezes(
        source_root, target_root, protocol_v4_path, implementation_v4_path
    )
    result: dict[str, Any] = {
        "claim_scope": protocol_v4["scope"],
        "freeze_receipt": freeze_receipt,
        "identity": protocol_v4["identity"],
        "implementation_v4_sha256": sha256_file(implementation_v4_path),
        "nonpromotion_rule": protocol_v4["nonpromotion_rule"],
        "preserved_adverse_terminals": implementation_v4["preserved_adverse_terminals"],
        "protocol_status": protocol_v4["status"],
        "protocol_v4_sha256": sha256_file(protocol_v4_path),
        "software": {
            "numpy": np.__version__,
            "openpyxl": openpyxl.__version__,
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
        },
    }
    cannot_check = "P2_SWIFT_V4_COMPONENT_FACTORIZATION_CANNOT_CHECK_BINDING_POPULATION_OR_REPRODUCIBILITY"
    if not freeze_ok:
        result.update({"terminal": cannot_check})
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return

    v3 = load_v3_module(source_root)
    source_binding, source_binding_ok = v3.binding_receipt(
        source_root,
        source_root / "SOURCE_AND_RIGHTS_FREEZE_V1.json",
        source_root / "PROTOCOL_FREEZE_V3.json",
        source_root / "IMPLEMENTATION_FREEZE_V3.json",
    )
    result["v3_source_binding_receipt"] = source_binding
    if not source_binding_ok:
        result.update({"terminal": cannot_check})
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return

    print("all_source_hashes_passed; loading frozen local PubMed snapshot", flush=True)
    pubmed, pubmed_receipt = v3.load_pubmed_snapshot(source_root / "private-source/pubmed-snapshot.jsonl")
    review_rows: dict[str, list[dict[str, Any]]] = {}
    population_receipts: dict[str, dict[str, Any]] = {}
    for review in v3.REVIEWS:
        rows, receipt = v3.load_review(source_root, review, v3_protocol, pubmed)
        review_rows[review] = rows
        population_receipts[review] = receipt
        print(f"population_loaded review={review} canonical_rows={len(rows)}", flush=True)

    pairwise_overlap: list[dict[str, Any]] = []
    max_overlap = 0
    for review_a, review_b in combinations(v3.REVIEWS, 2):
        a = {row["content_identity"] for row in review_rows[review_a]}
        b = {row["content_identity"] for row in review_rows[review_b]}
        count = len(a & b)
        max_overlap = max(max_overlap, count)
        pairwise_overlap.append(
            {"review_a": review_a, "review_b": review_b, "shared_content_identities": count}
        )
    overlap_receipt = {
        "max_pairwise_shared_content_identities": max_overlap,
        "pairwise": pairwise_overlap,
    }
    population_passed = (
        v3.population_ok(v3_protocol, population_receipts, overlap_receipt)
        and population_receipts == v3_result["population_receipts"]
        and overlap_receipt == v3_result["overlap_receipt"]
        and sum(item["canonical_rows"] for item in population_receipts.values()) == 96241
    )
    result.update(
        {
            "overlap_receipt": overlap_receipt,
            "population_receipts": population_receipts,
            "population_v3_exact_match": population_passed,
            "pubmed_receipt": pubmed_receipt,
            "total_canonical_rows": sum(item["canonical_rows"] for item in population_receipts.values()),
        }
    )
    if not population_passed:
        result.update({"terminal": cannot_check})
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return

    arms_by_review: dict[str, Any] = {}
    effects_by_review: dict[str, Any] = {}
    for review in v3.REVIEWS:
        rows = review_rows[review]
        texts = [row["text"] for row in rows]
        identities = [row["record_identity"] for row in rows]
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        batch_size = max(10, int(np.ceil(0.002 * len(rows))))
        seed = v3.initial_seed(review, labels, identities)
        seed_hash = hashlib.sha256(
            "\n".join(identities[index] for index in seed).encode("ascii")
        ).hexdigest()
        expected_adapter = v3_result["arms_by_review"][review]["adapter_receipt"]
        adapter_receipt = {
            "batch_size": batch_size,
            "initial_seed_record_identities_sha256": seed_hash,
            "text_list_sha256": v3.hash_text_list(texts),
        }
        if adapter_receipt != expected_adapter:
            result.update(
                {
                    "adapter_mismatch": {"actual": adapter_receipt, "expected": expected_adapter, "review": review},
                    "terminal": cannot_check,
                }
            )
            out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            return

        print(f"representation_R0_vectorize review={review} batch_size={batch_size}", flush=True)
        r0_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=50000,
            sublinear_tf=True,
            lowercase=True,
        )
        matrices = {"R0": r0_vectorizer.fit_transform(texts)}
        print(f"representation_R1_vectorize review={review}", flush=True)
        r1_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            lowercase=True,
        )
        matrices["R1"] = r1_vectorizer.fit_transform(texts)

        review_arms: dict[str, Any] = {}
        for arm in ARM_NAMES:
            representation = arm.split("_")[0]
            print(f"arm_execute review={review} arm={arm}", flush=True)
            order, fits = execute_arm(v3, arm, matrices[representation], labels, seed, batch_size)
            review_arms[arm] = {
                "features": int(matrices[representation].shape[1]),
                "metrics": v3.order_metrics(order, labels),
                "model_fits": fits,
                "order_sha256": v3.order_sha256(order, identities),
            }
        review_arms["adapter_receipt"] = adapter_receipt
        arms_by_review[review] = review_arms
        effects_by_review[review] = component_effects(
            {arm: review_arms[arm]["metrics"] for arm in ARM_NAMES}
        )
        del matrices
        print(f"review_complete review={review}", flush=True)

    corner_reproduction: dict[str, Any] = {}
    corner_passed = True
    for review in v3.REVIEWS:
        pairs = {
            "R0_L0_equals_v3_candidate": (
                arms_by_review[review]["R0_L0"],
                v3_result["arms_by_review"][review]["FIXED_LOGREG_CONTROLLER"],
            ),
            "R1_L1_equals_v3_u4": (
                arms_by_review[review]["R1_L1"],
                v3_result["arms_by_review"][review]["ASREVIEW_ELAS_U4_CADENCE_MATCHED_COMPONENTS"],
            ),
        }
        corner_reproduction[review] = {}
        for name, (actual, expected) in pairs.items():
            passed = actual == expected
            corner_reproduction[review][name] = {"passed": passed}
            corner_passed = corner_passed and passed

    unweighted_mean_arm_metrics = {
        arm: {
            metric: mean([arms_by_review[review][arm]["metrics"][metric] for review in v3.REVIEWS])
            for metric in METRICS
        }
        for arm in ARM_NAMES
    }
    unweighted_mean_component_effects = {
        effect: {
            metric: mean([effects_by_review[review][effect][metric] for review in v3.REVIEWS])
            for metric in METRICS
        }
        for effect in ("representation_main_effect", "learner_balancer_main_effect", "interaction")
    }
    classification = classify(
        effects_by_review,
        unweighted_mean_component_effects,
        v3_result["mean_candidate_minus_comparator"]["recall_at_010"],
    )
    if not corner_passed:
        terminal = cannot_check
    elif classification["category"] == "STABLE_COMPONENT":
        terminal = (
            "P2_SWIFT_V4_POST_OUTCOME_FACTORIZATION_IDENTIFIES_STABLE_COMPONENT_"
            "REQUIRES_CONTENT_DISJOINT_OUTCOME_UNOPENED_FAMILY"
        )
    elif classification["category"] == "INTERACTION_DOMINANT":
        terminal = (
            "P2_SWIFT_V4_POST_OUTCOME_FACTORIZATION_IDENTIFIES_INTERACTION_"
            "REQUIRES_CONTENT_DISJOINT_OUTCOME_UNOPENED_FAMILY"
        )
    else:
        terminal = (
            "P2_SWIFT_V4_POST_OUTCOME_FACTORIZATION_NO_STABLE_ATTRIBUTION_"
            "REQUIRES_CONTENT_DISJOINT_OUTCOME_UNOPENED_FAMILY"
        )
    result.update(
        {
            "arms_by_review": arms_by_review,
            "classification": classification,
            "corner_reproduction": corner_reproduction,
            "corner_reproduction_passed": corner_passed,
            "effects_by_review": effects_by_review,
            "elapsed_seconds": time.monotonic() - start,
            "tail_diagnostics_definition": protocol_v4["estimands"]["tail_diagnostics"],
            "terminal": terminal,
            "unweighted_mean_arm_metrics": unweighted_mean_arm_metrics,
            "unweighted_mean_component_effects": unweighted_mean_component_effects,
        }
    )
    result["result_payload_sha256"] = canonical_json_sha256(result)
    out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--protocol-v4", type=Path, required=True)
    parser.add_argument("--implementation-v4", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(
        source_root=args.source_root.resolve(),
        target_root=args.target_root.resolve(),
        protocol_v4_path=args.protocol_v4.resolve(),
        implementation_v4_path=args.implementation_v4.resolve(),
        out_path=args.out.resolve(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
