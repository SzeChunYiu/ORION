#!/usr/bin/env python3
"""Execute the frozen final-six adaptive route-portfolio successor."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import random
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
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


def rank_percentiles(values: np.ndarray, pool: list[int]) -> dict[int, float]:
    ranked = sorted(pool, key=lambda index: (-float(values[index]), index))
    denominator = max(1, len(ranked) - 1)
    return {index: 1.0 - rank / denominator for rank, index in enumerate(ranked)}


def safe_fusion_order(
    x: Any,
    y: np.ndarray,
    initial: list[int],
    batch: int,
    seed: int,
    query_scores: np.ndarray,
    seed_scores: np.ndarray,
) -> list[int]:
    """Fuse four frozen ranks while revealing labels only after selection."""
    selected = list(initial)
    remaining = set(range(len(y))) - set(selected)
    random_order = sorted(remaining)
    random.Random(seed).shuffle(random_order)
    random_values = np.zeros(len(y), dtype=float)
    for rank, index in enumerate(random_order):
        random_values[index] = 1.0 - rank / max(1, len(random_order) - 1)
    while remaining:
        model = SGDClassifier(loss="log_loss", class_weight="balanced", alpha=1e-5,
                              max_iter=2000, tol=1e-4, random_state=seed)
        model.fit(x[selected], y[selected])
        pool = sorted(remaining)
        active_values = np.zeros(len(y), dtype=float)
        active_values[pool] = model.predict_proba(x[pool])[:, 1]
        active_rank = rank_percentiles(active_values, pool)
        query_rank = rank_percentiles(query_scores, pool)
        seed_rank = rank_percentiles(seed_scores, pool)
        random_rank = rank_percentiles(random_values, pool)
        fused = {
            index: 0.40 * active_rank[index] + 0.30 * query_rank[index]
            + 0.20 * seed_rank[index] + 0.10 * random_rank[index]
            for index in pool
        }
        chosen = sorted(pool, key=lambda index: (-fused[index], index))[:batch]
        selected.extend(chosen)
        remaining.difference_update(chosen)
    return selected


def adaptive_portfolio_order(
    x: Any,
    y: np.ndarray,
    initial: list[int],
    batch: int,
    seed: int,
    query_scores: np.ndarray,
    seed_scores: np.ndarray,
) -> tuple[list[int], str, dict[str, dict[str, float | int]]]:
    selected = list(initial)
    remaining = set(range(len(y))) - set(selected)
    pilot_target = math.ceil(0.05 * len(y))
    random_order = sorted(remaining)
    random.Random(seed).shuffle(random_order)
    random_values = np.zeros(len(y), dtype=float)
    for rank, index in enumerate(random_order):
        random_values[index] = 1.0 - rank / max(1, len(random_order) - 1)
    stats = {route: {"pulled": 0, "included": 0} for route in ("ACTIVE", "QUERY", "SEED", "RANDOM")}
    chosen_route = ""
    while remaining:
        model = SGDClassifier(loss="log_loss", class_weight="balanced", alpha=1e-5,
                              max_iter=2000, tol=1e-4, random_state=seed)
        model.fit(x[selected], y[selected])
        pool = sorted(remaining)
        active_values = np.zeros(len(y), dtype=float)
        active_values[pool] = model.predict_proba(x[pool])[:, 1]
        rankings = {
            "ACTIVE": sorted(pool, key=lambda i: (-active_values[i], i)),
            "QUERY": sorted(pool, key=lambda i: (-query_scores[i], i)),
            "SEED": sorted(pool, key=lambda i: (-seed_scores[i], i)),
            "RANDOM": sorted(pool, key=lambda i: (-random_values[i], i)),
        }
        take = min(batch, len(pool))
        picked: list[int] = []
        if len(selected) < pilot_target:
            for route, fraction in (("ACTIVE", 0.30), ("QUERY", 0.30), ("SEED", 0.30), ("RANDOM", 1.0)):
                quota = math.ceil(fraction * take)
                route_picks = 0
                for index in rankings[route]:
                    if index not in picked:
                        picked.append(index)
                        stats[route]["pulled"] += 1
                        stats[route]["included"] += int(y[index])
                        route_picks += 1
                    if route_picks >= quota or len(picked) >= take:
                        break
                if len(picked) >= take:
                    break
        else:
            if not chosen_route:
                rates = {
                    route: stats[route]["included"] / max(1, stats[route]["pulled"])
                    for route in stats
                }
                best_nonactive = max(
                    ("QUERY", "SEED", "RANDOM"),
                    key=lambda route: (rates[route], {"QUERY": 2, "SEED": 1, "RANDOM": 0}[route]),
                )
                chosen_route = best_nonactive if rates[best_nonactive] - rates["ACTIVE"] >= 0.075 else "ACTIVE"
            main_quota = math.ceil(0.90 * take)
            for index in rankings[chosen_route]:
                if index not in picked:
                    picked.append(index)
                if len(picked) >= main_quota:
                    break
            for index in rankings["RANDOM"]:
                if index not in picked:
                    picked.append(index)
                if len(picked) >= take:
                    break
        selected.extend(picked)
        remaining.difference_update(picked)
    if not chosen_route:
        chosen_route = "PILOT_CONSUMED_POOL"
    report = {
        route: {
            **values,
            "positive_rate": values["included"] / max(1, values["pulled"]),
        }
        for route, values in stats.items()
    }
    return selected, chosen_route, report


def execute(protocol_path: Path, data_root: Path, out: Path) -> None:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    receipts: list[dict[str, Any]] = []
    worlds: list[dict[str, Any]] = []
    binding_ok = True
    for world in protocol["worlds"]:
        directory = data_root / world["world_id"]
        world_binding = True
        for spec in world["files"]:
            path = directory / spec["name"]
            actual = file_sha1(path) if path.is_file() else "MISSING"
            receipts.append({"world_id": world["world_id"], "file": spec["name"],
                             "expected_sha1": spec["sha1"], "actual_sha1": actual,
                             "passed": actual == spec["sha1"]})
            world_binding &= actual == spec["sha1"]
        binding_ok &= world_binding
        if not world_binding:
            continue
        labels_path = directory / "labels.csv"
        archives = sorted(directory.glob("works_*.zip"))
        id_field, label_field, labels = read_labels(labels_path)
        works = read_work_rows(archives)
        missing = sorted(set(labels) - set(works))
        extra = sorted(set(works) - set(labels))
        world_binding &= not missing
        binding_ok &= world_binding
        if not world_binding:
            continue
        ids = sorted(labels, key=lambda item: stable_key(world["world_id"], item))
        texts = []
        for record_id in ids:
            row = works[record_id]
            abstract = str(row.get("abstract", "") or "").strip()
            if not abstract:
                abstract = reconstruct_abstract(row.get("abstract_inverted_index"))
            texts.append(" ".join((str(row.get("title", "") or "").strip() + " " + abstract).split()))
        review = json.loads((directory / "metadata_publication.json").read_text(encoding="utf-8"))
        review_abstract = str(review.get("abstract", "") or "").strip()
        if not review_abstract:
            review_abstract = reconstruct_abstract(review.get("abstract_inverted_index"))
        review_query = " ".join(
            (str(review.get("title", "") or "").strip() + " " + review_abstract).split()
        )
        y = np.array([labels[item] for item in ids], dtype=int)
        positive = min((i for i, value in enumerate(y) if value == 1), key=lambda i: stable_key(world["world_id"], ids[i]))
        negative = min((i for i, value in enumerate(y) if value == 0), key=lambda i: stable_key(world["world_id"], ids[i]))
        initial = [positive, negative]
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000,
                                     sublinear_tf=True, lowercase=True)
        x_all = vectorizer.fit_transform(texts + [review_query])
        x = x_all[:-1]
        query_scores = (x @ x_all[-1].T).toarray().ravel()
        centroid_scores = (x @ x[positive].T).toarray().ravel()
        static_rest = sorted((i for i in range(len(ids)) if i not in initial),
                             key=lambda i: (-centroid_scores[i], i))
        static_order = initial + static_rest
        query_rest = sorted((i for i in range(len(ids)) if i not in initial),
                            key=lambda i: (-query_scores[i], i))
        query_order = initial + query_rest
        random_metrics = []
        for seed in protocol["random_seeds"]:
            rest = [i for i in range(len(ids)) if i not in initial]
            random.Random(seed).shuffle(rest)
            random_metrics.append(order_metrics(initial + rest, y))
        random_mean = {key: float(np.mean([item[key] for item in random_metrics])) for key in random_metrics[0]}
        batch = max(10, math.ceil(0.002 * len(ids)))
        active = active_order(x, y, initial, batch, int(protocol["active_model"]["random_state"]))
        adaptive, chosen_route, pilot_stats = adaptive_portfolio_order(
            x, y, initial, batch, int(protocol["active_model"]["random_state"]),
            query_scores, centroid_scores,
        )
        worlds.append({
            "world_id": world["world_id"], "eligible_records": len(ids), "included_records": int(y.sum()),
            "label_id_field": id_field, "label_field": label_field, "missing_label_work_joins": len(missing),
            "unlabelled_extra_works": len(extra), "initial_seed_ids_sha256": hashlib.sha256("\n".join(ids[i] for i in initial).encode()).hexdigest(),
            "tfidf_features": int(x.shape[1]), "active_batch_size": batch,
            "review_query_sha256": hashlib.sha256(review_query.encode()).hexdigest(),
            "adaptive_chosen_route": chosen_route, "adaptive_pilot_stats": pilot_stats,
            "arms": {"RANDOM": random_mean, "STATIC_SEED_CENTROID": order_metrics(static_order, y),
                     "STATIC_REVIEW_QUERY": order_metrics(query_order, y),
                     "ACTIVE_LOGREG": order_metrics(active, y),
                     "ADAPTIVE_ROUTE_PORTFOLIO": order_metrics(adaptive, y)},
        })
    paired: list[dict[str, Any]] = []
    if len(worlds) == 6:
        arms = ("RANDOM", "STATIC_SEED_CENTROID", "STATIC_REVIEW_QUERY",
                "ACTIVE_LOGREG", "ADAPTIVE_ROUTE_PORTFOLIO")
        keys = tuple(worlds[0]["arms"]["RANDOM"])
        aggregate = {
            arm: {
                key: float(np.mean([w["arms"][arm][key] for w in worlds]))
                for key in keys
            }
            for arm in arms
        }
        for world in worlds:
            candidate = world["arms"]["ADAPTIVE_ROUTE_PORTFOLIO"]
            comparators = ("RANDOM", "STATIC_SEED_CENTROID", "STATIC_REVIEW_QUERY", "ACTIVE_LOGREG")
            recall_comparator = max(comparators, key=lambda arm: world["arms"][arm]["recall_at_010"])
            paired.append({
                "world_id": world["world_id"],
                "strongest_recall_comparator": recall_comparator,
                "active_recall_at_010_difference": candidate["recall_at_010"] - world["arms"]["ACTIVE_LOGREG"]["recall_at_010"],
                "strongest_comparator_recall_at_010_regret": candidate["recall_at_010"] - world["arms"][recall_comparator]["recall_at_010"],
                "active_wss_at_95_difference": candidate["wss_at_95"] - world["arms"]["ACTIVE_LOGREG"]["wss_at_95"],
                "candidate_minus_random_recall_at_010": candidate["recall_at_010"] - world["arms"]["RANDOM"]["recall_at_010"],
            })
        differences = np.array([item["active_recall_at_010_difference"] for item in paired])
        observed = float(differences.mean())
        sign_flip_values = [
            float(np.mean(differences * np.array(signs)))
            for signs in itertools.product((-1.0, 1.0), repeat=len(differences))
        ]
        sign_flip_p = float(np.mean(np.array(sign_flip_values) >= observed - 1e-15))
        rng = np.random.default_rng(20260823)
        indices = rng.integers(0, len(differences), size=(100000, len(differences)))
        boot = differences[indices].mean(axis=1)
        uncertainty = {
            "paired_recall_gain_macro_mean": observed,
            "exact_one_sided_sign_flip_p": sign_flip_p,
            "bootstrap_replicates": 100000,
            "bootstrap_seed": 20260823,
            "bootstrap_percentile_95_interval": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        }
        wins = sum(item["active_recall_at_010_difference"] > 0 for item in paired)
        strongest_regret = float(np.mean([item["strongest_comparator_recall_at_010_regret"] for item in paired]))
        worst_regret = float(min(item["strongest_comparator_recall_at_010_regret"] for item in paired))
        wss_gain = float(np.mean([item["active_wss_at_95_difference"] for item in paired]))
    else:
        aggregate, uncertainty, wins, strongest_regret, worst_regret, wss_gain = {}, {}, 0, float("nan"), float("nan"), float("nan")
    gates = {
        "G1_BINDING": binding_ok and len(worlds) == 6 and all(w["missing_label_work_joins"] == 0 for w in worlds),
        "G2_ACTIVE_GAIN": len(worlds) == 6 and uncertainty["paired_recall_gain_macro_mean"] >= 0.02 and uncertainty["exact_one_sided_sign_flip_p"] <= 0.10,
        "G3_CONTROLLER_REPLICATION": len(worlds) == 6 and wins >= 4,
        "G4_NEAR_ORACLE": len(worlds) == 6 and strongest_regret >= -0.03 and worst_regret >= -0.10,
        "G5_WORK_SAVING": len(worlds) == 6 and all(w["arms"]["ADAPTIVE_ROUTE_PORTFOLIO"]["wss_at_95"] > 0 for w in worlds) and wss_gain >= -0.05,
        "G6_RANDOM_HARM": len(worlds) == 6 and all(item["candidate_minus_random_recall_at_010"] >= -0.05 for item in paired),
    }
    if not gates["G1_BINDING"]:
        terminal = protocol["cannot_check_terminal"]
    elif all(gates.values()):
        terminal = protocol["positive_terminal"]
    else:
        terminal = protocol["negative_successor_terminal"]
    result = {"schema_version": protocol["schema_version"], "claim_scope": protocol["claim_scope"],
              "terminal": terminal, "gates": gates, "candidate_strict_wins_over_active_worlds": wins,
              "uncertainty": uncertainty, "paired_world_differences": paired,
              "macro_recall_regret_to_strongest_per_world_comparator": strongest_regret,
              "worst_world_recall_regret_to_strongest_comparator": worst_regret,
              "macro_wss_difference_vs_active": wss_gain,
              "aggregate": aggregate, "worlds": worlds,
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
