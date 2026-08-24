#!/usr/bin/env python3
"""Execute the frozen four-world SYNERGY active-screening V2 successor.

V2 changes only sparse-matrix result extraction.  It leaves the frozen data,
seeds, features, arms, budgets, metrics, gates, and claim boundary unchanged.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import vstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier


def file_sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def stable_key(world: str, record_id: str) -> str:
    return hashlib.sha256(f"{world}:{record_id}".encode()).hexdigest()


def reconstruct_abstract(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for token, indices in value.items():
        for index in indices or []:
            positions.append((int(index), str(token)))
    return " ".join(token for _, token in sorted(positions))


def read_work_rows(archives: list[Path]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for archive in archives:
        with zipfile.ZipFile(archive) as zf:
            for name in zf.namelist():
                if name.endswith("/") or not name.lower().endswith((".json", ".jsonl")):
                    continue
                raw = zf.read(name).decode("utf-8")
                try:
                    payload = json.loads(raw)
                    objects = payload if isinstance(payload, list) else [payload]
                except json.JSONDecodeError:
                    objects = [json.loads(line) for line in raw.splitlines() if line.strip()]
                for row in objects:
                    record_id = str(row.get("id", "")).strip()
                    if record_id:
                        rows[record_id] = row
    return rows


def read_labels(path: Path) -> tuple[str, str, dict[str, int]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        id_field = next((x for x in ("id", "openalex_id", "record_id") if x in fields), "")
        label_field = next((x for x in ("label_included", "included", "label") if x in fields), "")
        if not id_field or not label_field:
            raise ValueError(f"unsupported labels schema: {fields}")
        labels = {str(row[id_field]).strip(): int(row[label_field]) for row in reader}
    if any(value not in (0, 1) for value in labels.values()):
        raise ValueError("labels must be binary")
    return id_field, label_field, labels


def order_metrics(order: list[int], y: np.ndarray) -> dict[str, float]:
    total = int(y.sum())
    cumulative = np.cumsum(y[order])
    def recall_at(fraction: float) -> float:
        k = max(1, math.ceil(fraction * len(order)))
        return float(cumulative[k - 1] / total)
    target = math.ceil(0.95 * total)
    effort_index = int(np.searchsorted(cumulative, target, side="left")) + 1
    effort = effort_index / len(order)
    return {
        "recall_at_005": recall_at(0.05),
        "recall_at_010": recall_at(0.10),
        "recall_at_020": recall_at(0.20),
        "fraction_screened_at_95_recall": effort,
        "wss_at_95": 0.95 - effort,
    }


def active_order(x: Any, y: np.ndarray, initial: list[int], batch: int, seed: int) -> list[int]:
    selected = list(initial)
    remaining = set(range(len(y))) - set(selected)
    while remaining:
        model = SGDClassifier(loss="log_loss", class_weight="balanced", alpha=1e-5,
                              max_iter=2000, tol=1e-4, random_state=seed)
        model.fit(x[selected], y[selected])
        pool = sorted(remaining)
        scores = model.predict_proba(x[pool])[:, 1]
        ranked = sorted(zip(pool, scores), key=lambda item: (-item[1], item[0]))
        chosen = [index for index, _ in ranked[:batch]]
        selected.extend(chosen)
        remaining.difference_update(chosen)
    return selected


def execute(protocol_path: Path, data_root: Path, out: Path) -> None:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    receipts: list[dict[str, Any]] = []
    worlds: list[dict[str, Any]] = []
    binding_ok = True
    for world in protocol["worlds"]:
        directory = data_root / world["world_id"]
        for spec in world["files"]:
            path = directory / spec["name"]
            actual = file_sha1(path) if path.is_file() else "MISSING"
            receipts.append({"world_id": world["world_id"], "file": spec["name"],
                             "expected_sha1": spec["sha1"], "actual_sha1": actual,
                             "passed": actual == spec["sha1"]})
            binding_ok &= actual == spec["sha1"]
        if not binding_ok:
            continue
        labels_path = directory / "labels.csv"
        archives = sorted(directory.glob("works_*.zip"))
        id_field, label_field, labels = read_labels(labels_path)
        works = read_work_rows(archives)
        missing = sorted(set(labels) - set(works))
        extra = sorted(set(works) - set(labels))
        binding_ok &= not missing
        ids = sorted(labels, key=lambda item: stable_key(world["world_id"], item))
        texts = []
        for record_id in ids:
            row = works[record_id]
            abstract = str(row.get("abstract", "") or "").strip()
            if not abstract:
                abstract = reconstruct_abstract(row.get("abstract_inverted_index"))
            texts.append(" ".join((str(row.get("title", "") or "").strip() + " " + abstract).split()))
        y = np.array([labels[item] for item in ids], dtype=int)
        positive = min((i for i, value in enumerate(y) if value == 1), key=lambda i: stable_key(world["world_id"], ids[i]))
        negative = min((i for i, value in enumerate(y) if value == 0), key=lambda i: stable_key(world["world_id"], ids[i]))
        initial = [positive, negative]
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000,
                                     sublinear_tf=True, lowercase=True)
        x = vectorizer.fit_transform(texts)
        # SciPy returns an n-by-1 sparse matrix here.  ``np.asarray`` preserves
        # that matrix as one object, so V1 produced a length-one array and
        # failed before writing any scientific result.  Materialise the sparse
        # values without changing the declared cosine-centroid calculation.
        centroid_scores = (x @ x[positive].T).toarray().ravel()
        static_rest = sorted((i for i in range(len(ids)) if i not in initial),
                             key=lambda i: (-centroid_scores[i], i))
        static_order = initial + static_rest
        random_metrics = []
        for seed in protocol["random_seeds"]:
            rest = [i for i in range(len(ids)) if i not in initial]
            random.Random(seed).shuffle(rest)
            random_metrics.append(order_metrics(initial + rest, y))
        random_mean = {key: float(np.mean([item[key] for item in random_metrics])) for key in random_metrics[0]}
        batch = max(10, math.ceil(0.002 * len(ids)))
        active = active_order(x, y, initial, batch, int(protocol["active_model"]["random_state"]))
        worlds.append({
            "world_id": world["world_id"], "eligible_records": len(ids), "included_records": int(y.sum()),
            "label_id_field": id_field, "label_field": label_field, "missing_label_work_joins": len(missing),
            "unlabelled_extra_works": len(extra), "initial_seed_ids_sha256": hashlib.sha256("\n".join(ids[i] for i in initial).encode()).hexdigest(),
            "tfidf_features": int(x.shape[1]), "active_batch_size": batch,
            "arms": {"RANDOM": random_mean, "STATIC_SEED_CENTROID": order_metrics(static_order, y),
                     "ACTIVE_LOGREG": order_metrics(active, y)},
        })
    if worlds:
        arms = ("RANDOM", "STATIC_SEED_CENTROID", "ACTIVE_LOGREG")
        keys = tuple(worlds[0]["arms"]["RANDOM"])
        aggregate = {arm: {key: float(np.mean([w["arms"][arm][key] for w in worlds])) for key in keys} for arm in arms}
        strongest = max(("RANDOM", "STATIC_SEED_CENTROID"), key=lambda arm: aggregate[arm]["recall_at_010"])
        wins = sum(w["arms"]["ACTIVE_LOGREG"]["recall_at_010"] >= w["arms"][strongest]["recall_at_010"] for w in worlds)
    else:
        aggregate, strongest, wins = {}, "", 0
    gates = {
        "G1_BINDING": binding_ok and len(worlds) == 4 and all(w["missing_label_work_joins"] == 0 for w in worlds),
        "G2_ABSOLUTE": bool(worlds) and aggregate["ACTIVE_LOGREG"]["recall_at_010"] >= 0.80,
        "G3_INCREMENTAL": bool(worlds) and aggregate["ACTIVE_LOGREG"]["recall_at_010"] - aggregate[strongest]["recall_at_010"] >= 0.10 and wins >= 3,
        "G4_WORK_SAVING": bool(worlds) and all(w["arms"]["ACTIVE_LOGREG"]["wss_at_95"] > 0 for w in worlds),
    }
    if not gates["G1_BINDING"]:
        terminal = protocol["cannot_check_terminal"]
    elif all(gates.values()):
        terminal = protocol["positive_terminal"]
    else:
        terminal = protocol["negative_successor_terminal"]
    result = {"schema_version": protocol["schema_version"], "claim_scope": protocol["claim_scope"],
              "terminal": terminal, "gates": gates, "strongest_comparator": strongest,
              "active_wins_or_ties_worlds": wins, "aggregate": aggregate, "worlds": worlds,
              "source_receipts": receipts, "forbidden_claims": protocol["forbidden_claims"]}
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(args.protocol, args.data_root, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
