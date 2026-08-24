#!/usr/bin/env python3
"""Execute the frozen post-V2 active-comparator audit on Zenodo 10423427.

This is a one-pool, post-outcome comparator audit.  It preserves the retained
V1 binding failure and V2 terminal, reproduces the known V2 candidate, and
only then evaluates the prospectively registered cadence-matched ASReview
ELAS u4/u3 model configurations.  It is not a confirmation or transport test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any, Callable

import numpy as np
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC


def hash_file(path: Path, algorithm: str = "sha256") -> str:
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
    return hashlib.sha256("\t".join((title, pmid, abstract, mesh)).encode("utf-8")).hexdigest()


def stable_seed_key(source_id: str, record_identity: str) -> str:
    return hashlib.sha256(f"{source_id}:{record_identity}".encode("utf-8")).hexdigest()


def normalize(value: str) -> str:
    return " ".join(value.split())


def parse_source(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    receipt = {
        "total_raw_lines": 0,
        "excluded_incident_rows": 0,
        "five_field_post_incident_rows": 0,
        "malformed_field_rows": 0,
        "noncanonical_class_rows_excluded": 0,
        "duplicate_identity_excess_rows_excluded": 0,
    }
    excluded_hash = ""
    with path.open("rb") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            receipt["total_raw_lines"] += 1
            body = remove_line_ending(raw_line)
            if line_number == 1:
                excluded_hash = hashlib.sha256(body).hexdigest()
                receipt["excluded_incident_rows"] += 1
                continue
            try:
                fields = body.decode("utf-8", errors="strict").split("\t")
            except UnicodeDecodeError:
                receipt["malformed_field_rows"] += 1
                continue
            if len(fields) != 5:
                receipt["malformed_field_rows"] += 1
                continue
            receipt["five_field_post_incident_rows"] += 1
            title, pmid, abstract, label, mesh = fields
            if label not in ("include", "exclude"):
                receipt["noncanonical_class_rows_excluded"] += 1
                continue
            identity = identity_hash(title, pmid, abstract, mesh)
            if identity in seen:
                receipt["duplicate_identity_excess_rows_excluded"] += 1
                continue
            seen.add(identity)
            mesh_text = mesh.replace("|", " ")
            rows.append(
                {
                    "record_identity": identity,
                    "label": 1 if label == "include" else 0,
                    "candidate_text": normalize(f"{title} {abstract} {mesh_text}"),
                    "comparator_title": normalize(title),
                    "comparator_abstract": normalize(f"{abstract} {mesh_text}"),
                }
            )
    receipt.update(
        {
            "excluded_first_raw_line_sha256": excluded_hash,
            "eligible_unique_records": len(rows),
            "duplicate_record_identities_after_repair": len(rows) - len(seen),
        }
    )
    return sorted(rows, key=lambda row: row["record_identity"]), receipt


def text_list_hash(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        body = value.encode("utf-8")
        digest.update(len(body).to_bytes(8, "big"))
        digest.update(body)
    return digest.hexdigest()


def order_hash(order: list[int], identities: list[str]) -> str:
    return hashlib.sha256("\n".join(identities[index] for index in order).encode("ascii")).hexdigest()


def order_metrics(order: list[int], y: np.ndarray) -> dict[str, float]:
    if len(order) != len(y) or len(set(order)) != len(y):
        raise ValueError("arm ordering must contain every record exactly once")
    total_included = int(y.sum())
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


def initial_seed(y: np.ndarray, identities: list[str]) -> list[int]:
    positives = np.flatnonzero(y == 1)
    negatives = np.flatnonzero(y == 0)
    source_id = "10423427"
    included = min(positives, key=lambda index: stable_seed_key(source_id, identities[int(index)]))
    excluded = min(negatives, key=lambda index: stable_seed_key(source_id, identities[int(index)]))
    return [int(included), int(excluded)]


def complete_active_order(
    x: Any,
    y: np.ndarray,
    initial: list[int],
    identities: list[str],
    batch_size: int,
    model_factory: Callable[[], Any],
    score_function: Callable[[Any, Any], np.ndarray],
    weight_ratio: float | None = None,
) -> tuple[list[int], int]:
    selected = list(initial)
    remaining = np.ones(len(y), dtype=bool)
    remaining[selected] = False
    fits = 0
    while remaining.any():
        model = model_factory()
        fit_kwargs: dict[str, Any] = {}
        if weight_ratio is not None:
            selected_y = y[selected]
            positives = int(selected_y.sum())
            negatives = len(selected_y) - positives
            if positives == 0 or negatives == 0:
                raise ValueError("balanced active comparator requires both seed classes")
            weights = np.where(selected_y == 1, 1.0, positives / (weight_ratio * negatives))
            weights = weights * (len(weights) / float(weights.sum()))
            fit_kwargs["sample_weight"] = weights
        model.fit(x[selected], y[selected], **fit_kwargs)
        fits += 1
        pool = np.flatnonzero(remaining)
        scores = np.asarray(score_function(model, x[pool]), dtype=float)
        ranked_pool = pool[np.argsort(-scores, kind="stable")]
        chosen = ranked_pool[:batch_size]
        selected.extend(int(index) for index in chosen)
        remaining[chosen] = False
    return selected, fits


def candidate_order(x: Any, y: np.ndarray, seed: list[int], identities: list[str], batch_size: int) -> tuple[list[int], int]:
    return complete_active_order(
        x=x,
        y=y,
        initial=seed,
        identities=identities,
        batch_size=batch_size,
        model_factory=lambda: SGDClassifier(
            loss="log_loss",
            class_weight="balanced",
            alpha=1e-5,
            max_iter=2000,
            tol=1e-4,
            random_state=20260823,
        ),
        score_function=lambda model, pool: model.predict_proba(pool)[:, 1],
    )


def binding_receipt(
    protocol: dict[str, Any],
    data_path: Path,
    v2_dir: Path,
    archive_path: Path,
    asreview_root: Path,
) -> tuple[dict[str, Any], bool]:
    provenance = protocol["provenance"]
    files = {
        "v1_retained_result": (v2_dir / "RESULT_V1_RETAINED.json", provenance["v1_retained_result_sha256"]),
        "v2_protocol": (v2_dir / "PROTOCOL_FREEZE_V2.json", provenance["v2_protocol_sha256"]),
        "v2_implementation": (v2_dir / "IMPLEMENTATION_FREEZE_V2.json", provenance["v2_implementation_sha256"]),
        "v2_result": (v2_dir / "RESULT_V2.json", provenance["v2_result_sha256"]),
        "asreview_archive": (archive_path, provenance["asreview_archive_sha256"]),
    }
    receipt: dict[str, Any] = {
        "source": {
            "bytes_actual": data_path.stat().st_size if data_path.is_file() else None,
            "bytes_expected": protocol["population"]["source_bytes"],
            "md5_actual": hash_file(data_path, "md5") if data_path.is_file() else None,
            "md5_expected": protocol["population"]["source_md5"],
        },
        "files": {},
        "selected_asreview_source": {},
    }
    receipt["source"]["passed"] = (
        receipt["source"]["bytes_actual"] == receipt["source"]["bytes_expected"]
        and receipt["source"]["md5_actual"] == receipt["source"]["md5_expected"]
    )
    for name, (path, expected) in files.items():
        actual = hash_file(path) if path.is_file() else None
        receipt["files"][name] = {"actual": actual, "expected": expected, "passed": actual == expected}
    for relative, expected in provenance["selected_source_sha256"].items():
        path = asreview_root / relative
        actual = hash_file(path) if path.is_file() else None
        receipt["selected_asreview_source"][relative] = {
            "actual": actual,
            "expected": expected,
            "passed": actual == expected,
        }
    passed = bool(receipt["source"]["passed"]) and all(
        item["passed"] for group in (receipt["files"], receipt["selected_asreview_source"]) for item in group.values()
    )
    receipt["passed"] = passed
    return receipt, passed


def execute(
    protocol_path: Path,
    implementation_path: Path,
    data_path: Path,
    v2_dir: Path,
    archive_path: Path,
    asreview_root: Path,
    out_path: Path,
) -> None:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    implementation = json.loads(implementation_path.read_text(encoding="utf-8"))
    binding, binding_ok = binding_receipt(protocol, data_path, v2_dir, archive_path, asreview_root)
    result: dict[str, Any] = {
        "audit_identity": protocol["audit_identity"],
        "claim_scope": protocol["claim_scope"],
        "protocol_sha256": hash_file(protocol_path),
        "implementation_freeze_sha256": hash_file(implementation_path),
        "binding_receipt": binding,
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
                "gates": {name: False for name in protocol["gates"]},
                "arms": {},
            }
        )
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return

    rows, parse_receipt = parse_source(data_path)
    identities = [row["record_identity"] for row in rows]
    y = np.array([row["label"] for row in rows], dtype=int)
    parse_ok = all(
        (
            parse_receipt["total_raw_lines"] == 25540,
            parse_receipt["excluded_incident_rows"] == 1,
            parse_receipt["five_field_post_incident_rows"] == 25539,
            parse_receipt["malformed_field_rows"] == 0,
            parse_receipt["noncanonical_class_rows_excluded"] == 2,
            parse_receipt["duplicate_identity_excess_rows_excluded"] == 3,
            parse_receipt["eligible_unique_records"] == protocol["population"]["eligible_unique_records"],
            int(y.sum()) == protocol["population"]["included_records"],
            int((1 - y).sum()) == protocol["population"]["excluded_records"],
            parse_receipt["duplicate_record_identities_after_repair"] == 0,
            parse_receipt["excluded_first_raw_line_sha256"]
            == "c619fb151436f2569165e3e7b8e8421310e8685740dd1be19945c449c8b266d5",
        )
    )
    if not parse_ok:
        result.update(
            {
                "terminal": protocol["cannot_check_terminal"],
                "gates": {name: False for name in protocol["gates"]},
                "parse_receipt": parse_receipt,
                "arms": {},
            }
        )
        out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return

    seed = initial_seed(y, identities)
    seed_hash = hashlib.sha256("\n".join(identities[index] for index in seed).encode("ascii")).hexdigest()
    candidate_texts = [row["candidate_text"] for row in rows]
    comparator_texts = [f"{row['comparator_title']} {row['comparator_abstract']}".strip() for row in rows]

    candidate_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True, lowercase=True
    )
    x_candidate = candidate_vectorizer.fit_transform(candidate_texts)
    candidate, candidate_fits = candidate_order(x_candidate, y, seed, identities, batch_size=52)

    u4_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), sublinear_tf=True, min_df=1, max_df=0.95, lowercase=True
    )
    x_u4 = u4_vectorizer.fit_transform(comparator_texts)
    u4, u4_fits = complete_active_order(
        x=x_u4,
        y=y,
        initial=seed,
        identities=identities,
        batch_size=52,
        model_factory=lambda: LinearSVC(loss="squared_hinge", C=0.11, random_state=20260823),
        score_function=lambda model, pool: model.decision_function(pool),
        weight_ratio=9.8,
    )

    u3_vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
    x_u3 = u3_vectorizer.fit_transform(comparator_texts)
    u3, u3_fits = complete_active_order(
        x=x_u3,
        y=y,
        initial=seed,
        identities=identities,
        batch_size=52,
        model_factory=lambda: MultinomialNB(alpha=3.822),
        score_function=lambda model, pool: model.predict_proba(pool)[:, 1],
        weight_ratio=1.2,
    )

    arms = {
        "ACTIVE_LOGREG_V2_CANDIDATE": {
            "metrics": order_metrics(candidate, y),
            "order_sha256": order_hash(candidate, identities),
            "model_fits": candidate_fits,
            "features": int(x_candidate.shape[1]),
        },
        "ASREVIEW_ELAS_U4_CADENCE_MATCHED": {
            "metrics": order_metrics(u4, y),
            "order_sha256": order_hash(u4, identities),
            "model_fits": u4_fits,
            "features": int(x_u4.shape[1]),
        },
        "ASREVIEW_ELAS_U3_CADENCE_MATCHED": {
            "metrics": order_metrics(u3, y),
            "order_sha256": order_hash(u3, identities),
            "model_fits": u3_fits,
            "features": int(x_u3.shape[1]),
        },
    }
    candidate_metrics = arms["ACTIVE_LOGREG_V2_CANDIDATE"]["metrics"]
    active_names = ["ASREVIEW_ELAS_U4_CADENCE_MATCHED", "ASREVIEW_ELAS_U3_CADENCE_MATCHED"]
    strongest_primary = max(active_names, key=lambda name: arms[name]["metrics"]["recall_at_010"])
    strongest_wss = max(active_names, key=lambda name: arms[name]["metrics"]["wss_at_95"])
    primary_delta = candidate_metrics["recall_at_010"] - arms[strongest_primary]["metrics"]["recall_at_010"]
    wss_delta = candidate_metrics["wss_at_95"] - arms[strongest_wss]["metrics"]["wss_at_95"]
    expected = protocol["candidate"]
    candidate_reproduced = all(
        (
            arms["ACTIVE_LOGREG_V2_CANDIDATE"]["order_sha256"] == expected["order_sha256_expected"],
            abs(candidate_metrics["recall_at_010"] - expected["recall_at_010_expected"]) <= 1e-15,
            abs(candidate_metrics["wss_at_95"] - expected["wss_at_95_expected"]) <= 1e-15,
        )
    )
    gates = {
        "G1_BINDING": True,
        "G2_CANDIDATE_REPRODUCTION": candidate_reproduced,
        "G3_PRIMARY_ACTIVE_MARGIN": primary_delta >= 0.05,
        "G4_WORK_SAVING_DOMINANCE": wss_delta >= 0.0,
    }
    terminal = protocol["positive_terminal"] if all(gates.values()) else protocol["negative_terminal"]
    result.update(
        {
            "terminal": terminal,
            "gates": gates,
            "parse_receipt": parse_receipt,
            "eligible_records": len(y),
            "included_records": int(y.sum()),
            "excluded_records": int((1 - y).sum()),
            "initial_seed_record_identities_sha256": seed_hash,
            "adapter_receipt": {
                "candidate_text_sha256": text_list_hash(candidate_texts),
                "comparator_text_sha256": text_list_hash(comparator_texts),
                "record_identity_order_sha256": hashlib.sha256("\n".join(identities).encode("ascii")).hexdigest(),
            },
            "strongest_active_comparator_at_010": strongest_primary,
            "strongest_active_comparator_at_wss95": strongest_wss,
            "candidate_minus_strongest_active_recall_at_010": primary_delta,
            "candidate_minus_best_active_wss_at_95": wss_delta,
            "arms": arms,
        }
    )
    out_path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--implementation", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--v2-dir", type=Path, required=True)
    parser.add_argument("--asreview-archive", type=Path, required=True)
    parser.add_argument("--asreview-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(
        args.protocol,
        args.implementation,
        args.data,
        args.v2_dir,
        args.asreview_archive,
        args.asreview_root,
        args.out,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
