#!/usr/bin/env python3
"""Run the KIFMS V8 u4 donor-envelopment development study.

KIFMS outcomes are open development data.  This runner never describes the
cross-fitted estimate as confirmation and emits no source text or row labels.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import math
import platform
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC


BASE_METRICS = (
    "recall_at_005",
    "recall_at_010",
    "recall_at_020",
    "fraction_screened_at_95_recall",
    "wss_at_95",
)
METRICS = BASE_METRICS + ("cre20",)
LABEL_HEADERS = ["noisy_inclusion", "expert_inclusion", "fulltext_inclusion"]
ALLOWED_LABEL_TOKENS = {
    "0": 0,
    "0.0": 0,
    "false": 0,
    "1": 1,
    "1.0": 1,
    "true": 1,
}
FAMILY_ORDER = ("F1_WORD_PRUNED", "F2_TITLE_EMPHASIS", "F3_CHAR_MORPHOLOGY")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_lines(values: list[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("ascii")).hexdigest()


def canonical_json_sha256(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_pmid(value: Any) -> str:
    text = normalize_text(value)
    match = re.search(r"(\d+)(?:/)?$", text)
    return match.group(1) if match else text


def content_identity(title: Any, abstract: Any) -> str:
    text = f"{normalize_text(title)} {normalize_text(abstract)}"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_label(raw: Any, location: str) -> int:
    token = normalize_text(raw).casefold()
    if token not in ALLOWED_LABEL_TOKENS:
        raise ValueError(f"Unmapped expert_inclusion value at {location}: {token!r}")
    return ALLOWED_LABEL_TOKENS[token]


def mean(values: list[float]) -> float:
    return float(np.mean(values))


def verify_bindings(
    packet: Path, v6: Path, v7: Path, stage: Path
) -> tuple[dict[str, Any], bool]:
    implementation = json.loads((packet / "IMPLEMENTATION_FREEZE_V8.json").read_text())
    rights = json.loads((v6 / "SOURCE_RIGHTS_PROVENANCE_RECEIPT_V6.json").read_text())
    fixed_paths = {
        "protocol_v8": packet / "PROTOCOL_V8.json",
        "runner_v8": Path(__file__).resolve(),
        "pinned_active_core_v3": packet / "pinned_active_core_v3.py",
        "v7_result": v7 / "RESULT_V7.json",
        "v7_protocol": v7 / "PROTOCOL_FREEZE_V7.json",
        "v6_overlap": v6 / "LABEL_BLIND_OVERLAP_RECEIPT_V6.json",
        "v6_rights": v6 / "SOURCE_RIGHTS_PROVENANCE_RECEIPT_V6.json",
    }
    fixed: dict[str, Any] = {}
    passed = True
    for role, path in fixed_paths.items():
        expected = implementation["fixed_sha256"][role]
        actual = sha256_file(path) if path.is_file() else None
        ok = actual == expected
        fixed[role] = {"expected": expected, "actual": actual, "passed": ok}
        passed = passed and ok

    staged: dict[str, Any] = {}
    for source in rights["source"]["csv_files"]:
        path = stage / source["filename"]
        actual_hash = sha256_file(path) if path.is_file() else None
        actual_bytes = path.stat().st_size if path.is_file() else None
        ok = actual_hash == source["sha256"] and actual_bytes == source["bytes"]
        staged[source["filename"]] = {
            "bytes_expected": source["bytes"],
            "bytes_actual": actual_bytes,
            "sha256_expected": source["sha256"],
            "sha256_actual": actual_hash,
            "passed": ok,
        }
        passed = passed and ok
    return {"fixed": fixed, "staged_sources": staged, "passed": passed}, passed


def read_with_labels(
    stage: Path, overlap: dict[str, Any]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    reviews: dict[str, list[dict[str, Any]]] = {}
    receipt: dict[str, Any] = {}
    for review in overlap["review_units"]:
        expected = overlap["per_review"][review]
        path = stage / expected["filename"]
        rows: list[dict[str, Any]] = []
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle, delimiter=";")
            header = next(reader)
            if header[:3] != LABEL_HEADERS:
                raise ValueError(f"Unexpected label header boundary in {path}: {header[:3]}")
            positions = {name: header.index(name) for name in ("key", "title", "abstract", "pubmed_id")}
            for row_number, row in enumerate(reader, start=2):
                title = normalize_text(row[positions["title"]])
                abstract = normalize_text(row[positions["abstract"]])
                key = normalize_text(row[positions["key"]]) or f"row-{row_number:09d}"
                rows.append(
                    {
                        "key": key,
                        "row_number": row_number,
                        "content_id": content_identity(title, abstract),
                        "empty_text": not (title or abstract),
                        "pmid": normalize_pmid(row[positions["pubmed_id"]]),
                        "label": parse_label(row[1], f"{path.name}:{row_number}"),
                        "title": title,
                        "abstract": abstract,
                        "text": f"{title} {abstract}".strip(),
                    }
                )
        if len(rows) != expected["raw_rows"]:
            raise ValueError(f"Raw row mismatch for {review}: {len(rows)}")
        reviews[review] = rows
        receipt[review] = {
            "raw_rows": len(rows),
            "header_sha256": hashlib.sha256("\0".join(header).encode("utf-8")).hexdigest(),
        }
    return reviews, receipt


def within_review_canonicalize(
    source: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    output: dict[str, list[dict[str, Any]]] = {}
    receipts: dict[str, Any] = {}
    for review, source_rows in source.items():
        seen_content: set[str] = set()
        seen_pmids: set[str] = set()
        retained: list[dict[str, Any]] = []
        empty = duplicate_content = duplicate_pmid = duplicate_label_conflict = 0
        first_label: dict[str, int] = {}
        for row in sorted(source_rows, key=lambda value: (value["key"], value["row_number"])):
            if row["empty_text"]:
                empty += 1
                continue
            if row["content_id"] in seen_content:
                duplicate_content += 1
                if first_label[row["content_id"]] != row["label"]:
                    duplicate_label_conflict += 1
                continue
            if row["pmid"] and row["pmid"] in seen_pmids:
                duplicate_pmid += 1
                continue
            seen_content.add(row["content_id"])
            first_label[row["content_id"]] = row["label"]
            if row["pmid"]:
                seen_pmids.add(row["pmid"])
            retained.append(row)
        output[review] = retained
        receipts[review] = {
            "empty_text_rows": empty,
            "within_review_duplicate_content_excess": duplicate_content,
            "within_review_duplicate_pmid_excess_after_content_dedup": duplicate_pmid,
            "duplicate_content_label_conflicts": duplicate_label_conflict,
            "provisional_unique_rows": len(retained),
        }
    return output, receipts


def final_after_candidate_external_drop(
    provisional: dict[str, list[dict[str, Any]]], drop_review: str, drop_content: str
) -> dict[str, list[dict[str, Any]]]:
    after_external = {
        review: [
            row for row in rows if not (review == drop_review and row["content_id"] == drop_content)
        ]
        for review, rows in provisional.items()
    }
    content_owners: dict[str, set[str]] = defaultdict(set)
    pmid_owners: dict[str, set[str]] = defaultdict(set)
    for review, rows in after_external.items():
        for row in rows:
            content_owners[row["content_id"]].add(review)
            if row["pmid"]:
                pmid_owners[row["pmid"]].add(review)
    shared_content = {value for value, owners in content_owners.items() if len(owners) > 1}
    shared_pmids = {value for value, owners in pmid_owners.items() if len(owners) > 1}
    return {
        review: [
            row
            for row in rows
            if row["content_id"] not in shared_content
            and (not row["pmid"] or row["pmid"] not in shared_pmids)
        ]
        for review, rows in after_external.items()
    }


def matches_v6_population(
    final: dict[str, list[dict[str, Any]]], overlap: dict[str, Any]
) -> bool:
    for review, rows in final.items():
        expected = overlap["per_review"][review]
        if len(rows) != expected["canonical_rows"]:
            return False
        if hash_lines(sorted(row["content_id"] for row in rows)) != expected["canonical_content_set_sha256"]:
            return False
        if hash_lines(sorted(row["pmid"] for row in rows if row["pmid"])) != expected["canonical_pmid_set_sha256"]:
            return False
    union_content = sorted({row["content_id"] for rows in final.values() for row in rows})
    union_pmids = sorted({row["pmid"] for rows in final.values() for row in rows if row["pmid"]})
    return (
        sum(len(rows) for rows in final.values()) == overlap["total_canonical_rows"]
        and hash_lines(union_content) == overlap["canonical_union_content_set_sha256"]
        and hash_lines(union_pmids) == overlap["canonical_union_pmid_set_sha256"]
    )


def reconstruct_frozen_population(
    provisional: dict[str, list[dict[str, Any]]], overlap: dict[str, Any]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    candidates: list[tuple[str, str, dict[str, list[dict[str, Any]]]]] = []
    for review, rows in provisional.items():
        for row in rows:
            final = final_after_candidate_external_drop(provisional, review, row["content_id"])
            if matches_v6_population(final, overlap):
                candidates.append((review, row["content_id"], final))
    if len(candidates) != 1:
        raise ValueError(f"Frozen V6 population reconstruction is not unique: {len(candidates)} candidates")
    drop_review, drop_content, final = candidates[0]
    return final, {
        "unique_external_exclusion_reconstructed": True,
        "candidate_count": 1,
        "excluded_review": drop_review,
        "excluded_content_identity_sha256": hashlib.sha256(drop_content.encode("ascii")).hexdigest(),
        "canonical_rows": sum(len(rows) for rows in final.values()),
        "canonical_union_content_set_sha256": hash_lines(
            sorted({row["content_id"] for rows in final.values() for row in rows})
        ),
    }


def cre20(order: list[int], labels: np.ndarray) -> float:
    positives = int(labels.sum())
    if positives <= 0 or positives >= len(labels):
        raise ValueError("CRE20 requires both classes")
    total = 0.0
    n = len(order)
    for i, index in enumerate(order, start=1):
        total += int(labels[index]) * max(0.20 - i / n, 0.0)
    return total / (0.20 * positives)


def u4_model() -> LinearSVC:
    return LinearSVC(loss="squared_hinge", C=0.11, random_state=20260823)


def fit_u4(model: LinearSVC, matrix: Any, labels: np.ndarray, selected: list[int]) -> None:
    selected_labels = labels[selected]
    positives = int(selected_labels.sum())
    negatives = len(selected_labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("u4 requires both observed classes")
    weights = np.where(selected_labels == 1, 1.0, positives / (9.8 * negatives))
    weights = weights * (len(weights) / float(weights.sum()))
    model.fit(matrix[selected], selected_labels, sample_weight=weights)


def zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    scale = float(values.std(ddof=0))
    if not math.isfinite(scale) or scale <= 1e-12:
        return np.zeros_like(values)
    return (values - float(values.mean())) / scale


def complete_enveloped_order(
    base_matrix: Any,
    residual_matrix: Any,
    labels: np.ndarray,
    seed: list[int],
    batch_size: int,
    alpha: float,
) -> tuple[list[int], int]:
    selected = list(seed)
    remaining = np.ones(len(labels), dtype=bool)
    remaining[selected] = False
    iterations = 0
    while remaining.any():
        base_model = u4_model()
        residual_model = u4_model()
        fit_u4(base_model, base_matrix, labels, selected)
        fit_u4(residual_model, residual_matrix, labels, selected)
        pool = np.flatnonzero(remaining)
        base_score = np.asarray(base_model.decision_function(base_matrix[pool]), dtype=float)
        residual_score = np.asarray(residual_model.decision_function(residual_matrix[pool]), dtype=float)
        base_z = zscore(base_score)
        residual_z = zscore(residual_score)
        combined = base_z + alpha * (residual_z - base_z)
        ranked_pool = pool[np.argsort(-combined, kind="stable")]
        chosen = ranked_pool[:batch_size]
        selected.extend(int(index) for index in chosen)
        remaining[chosen] = False
        iterations += 1
    return selected, iterations


def configuration_id(family: str, alpha: float) -> str:
    return f"{family}_A{int(round(alpha * 1000)):03d}"


def build_residual_matrices(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, int]]:
    texts = [row["text"] for row in rows]
    title_emphasis = [f'{row["title"]} {row["title"]} {row["abstract"]}'.strip() for row in rows]
    matrices = {
        "F1_WORD_PRUNED": TfidfVectorizer(
            ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True, lowercase=True
        ).fit_transform(texts),
        "F2_TITLE_EMPHASIS": TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True, lowercase=True
        ).fit_transform(title_emphasis),
        "F3_CHAR_MORPHOLOGY": TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            max_features=30000,
            sublinear_tf=True,
            lowercase=True,
        ).fit_transform(texts),
    }
    return matrices, {family: int(matrix.shape[1]) for family, matrix in matrices.items()}


def metrics_for_order(active: Any, order: list[int], labels: np.ndarray) -> dict[str, float]:
    metrics = active.order_metrics(order, labels)
    metrics["cre20"] = cre20(order, labels)
    return metrics


def delta_metrics(candidate: dict[str, float], base: dict[str, float]) -> dict[str, float]:
    return {metric: candidate[metric] - base[metric] for metric in METRICS}


def exact_metric_mapping_equal(left: dict[str, float], right: dict[str, float]) -> bool:
    return all(left[metric] == right[metric] for metric in METRICS)


def select_nested_loro(
    reviews: tuple[str, ...],
    configurations: tuple[str, ...],
    grid: dict[str, dict[str, Any]],
    configuration_meta: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    outer: dict[str, Any] = {}
    for held_out in reviews:
        training = tuple(review for review in reviews if review != held_out)
        support: dict[str, Any] = {}
        for config in configurations:
            cre = mean([grid[review][config]["delta_vs_u4"]["cre20"] for review in training])
            wss = mean([grid[review][config]["delta_vs_u4"]["wss_at_95"] for review in training])
            worst_r10 = min(grid[review][config]["delta_vs_u4"]["recall_at_010"] for review in training)
            passed = cre > 0 and wss >= 0 and worst_r10 >= -0.05
            support[config] = {
                "mean_delta_cre20": cre,
                "mean_delta_wss95": wss,
                "worst_review_delta_r10": worst_r10,
                "passed": passed,
            }
        supported = [config for config in configurations if support[config]["passed"]]
        if supported:
            def key(config: str) -> tuple[float, float, float, float, int]:
                stats = support[config]
                meta = configuration_meta[config]
                return (
                    stats["mean_delta_cre20"],
                    stats["mean_delta_wss95"],
                    stats["worst_review_delta_r10"],
                    -meta["alpha"],
                    -FAMILY_ORDER.index(meta["family"]),
                )

            selected = max(supported, key=key)
            held_metrics = grid[held_out][selected]["metrics"]
            held_delta = grid[held_out][selected]["delta_vs_u4"]
            fallback = False
            order_sha = grid[held_out][selected]["order_sha256"]
        else:
            selected = "EXACT_U4_FALLBACK"
            held_metrics = grid[held_out]["EXACT_U4"]["metrics"]
            held_delta = {metric: 0.0 for metric in METRICS}
            fallback = True
            order_sha = grid[held_out]["EXACT_U4"]["order_sha256"]
        outer[held_out] = {
            "training_reviews": list(training),
            "support_by_configuration": support,
            "supported_configuration_count": len(supported),
            "selected": selected,
            "exact_u4_fallback": fallback,
            "held_out_metrics": held_metrics,
            "held_out_delta_vs_u4": held_delta,
            "held_out_order_sha256": order_sha,
        }

    fallback_count = sum(item["exact_u4_fallback"] for item in outer.values())
    selected_counts: dict[str, int] = {config: 0 for config in configurations}
    selected_counts["EXACT_U4_FALLBACK"] = fallback_count
    for item in outer.values():
        if not item["exact_u4_fallback"]:
            selected_counts[item["selected"]] += 1
    deltas = {review: item["held_out_delta_vs_u4"] for review, item in outer.items()}
    aggregate = {
        "mean_delta_vs_u4": {
            metric: mean([deltas[review][metric] for review in reviews]) for metric in METRICS
        },
        "worst_review_delta_r10": min(deltas[review]["recall_at_010"] for review in reviews),
        "strictly_positive_review_counts": {
            "cre20": sum(deltas[review]["cre20"] > 0 for review in reviews),
            "r10": sum(deltas[review]["recall_at_010"] > 0 for review in reviews),
        },
        "fallback_count": fallback_count,
        "fallback_fraction": fallback_count / len(reviews),
        "selected_counts": selected_counts,
        "development_safety_checks": {
            "mean_cre20_positive": mean([deltas[review]["cre20"] for review in reviews]) > 0,
            "mean_wss95_nonnegative": mean([deltas[review]["wss_at_95"] for review in reviews]) >= 0,
            "worst_review_r10_at_least_minus_0_05": min(
                deltas[review]["recall_at_010"] for review in reviews
            )
            >= -0.05,
        },
    }
    return outer, aggregate


def execute(packet: Path, v6: Path, v7: Path, stage: Path, out: Path) -> None:
    start = time.monotonic()
    protocol = json.loads((packet / "PROTOCOL_V8.json").read_text())
    overlap = json.loads((v6 / "LABEL_BLIND_OVERLAP_RECEIPT_V6.json").read_text())
    v7_result = json.loads((v7 / "RESULT_V7.json").read_text())
    binding, binding_ok = verify_bindings(packet, v6, v7, stage)
    result: dict[str, Any] = {
        "identity": protocol["identity"],
        "scope": protocol["scope"],
        "execution_started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "binding_receipt": binding,
        "custody": {
            "mode": "SAME_WORKSPACE_OPEN_KIFMS_DEVELOPMENT",
            "independent_custody": False,
            "confirmatory_claim_permitted": False,
            "source_disjoint_claim_permitted": False,
        },
        "preserved_terminal": protocol["preserved_terminal"],
        "forbidden_claims": protocol["forbidden_claims"],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    if not binding_ok:
        result["terminal"] = protocol["development_decision"]["binding_or_base_drift"]
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return

    source_rows, source_receipt = read_with_labels(stage, overlap)
    provisional, canonicalization_receipt = within_review_canonicalize(source_rows)
    final, reconstruction_receipt = reconstruct_frozen_population(provisional, overlap)
    active = import_module(packet / "pinned_active_core_v3.py", "p2_kifms_v8_active")
    reviews = tuple(overlap["review_units"])
    declared_families = tuple(item["id"] for item in protocol["residual_families"])
    if declared_families != FAMILY_ORDER:
        raise ValueError("Residual family order drift")
    strengths = tuple(float(value) for value in protocol["residual_score_definition"]["strengths"])
    configurations = tuple(configuration_id(family, alpha) for family in FAMILY_ORDER for alpha in strengths)
    if len(configurations) != protocol["configuration_count"]:
        raise ValueError("Configuration count drift")
    configuration_meta = {
        configuration_id(family, alpha): {"family": family, "alpha": alpha}
        for family in FAMILY_ORDER
        for alpha in strengths
    }

    grid: dict[str, dict[str, Any]] = {}
    class_counts: dict[str, Any] = {}
    u4_identity_pass_by_review: dict[str, bool] = {}
    for review in reviews:
        rows = sorted(final[review], key=lambda row: active.record_identity(review, row["content_id"]))
        texts = [row["text"] for row in rows]
        identities = [active.record_identity(review, row["content_id"]) for row in rows]
        labels = np.asarray([row["label"] for row in rows], dtype=np.int8)
        class_counts[review] = {"negative": int((labels == 0).sum()), "positive": int(labels.sum())}
        if class_counts[review]["negative"] == 0 or class_counts[review]["positive"] == 0:
            raise ValueError(f"Both classes required in {review}")
        batch_size = max(10, math.ceil(0.002 * len(rows)))
        seed = active.initial_seed(review, labels, identities)
        base_matrix = TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, max_df=0.95, sublinear_tf=True, lowercase=True
        ).fit_transform(texts)
        base_order, base_fits = active.complete_active_order(
            x=base_matrix,
            labels=labels,
            seed=seed,
            batch_size=batch_size,
            model_factory=u4_model,
            score_function=lambda model, pool: model.decision_function(pool),
            weight_ratio=9.8,
        )
        base_metrics = metrics_for_order(active, base_order, labels)
        base_order_sha = active.order_sha256(base_order, identities)
        v7_base = v7_result["arms_by_review"][review]["R1_L1"]
        identity_pass = (
            base_order_sha == v7_base["order_sha256"]
            and exact_metric_mapping_equal(base_metrics, v7_base["metrics"])
        )
        u4_identity_pass_by_review[review] = identity_pass
        grid[review] = {
            "EXACT_U4": {
                "features": int(base_matrix.shape[1]),
                "metrics": base_metrics,
                "model_fits": base_fits,
                "order_sha256": base_order_sha,
                "v7_R1_L1_identity_passed": identity_pass,
            }
        }
        residual_matrices, feature_counts = build_residual_matrices(rows)
        for family in FAMILY_ORDER:
            for alpha in strengths:
                config = configuration_id(family, alpha)
                order, iterations = complete_enveloped_order(
                    base_matrix=base_matrix,
                    residual_matrix=residual_matrices[family],
                    labels=labels,
                    seed=seed,
                    batch_size=batch_size,
                    alpha=alpha,
                )
                metrics = metrics_for_order(active, order, labels)
                grid[review][config] = {
                    "family": family,
                    "alpha": alpha,
                    "residual_features": feature_counts[family],
                    "metrics": metrics,
                    "delta_vs_u4": delta_metrics(metrics, base_metrics),
                    "active_iterations": iterations,
                    "model_fits": 2 * iterations,
                    "order_sha256": active.order_sha256(order, identities),
                }
        grid[review]["adapter_receipt"] = {
            "rows": len(rows),
            "batch_size": batch_size,
            "initial_seed_record_identities_sha256": hashlib.sha256(
                "\n".join(identities[index] for index in seed).encode("ascii")
            ).hexdigest(),
            "text_list_sha256": active.hash_text_list(texts),
        }
        print(f"review_complete review={review} configs={len(configurations)}", flush=True)

    if not all(u4_identity_pass_by_review.values()):
        result.update(
            {
                "source_receipt": source_receipt,
                "canonicalization_receipt": canonicalization_receipt,
                "population_reconstruction_receipt": reconstruction_receipt,
                "u4_identity_pass_by_review": u4_identity_pass_by_review,
                "terminal": protocol["development_decision"]["binding_or_base_drift"],
            }
        )
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return

    outer, aggregate = select_nested_loro(
        reviews=reviews,
        configurations=configurations,
        grid=grid,
        configuration_meta=configuration_meta,
    )
    any_residual = aggregate["fallback_count"] < len(reviews)
    terminal_key = "one_or_more_outer_folds_select_residual" if any_residual else "no_residual_survives"
    result.update(
        {
            "source_receipt": source_receipt,
            "canonicalization_receipt": canonicalization_receipt,
            "population_reconstruction_receipt": reconstruction_receipt,
            "class_counts": class_counts,
            "u4_identity_pass_by_review": u4_identity_pass_by_review,
            "u4_identity_passed_all_reviews": True,
            "configuration_meta": configuration_meta,
            "complete_development_grid": grid,
            "nested_loro_by_held_out_review": outer,
            "cross_fitted_aggregate": aggregate,
            "elapsed_seconds": time.monotonic() - start,
            "execution_completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "terminal": protocol["development_decision"][terminal_key],
        }
    )
    result["result_payload_sha256"] = canonical_json_sha256(result)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--v6", type=Path, required=True)
    parser.add_argument("--v7", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("RESULT_V8.json"))
    args = parser.parse_args()
    execute(args.packet.resolve(), args.v6.resolve(), args.v7.resolve(), args.stage.resolve(), args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
