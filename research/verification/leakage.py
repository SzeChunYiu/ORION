"""Leakage and shortcut falsifiers for the #283 verification stack.

Detectors are written from the issue contract, not from paper scorer internals.
A planted case with the gold label inside candidate-visible text must fire.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterable, Sequence

LABEL_TOKEN = re.compile(r"[A-Z][A-Z0-9_]{3,}")


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def exact_label_in_visible_text(visible: str, gold_label: str) -> bool:
    if not gold_label:
        return False
    pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(gold_label) + r"(?![A-Za-z0-9_])")
    return bool(pattern.search(visible))


def planted_label_leakage_hits(cases: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fire when the gold label token appears in candidate-visible text."""
    hits: list[dict[str, Any]] = []
    for case in cases:
        visible = str(case.get("visible") or case.get("visible_symptom") or "")
        gold = str(case.get("gold") or case.get("protected_root_cause") or case.get("gold_label") or "")
        case_id = str(case.get("case_id") or case.get("id") or "")
        if exact_label_in_visible_text(visible, gold):
            hits.append({"case_id": case_id, "gold": gold, "kind": "exact_label_in_visible_text"})
    return hits


def lexical_label_predictor(visible: str, labels: Sequence[str]) -> str | None:
    """Substring/token predictor: pick the label whose distinctive tokens overlap most."""
    text = normalize(visible)
    if not text:
        return None
    best: tuple[int, str] | None = None
    for label in labels:
        tokens = [tok for tok in normalize(label.replace("_", " ")).split() if len(tok) > 3]
        score = sum(1 for tok in tokens if tok in text)
        # also score raw label fragments
        if normalize(label.replace("_", " ")) in text:
            score += 5
        if best is None or score > best[0]:
            best = (score, label)
    if best is None or best[0] <= 0:
        return None
    return best[1]


def family_template_predictor(case_family: str, family_to_label: dict[str, str]) -> str | None:
    return family_to_label.get(case_family)


def label_permutation_accuracy(preds: Sequence[str], gold: Sequence[str], *, shift: int = 1) -> float:
    if len(preds) != len(gold) or not gold:
        raise ValueError("preds and gold must have the same positive length")
    labels = sorted(set(gold))
    remap = {label: labels[(index + shift) % len(labels)] for index, label in enumerate(labels)}
    permuted = [remap[value] for value in gold]
    return sum(pred == perm for pred, perm in zip(preds, permuted, strict=True)) / len(gold)


def duplicate_ids(*groups: Iterable[str]) -> set[str]:
    counts: Counter[str] = Counter()
    for group in groups:
        counts.update(group)
    return {key for key, value in counts.items() if value > 1}


def metadata_only_accuracy(
    rows: Sequence[dict[str, Any]],
    *,
    gold_key: str,
    metadata_keys: Sequence[str],
) -> dict[str, Any]:
    """Majority-label-by-metadata-tuple predictor."""
    buckets: dict[tuple[Any, ...], list[str]] = {}
    for row in rows:
        key = tuple(row.get(name) for name in metadata_keys)
        buckets.setdefault(key, []).append(str(row[gold_key]))
    correct = 0
    for row in rows:
        key = tuple(row.get(name) for name in metadata_keys)
        majority = Counter(buckets[key]).most_common(1)[0][0]
        if str(row[gold_key]) == majority:
            correct += 1
    return {
        "n": len(rows),
        "accuracy": correct / len(rows) if rows else 0.0,
        "unique_metadata_tuples": len(buckets),
    }
