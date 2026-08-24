#!/usr/bin/env python3
"""Execute the frozen Zenodo 10423427 V2 schema-repair successor.

The public source has no header.  A schema preflight therefore exposed the
first labelled row before the protocol was frozen.  This runner verifies and
excludes that exact raw row before parsing any remaining row.  Its outputs are
development evidence only, never outcome-blind confirmation.  V2 excludes the
two noncanonical class rows and retains the earliest canonical row within each
of the three class-free identity collisions diagnosed by V1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier


def hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def remove_line_ending(raw_line: bytes) -> bytes:
    if raw_line.endswith(b"\n"):
        raw_line = raw_line[:-1]
        if raw_line.endswith(b"\r"):
            raw_line = raw_line[:-1]
    return raw_line


def identity_hash(title: str, pmid: str, abstract: str, mesh: str) -> str:
    value = "\t".join((title, pmid, abstract, mesh))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_seed_key(source_id: str, record_identity: str) -> str:
    return hashlib.sha256(f"{source_id}:{record_identity}".encode("utf-8")).hexdigest()


def normalized_text(title: str, abstract: str, mesh: str) -> str:
    return " ".join(f"{title} {abstract} {mesh.replace('|', ' ')}".split())


def parse_source(path: Path, protocol: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    expected_excluded = protocol["preflight_incident"]["excluded_first_raw_line_sha256"]
    rows: list[dict[str, Any]] = []
    malformed_field_rows = 0
    noncanonical_class_rows = 0
    five_field_post_incident_rows = 0
    canonical_class_rows = 0
    duplicate_identity_excess_rows = 0
    seen_identities: set[str] = set()
    total_raw_lines = 0
    excluded_hash = ""
    with path.open("rb") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            total_raw_lines += 1
            body = remove_line_ending(raw_line)
            if line_number == 1:
                excluded_hash = hashlib.sha256(body).hexdigest()
                # Do not decode or print the contaminated row.  Its raw hash is
                # the complete exclusion identity frozen by the protocol.
                continue
            try:
                fields = body.decode("utf-8", errors="strict").split("\t")
            except UnicodeDecodeError:
                malformed_field_rows += 1
                continue
            if len(fields) != 5:
                malformed_field_rows += 1
                continue
            five_field_post_incident_rows += 1
            title, pmid, abstract, label, mesh = fields
            if label not in ("include", "exclude"):
                noncanonical_class_rows += 1
                continue
            canonical_class_rows += 1
            record_identity = identity_hash(title, pmid, abstract, mesh)
            if record_identity in seen_identities:
                duplicate_identity_excess_rows += 1
                continue
            seen_identities.add(record_identity)
            rows.append(
                {
                    "record_identity": record_identity,
                    "label": 1 if label == "include" else 0,
                    "text": normalized_text(title, abstract, mesh),
                }
            )
    receipt = {
        "total_raw_lines": total_raw_lines,
        "excluded_rows": 1,
        "excluded_first_raw_line_sha256_expected": expected_excluded,
        "excluded_first_raw_line_sha256_actual": excluded_hash,
        "excluded_first_raw_line_hash_passed": excluded_hash == expected_excluded,
        "eligible_rows": len(rows),
        "five_field_post_incident_rows": five_field_post_incident_rows,
        "canonical_class_rows": canonical_class_rows,
        "malformed_field_rows": malformed_field_rows,
        "noncanonical_class_rows_excluded": noncanonical_class_rows,
        "duplicate_identity_excess_rows_excluded": duplicate_identity_excess_rows,
        "duplicate_record_identities_after_repair": 0,
    }
    return rows, receipt


def order_hash(order: list[int], identities: list[str]) -> str:
    body = "\n".join(identities[index] for index in order)
    return hashlib.sha256(body.encode("ascii")).hexdigest()


def order_metrics(order: list[int], y: np.ndarray) -> dict[str, float]:
    if len(order) != len(y) or len(set(order)) != len(y):
        raise ValueError("arm ordering must contain every record exactly once")
    total_included = int(y.sum())
    if total_included == 0:
        raise ValueError("at least one included record is required")
    cumulative = np.cumsum(y[order])

    def recall_at(fraction: float) -> float:
        screened = max(1, math.ceil(fraction * len(order)))
        return float(cumulative[screened - 1] / total_included)

    target = math.ceil(0.95 * total_included)
    effort_index = int(np.searchsorted(cumulative, target, side="left")) + 1
    effort = effort_index / len(order)
    return {
        "recall_at_005": recall_at(0.05),
        "recall_at_010": recall_at(0.10),
        "recall_at_020": recall_at(0.20),
        "fraction_screened_at_95_recall": effort,
        "wss_at_95": 0.95 - effort,
    }


def active_order(
    x: Any,
    y: np.ndarray,
    initial: list[int],
    batch_size: int,
    seed: int,
    identities: list[str],
) -> list[int]:
    selected = list(initial)
    remaining = set(range(len(y))) - set(selected)
    while remaining:
        model = SGDClassifier(
            loss="log_loss",
            class_weight="balanced",
            alpha=1e-5,
            max_iter=2000,
            tol=1e-4,
            random_state=seed,
        )
        model.fit(x[selected], y[selected])
        pool = sorted(remaining, key=lambda index: identities[index])
        scores = model.predict_proba(x[pool])[:, 1]
        ranked = sorted(
            zip(pool, scores),
            key=lambda pair: (-float(pair[1]), identities[pair[0]]),
        )
        chosen = [index for index, _ in ranked[:batch_size]]
        selected.extend(chosen)
        remaining.difference_update(chosen)
    return selected


def execute(protocol_path: Path, implementation_path: Path, data_path: Path, out_path: Path) -> None:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    implementation = json.loads(implementation_path.read_text(encoding="utf-8"))
    source = protocol["source"]
    source_receipt = {
        "path_basename": data_path.name,
        "bytes_expected": int(source["bytes"]),
        "bytes_actual": data_path.stat().st_size if data_path.is_file() else None,
        "md5_expected": source["md5"],
        "md5_actual": hash_file(data_path, "md5") if data_path.is_file() else None,
    }
    source_receipt["bytes_passed"] = source_receipt["bytes_actual"] == source_receipt["bytes_expected"]
    source_receipt["md5_passed"] = source_receipt["md5_actual"] == source_receipt["md5_expected"]

    rows: list[dict[str, Any]] = []
    parse_receipt: dict[str, Any] = {}
    if source_receipt["bytes_passed"] and source_receipt["md5_passed"]:
        rows, parse_receipt = parse_source(data_path, protocol)
    identities = [row["record_identity"] for row in rows]
    sanitation = protocol["sanitation"]
    binding_ok = bool(rows) and all(
        (
            source_receipt["bytes_passed"],
            source_receipt["md5_passed"],
            parse_receipt.get("excluded_first_raw_line_hash_passed", False),
            parse_receipt.get("total_raw_lines") == int(source["declared_rows"]),
            parse_receipt.get("five_field_post_incident_rows") == int(source["declared_rows"]) - 1,
            parse_receipt.get("canonical_class_rows")
            == int(source["declared_rows"]) - 1 - int(sanitation["noncanonical_class_rows_expected"]),
            parse_receipt.get("eligible_rows") == int(sanitation["eligible_unique_records_expected"]),
            parse_receipt.get("malformed_field_rows") == 0,
            parse_receipt.get("noncanonical_class_rows_excluded")
            == int(sanitation["noncanonical_class_rows_expected"]),
            parse_receipt.get("duplicate_identity_excess_rows_excluded")
            == int(sanitation["duplicate_identity_excess_rows_expected"]),
            parse_receipt.get("duplicate_record_identities_after_repair") == 0,
            len(set(identities)) == len(identities),
        )
    )

    result: dict[str, Any] = {
        "schema_version": protocol["schema_version"],
        "claim_scope": protocol["claim_scope"],
        "protocol_sha256": hash_file(protocol_path, "sha256"),
        "implementation_freeze_sha256": hash_file(implementation_path, "sha256"),
        "source_receipt": source_receipt,
        "parse_receipt": parse_receipt,
        "preflight_incident": protocol["preflight_incident"],
        "outcome_blind_before_protocol": False,
        "forbidden_claims": protocol["forbidden_claims"],
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    if not binding_ok:
        result.update(
            {
                "terminal": protocol["cannot_check_terminal"],
                "gates": {
                    "G1_BINDING": False,
                    "G2_ABSOLUTE": False,
                    "G3_INCREMENTAL": False,
                    "G4_WORK_SAVING": False,
                    "G5_NO_RANDOM_HARM": False,
                },
                "arms": {},
            }
        )
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return

    ordered_rows = sorted(rows, key=lambda row: row["record_identity"])
    identities = [row["record_identity"] for row in ordered_rows]
    texts = [row["text"] for row in ordered_rows]
    y = np.array([row["label"] for row in ordered_rows], dtype=int)
    source_id = str(source["record_id"])
    positives = [index for index, value in enumerate(y) if value == 1]
    negatives = [index for index, value in enumerate(y) if value == 0]
    included_seed = min(positives, key=lambda index: stable_seed_key(source_id, identities[index]))
    excluded_seed = min(negatives, key=lambda index: stable_seed_key(source_id, identities[index]))
    initial = [included_seed, excluded_seed]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=50000,
        sublinear_tf=True,
        lowercase=True,
    )
    x = vectorizer.fit_transform(texts)
    centroid_scores = (x @ x[included_seed].T).toarray().ravel()
    static_rest = sorted(
        (index for index in range(len(y)) if index not in initial),
        key=lambda index: (-float(centroid_scores[index]), identities[index]),
    )
    static = initial + static_rest

    random_runs: list[dict[str, Any]] = []
    deterministic_rest = sorted(
        (index for index in range(len(y)) if index not in initial),
        key=lambda index: identities[index],
    )
    for seed in protocol["random_seeds"]:
        rest = list(deterministic_rest)
        random.Random(seed).shuffle(rest)
        order = initial + rest
        random_runs.append(
            {
                "seed": seed,
                "metrics": order_metrics(order, y),
                "order_sha256": order_hash(order, identities),
            }
        )
    metric_names = tuple(random_runs[0]["metrics"])
    random_mean = {
        metric: float(np.mean([run["metrics"][metric] for run in random_runs]))
        for metric in metric_names
    }
    random_ranges = {
        metric: {
            "min": float(min(run["metrics"][metric] for run in random_runs)),
            "max": float(max(run["metrics"][metric] for run in random_runs)),
        }
        for metric in metric_names
    }

    batch_size = max(10, math.ceil(0.002 * len(y)))
    active = active_order(
        x,
        y,
        initial,
        batch_size,
        int(protocol["active_model"]["random_state"]),
        identities,
    )
    arms = {
        "RANDOM": {
            "metrics": random_mean,
            "metric_ranges": random_ranges,
            "runs": random_runs,
        },
        "STATIC_SEED_CENTROID": {
            "metrics": order_metrics(static, y),
            "order_sha256": order_hash(static, identities),
        },
        "ACTIVE_LOGREG": {
            "metrics": order_metrics(active, y),
            "order_sha256": order_hash(active, identities),
        },
    }
    active_metrics = arms["ACTIVE_LOGREG"]["metrics"]
    strongest_comparator = max(
        ("RANDOM", "STATIC_SEED_CENTROID"),
        key=lambda arm: float(arms[arm]["metrics"]["recall_at_010"]),
    )
    comparator_metrics = arms[strongest_comparator]["metrics"]
    gates = {
        "G1_BINDING": True,
        "G2_ABSOLUTE": active_metrics["recall_at_010"] >= 0.50,
        "G3_INCREMENTAL": active_metrics["recall_at_010"] - comparator_metrics["recall_at_010"] >= 0.10,
        "G4_WORK_SAVING": active_metrics["wss_at_95"] > 0.0,
        "G5_NO_RANDOM_HARM": active_metrics["recall_at_010"] >= random_mean["recall_at_010"],
    }
    terminal = protocol["positive_terminal"] if all(gates.values()) else protocol["negative_terminal"]
    result.update(
        {
            "terminal": terminal,
            "gates": gates,
            "eligible_records": len(y),
            "included_records": int(y.sum()),
            "excluded_records": int(len(y) - y.sum()),
            "prevalence": float(y.mean()),
            "tfidf_features": int(x.shape[1]),
            "active_batch_size": batch_size,
            "initial_seed_record_identities_sha256": hashlib.sha256(
                "\n".join(identities[index] for index in initial).encode("ascii")
            ).hexdigest(),
            "strongest_comparator_at_010": strongest_comparator,
            "active_minus_strongest_comparator_recall_at_010": (
                active_metrics["recall_at_010"] - comparator_metrics["recall_at_010"]
            ),
            "arms": arms,
        }
    )
    out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--implementation", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(args.protocol, args.implementation, args.data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
