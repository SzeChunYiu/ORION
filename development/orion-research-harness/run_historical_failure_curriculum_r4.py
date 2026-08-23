#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.svm import LinearSVC

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "research" / "negative-recovery" / "HISTORICAL_FAILURE_CURRICULUM_V1.json"
PROTOCOL = REPO / "research" / "negative-recovery" / "R4_HISTORICAL_FAILURE_CURRICULUM_PROTOCOL_V1.md"
OUT = REPO / "artifacts" / "orion-historical-failure-curriculum-r4.json"
PREFIX = "ORION_HISTORICAL_FAILURE_CURRICULUM_R4="

ACTIONS = (
    "RESTORE_AUTHORITY_GOVERNANCE",
    "BIND_IDENTITY_AND_TYPE",
    "REPAIR_INSTRUMENT_IDENTIFIABILITY",
    "WIRE_MECHANISM_INTO_EXECUTION",
    "HARDEN_STATE_CUSTODY_AND_FRESHNESS",
    "REPAIR_IMPLEMENTATION_OR_NUMERIC_SEMANTICS",
)

LEXICONS = {
    "RESTORE_AUTHORITY_GOVERNANCE": (
        "authority", "authorize", "promotion", "self-cert", "waiver", "readiness",
        "provisional", "attestor", "verifier lane", "self-promotion", "closure",
    ),
    "BIND_IDENTITY_AND_TYPE": (
        "identity", "digest", "hash", "ref", "branch", "commit", "tree",
        "representation", "bound", "binding", "subject", "artifact",
    ),
    "REPAIR_INSTRUMENT_IDENTIFIABILITY": (
        "label", "cue", "denominator", "falsifiable", "refutation", "treatment",
        "ablation", "metric", "construction", "guard", "predicate", "null",
    ),
    "WIRE_MECHANISM_INTO_EXECUTION": (
        "unwired", "caller", "production path", "not called", "applied", "unreachable",
        "operator", "gate", "premise", "runtime path", "consumer", "reachable",
    ),
    "HARDEN_STATE_CUSTODY_AND_FRESHNESS": (
        "race", "toctou", "stale", "supersession", "alias", "custody", "concurrent",
        "snapshot", "drift", "occasion", "symlink", "fresh", "atomic",
    ),
    "REPAIR_IMPLEMENTATION_OR_NUMERIC_SEMANTICS": (
        "overflow", "int16", "int32", "dtype", "module", "import", "process",
        "subprocess", "placeholder", "exception", "sentinel", "integer", "pytest",
    ),
}

HEX_RE = re.compile(r"\b[0-9a-fA-F]{7,}\b")
NUM_RE = re.compile(r"\b\d+\b")
FENCE_RE = re.compile(r"^```.*$", re.MULTILINE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_visible(text: str) -> str:
    marker = "## Failure class"
    if text.count(marker) != 1:
        raise ValueError("record must contain exactly one '## Failure class' marker")
    before = text.split(marker, 1)[0]
    lines = before.splitlines()
    # Strip top-level title entirely; evaluator-created titles may name the diagnosis.
    while lines and not lines[0].startswith("# "):
        lines.pop(0)
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    visible = "\n".join(lines).strip()
    visible = FENCE_RE.sub("", visible)
    visible = HEX_RE.sub("<HEX>", visible)
    visible = NUM_RE.sub("<NUM>", visible)
    return re.sub(r"\s+", " ", visible).strip()


def linear_predict(texts: list[str], labels: list[str]) -> list[str]:
    predictions: list[str] = []
    for holdout in range(len(texts)):
        train_texts = [text for i, text in enumerate(texts) if i != holdout]
        train_labels = [label for i, label in enumerate(labels) if i != holdout]
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            sublinear_tf=True,
        )
        matrix = vectorizer.fit_transform(train_texts)
        model = LinearSVC(C=1.0, class_weight="balanced", random_state=0)
        model.fit(matrix, train_labels)
        predictions.append(model.predict(vectorizer.transform([texts[holdout]]))[0])
    return predictions


def native_predict(text: str) -> str:
    lowered = text.lower()
    scores = {}
    for action in ACTIONS:
        scores[action] = sum(1 for term in LEXICONS[action] if term in lowered)
    # Frozen action order breaks ties.
    return max(ACTIONS, key=lambda action: (scores[action], -ACTIONS.index(action)))


def class_recall(labels: list[str], predictions: list[str]) -> dict[str, float]:
    by_action: dict[str, list[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        by_action[label].append(index)
    return {
        action: sum(predictions[i] == action for i in by_action[action]) / len(by_action[action])
        for action in ACTIONS
    }


def shuffled_controls(texts: list[str], labels: list[str]) -> list[float]:
    values = []
    for seed in range(64):
        shuffled = labels.copy()
        random.Random(2026082300 + seed).shuffle(shuffled)
        pred = linear_predict(texts, shuffled)
        values.append(accuracy_score(shuffled, pred))
    return values


def main() -> int:
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if tuple(registry["actions"]) != ACTIONS:
        raise SystemExit("registry action order drift")
    records = registry["records"]
    if len(records) != 30 or Counter(action for _slug, action in records) != Counter({a: 5 for a in ACTIONS}):
        raise SystemExit("registry is not the frozen balanced 30-record panel")

    texts: list[str] = []
    labels: list[str] = []
    record_receipts = []
    leakage_failures = []
    for slug, action in records:
        path = REPO / "research" / "failures" / slug / "README.md"
        raw = path.read_text(encoding="utf-8")
        visible = normalize_visible(raw)
        if slug.lower() in visible.lower():
            leakage_failures.append(f"slug:{slug}")
        if action.lower() in visible.lower():
            leakage_failures.append(f"action:{slug}")
        if "## failure class" in visible.lower():
            leakage_failures.append(f"class-section:{slug}")
        texts.append(visible)
        labels.append(action)
        record_receipts.append({
            "slug_digest": hashlib.sha256(slug.encode()).hexdigest(),
            "source_sha256": sha256_bytes(raw.encode()),
            "visible_sha256": sha256_bytes(visible.encode()),
            "visible_chars": len(visible),
        })

    lane_a = linear_predict(texts, labels)
    lane_b = [native_predict(text) for text in texts]
    lane_a_accuracy = accuracy_score(labels, lane_a)
    lane_a_f1 = f1_score(labels, lane_a, labels=list(ACTIONS), average="macro", zero_division=0)
    lane_b_accuracy = accuracy_score(labels, lane_b)
    dual_agreement = accuracy_score(lane_a, lane_b)
    recalls = class_recall(labels, lane_a)
    shuffled = shuffled_controls(texts, labels)
    majority = 1 / len(ACTIONS)

    metrics = {
        "lane_a_accuracy": lane_a_accuracy,
        "lane_a_macro_f1": lane_a_f1,
        "lane_b_accuracy": lane_b_accuracy,
        "dual_exact_action_agreement": dual_agreement,
        "lane_a_class_recall": recalls,
        "majority_baseline": majority,
        "shuffled_control_max": max(shuffled),
        "shuffled_control_mean": sum(shuffled) / len(shuffled),
        "shuffled_control_accuracies": shuffled,
    }
    gates = {
        "lane_a_accuracy_ge_0_60": lane_a_accuracy >= 0.60,
        "lane_a_macro_f1_ge_0_55": lane_a_f1 >= 0.55,
        "lane_a_majority_delta_ge_0_30": lane_a_accuracy - majority >= 0.30,
        "lane_a_beats_every_shuffle": lane_a_accuracy > max(shuffled),
        "every_lane_a_class_recall_ge_0_40": min(recalls.values()) >= 0.40,
        "lane_b_accuracy_ge_0_55": lane_b_accuracy >= 0.55,
        "dual_agreement_ge_0_45": dual_agreement >= 0.45,
        "leakage_clean": not leakage_failures,
    }
    terminal = (
        "ORION_HISTORICAL_FAILURE_CURRICULUM_REPAIR_RESPONSIBILITY_SUPPORTED"
        if all(gates.values())
        else "ORION_HISTORICAL_FAILURE_CURRICULUM_REPAIR_RESPONSIBILITY_NOT_SUPPORTED"
    )
    payload = {
        "schema": "ORION.HistoricalFailureCurriculumResult.v1",
        "protocol_sha256": sha256_bytes(PROTOCOL.read_bytes()),
        "registry_sha256": sha256_bytes(registry_bytes),
        "record_count": len(records),
        "class_count": len(ACTIONS),
        "records": record_receipts,
        "metrics": metrics,
        "gates": gates,
        "leakage_failures": leakage_failures,
        "predictions": [
            {
                "record_index": i,
                "gold": labels[i],
                "lane_a": lane_a[i],
                "lane_b": lane_b[i],
                "lane_a_correct": lane_a[i] == labels[i],
                "lane_b_correct": lane_b[i] == labels[i],
            }
            for i in range(len(records))
        ],
        "terminal": terminal,
        "claim_boundary": (
            "Repository-native historical failure descriptions only; broad repair-responsibility "
            "classification under leave-one-record-out. No exact repair synthesis or external-science claim."
        ),
    }
    payload["result_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(PREFIX + json.dumps({
        "terminal": terminal,
        "result_digest": payload["result_digest"],
        "metrics": metrics,
        "gates": gates,
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
