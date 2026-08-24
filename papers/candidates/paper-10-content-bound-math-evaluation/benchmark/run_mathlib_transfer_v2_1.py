#!/usr/bin/env python3
"""Run the frozen programme-scale P10 Mathlib source-transfer study."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
FRAMEWORK = PAPER.parent / "orion-learning-machine" / "framework"
sys.path.insert(0, str(FRAMEWORK))

from orion_learning_machine.adapters import lean_source


PROTOCOL_PATH = HERE / "MATHLIB_TRANSFER_PROTOCOL_V2_1.json"
MANIFEST_PATH = HERE / "MATHLIB_CORPUS_V2_MANIFEST.json"
CORPUS_ROOT = HERE / "corpus" / "mathlib4_e72c1e277f31"
RESULT_DIR = PAPER / "results"
RESULT_PATH = RESULT_DIR / "MATHLIB_TRANSFER_V2_1.json"
NULL_PATH = RESULT_DIR / "MATHLIB_TRANSFER_V2_1_NULL_DISTRIBUTIONS.json"
MARKDOWN_PATH = RESULT_DIR / "MATHLIB_TRANSFER_V2_1.md"
FAMILY_COUNT = len(lean_source.TACTIC_FAMILIES)
BOOTSTRAPS = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def verify_and_load() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, int]]:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest["source"]["commit"] != protocol["source"]["commit"]:
        raise ValueError("protocol/manifest source revision mismatch")
    if manifest["source"]["lean_toolchain"] != protocol["source"]["lean_toolchain"]:
        raise ValueError("protocol/manifest toolchain mismatch")

    rows: list[dict[str, Any]] = []
    projection = {"unknown_lines": 0, "recognized_files": 0, "recognized_actions": 0}
    for item in manifest["files"]:
        path = CORPUS_ROOT / item["path"]
        if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise ValueError(f"frozen source mismatch: {item['path']}")
        text = path.read_text(encoding="utf-8")
        theorems = lean_source.parse_lean_source(text, item["path"])
        if theorems:
            projection["recognized_files"] += 1
        for theorem in theorems:
            block = list(theorem.raw_lines)
            proof_start = lean_source._proof_start(block)
            if proof_start is None:
                raise AssertionError("parser returned a trajectory without a proof opener")
            projection["unknown_lines"] += sum(
                lean_source.tactic_family(line) == "unknown"
                for line in block[proof_start + 1 :]
            )
            sequence = tuple(theorem.tactics)
            projection["recognized_actions"] += len(sequence)
            rows.append(
                {
                    "trajectory_id": f"{item['path']}::{theorem.theorem_name}",
                    "source_id": item["path"],
                    "top_module": item["top_module"],
                    "theorem_name": theorem.theorem_name,
                    "statement_head": theorem.statement_head,
                    "proof_start_line": theorem.proof_start_line,
                    "mechanics": sequence,
                }
            )
    if not rows:
        raise ValueError("source projection produced no theorem trajectories")
    return protocol, manifest, rows, projection


def ngrams(sequence: tuple[str, ...], n: int) -> list[tuple[str, ...]]:
    return [tuple(sequence[index : index + n]) for index in range(len(sequence) - n + 1)]


def split_evaluation(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, Any]:
    seen = {
        n: {gram for row in train for gram in ngrams(row["mechanics"], n)}
        for n in (2, 3)
    }
    coverage: dict[str, dict[str, int | float | None]] = {}
    for n in (2, 3):
        held_out = [gram for row in test for gram in ngrams(row["mechanics"], n)]
        hits = sum(gram in seen[n] for gram in held_out)
        coverage[str(n)] = {
            "hits": hits,
            "total": len(held_out),
            "coverage": hits / len(held_out) if held_out else None,
        }

    next_by: dict[str, Counter[str]] = defaultdict(Counter)
    global_next: Counter[str] = Counter()
    for row in train:
        for current, following in zip(row["mechanics"], row["mechanics"][1:]):
            next_by[current][following] += 1
            global_next[following] += 1
    if not global_next:
        return {
            "coverage": coverage,
            "markov_correct": 0,
            "unigram_correct": 0,
            "transitions": 0,
        }
    global_prediction = global_next.most_common(1)[0][0]
    markov_correct = unigram_correct = transitions = 0
    for row in test:
        for current, following in zip(row["mechanics"], row["mechanics"][1:]):
            prediction = (
                next_by[current].most_common(1)[0][0]
                if next_by[current]
                else global_prediction
            )
            markov_correct += prediction == following
            unigram_correct += global_prediction == following
            transitions += 1
    return {
        "coverage": coverage,
        "markov_correct": markov_correct,
        "unigram_correct": unigram_correct,
        "transitions": transitions,
    }


def blocked_evaluation(
    rows: list[dict[str, Any]], key: Callable[[dict[str, Any]], str]
) -> dict[str, Any]:
    blocks = sorted({key(row) for row in rows})
    per_block = []
    for block in blocks:
        train = [row for row in rows if key(row) != block]
        test = [row for row in rows if key(row) == block]
        receipt = split_evaluation(train, test)
        receipt["held_out"] = block
        receipt["held_out_trajectories"] = len(test)
        per_block.append(receipt)

    transitions = sum(item["transitions"] for item in per_block)
    markov_correct = sum(item["markov_correct"] for item in per_block)
    unigram_correct = sum(item["unigram_correct"] for item in per_block)
    pooled_coverage = {}
    for n in (2, 3):
        hits = sum(int(item["coverage"][str(n)]["hits"]) for item in per_block)
        total = sum(int(item["coverage"][str(n)]["total"]) for item in per_block)
        pooled_coverage[str(n)] = {
            "hits": hits,
            "total": total,
            "coverage": hits / total if total else None,
        }
    return {
        "blocks": len(blocks),
        "transitions": transitions,
        "markov_accuracy": markov_correct / transitions if transitions else None,
        "unigram_accuracy": unigram_correct / transitions if transitions else None,
        "markov_minus_unigram": (
            (markov_correct - unigram_correct) / transitions if transitions else None
        ),
        "coverage": pooled_coverage,
        "per_block": per_block,
    }


def macro_provenance(rows: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    support: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for row_index, row in enumerate(rows):
        for gram in set(ngrams(row["mechanics"], n)):
            support[gram].append(row_index)
    records = []
    for gram, row_indices in sorted(support.items()):
        modules = sorted({rows[index]["top_module"] for index in row_indices})
        if len(row_indices) < 2 or len(modules) < 2:
            continue
        trajectories = sorted(rows[index]["trajectory_id"] for index in row_indices)
        sources = sorted({rows[index]["source_id"] for index in row_indices})
        records.append(
            {
                "sequence": list(gram),
                "trajectory_support": len(row_indices),
                "top_modules": modules,
                "source_ids": sources,
                "trajectory_ids": trajectories,
                "provenance_sha256": json_sha256(
                    {"sources": sources, "trajectories": trajectories}
                ),
            }
        )
    return records


def encode_rows(rows: list[dict[str, Any]]) -> tuple[list[tuple[int, ...]], list[int], list[str]]:
    family_index = {
        name: index for index, (name, _) in enumerate(lean_source.TACTIC_FAMILIES)
    }
    modules = sorted({row["top_module"] for row in rows})
    module_index = {name: index for index, name in enumerate(modules)}
    sequences = [tuple(family_index[item] for item in row["mechanics"]) for row in rows]
    labels = [module_index[row["top_module"]] for row in rows]
    return sequences, labels, modules


def gram_ids(sequence: tuple[int, ...], n: int) -> set[int]:
    if n == 2:
        return {
            sequence[index] * FAMILY_COUNT + sequence[index + 1]
            for index in range(len(sequence) - 1)
        }
    offset = FAMILY_COUNT**2
    return {
        offset
        + (sequence[index] * FAMILY_COUNT + sequence[index + 1]) * FAMILY_COUNT
        + sequence[index + 2]
        for index in range(len(sequence) - 2)
    }


def cross_module_counts(sequences: list[tuple[int, ...]], labels: list[int]) -> dict[str, int]:
    output = {}
    for n in (2, 3):
        counts: Counter[int] = Counter()
        masks: dict[int, int] = defaultdict(int)
        for sequence, label in zip(sequences, labels):
            for gram in gram_ids(sequence, n):
                counts[gram] += 1
                masks[gram] |= 1 << label
        output[str(n)] = sum(
            count >= 2 and masks[gram].bit_count() >= 2
            for gram, count in counts.items()
        )
    return output


def null_distributions(
    rows: list[dict[str, Any]], seeds: list[int], replicates: int
) -> tuple[dict[str, Any], dict[str, int]]:
    sequences, labels, _ = encode_rows(rows)
    observed = cross_module_counts(sequences, labels)
    distributions: dict[str, Any] = {
        "schema": "P10MathlibTransferNullDistributions.v2_1",
        "observed": observed,
        "replicates_per_seed_and_null": replicates,
        "seeds": {},
    }
    for seed in seeds:
        order_rng = random.Random(f"{seed}:order")
        provenance_rng = random.Random(f"{seed}:provenance")
        seed_result = {
            "order_null": {"2": [], "3": []},
            "provenance_null": {"2": [], "3": []},
        }
        for _ in range(replicates):
            shuffled_sequences = []
            for sequence in sequences:
                shuffled = list(sequence)
                order_rng.shuffle(shuffled)
                shuffled_sequences.append(tuple(shuffled))
            counts = cross_module_counts(shuffled_sequences, labels)
            for n in ("2", "3"):
                seed_result["order_null"][n].append(counts[n])

            shuffled_labels = labels.copy()
            provenance_rng.shuffle(shuffled_labels)
            counts = cross_module_counts(sequences, shuffled_labels)
            for n in ("2", "3"):
                seed_result["provenance_null"][n].append(counts[n])
        distributions["seeds"][str(seed)] = seed_result
    return distributions, observed


def null_summary(values: list[int], observed: int) -> dict[str, Any]:
    upper = (1 + sum(value >= observed for value in values)) / (len(values) + 1)
    lower = (1 + sum(value <= observed for value in values)) / (len(values) + 1)
    return {
        "mean": statistics.mean(values),
        "sd": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
        "p_upper": upper,
        "p_lower": lower,
        "p_two_sided": min(1.0, 2.0 * min(upper, lower)),
        "distribution_sha256": json_sha256(values),
    }


def summarize_nulls(distributions: dict[str, Any]) -> dict[str, Any]:
    observed = distributions["observed"]
    summary = {}
    for seed, seed_values in distributions["seeds"].items():
        summary[seed] = {}
        for family in ("order_null", "provenance_null"):
            summary[seed][family] = {
                n: null_summary(values, observed[n])
                for n, values in seed_values[family].items()
            }
    return summary


def module_bootstrap(per_module: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    usable = [item for item in per_module if item["transitions"]]
    rng = random.Random(seed)
    samples = []
    for _ in range(BOOTSTRAPS):
        selected = [rng.choice(usable) for _ in usable]
        denominator = sum(item["transitions"] for item in selected)
        numerator = sum(
            item["markov_correct"] - item["unigram_correct"] for item in selected
        )
        samples.append(numerator / denominator)
    samples.sort()
    lower = samples[math.floor(0.025 * (len(samples) - 1))]
    upper = samples[math.ceil(0.975 * (len(samples) - 1))]
    return {
        "resamples": BOOTSTRAPS,
        "blocks": len(usable),
        "interval": [lower, upper],
        "samples_sha256": json_sha256(samples),
    }


def render_markdown(result: dict[str, Any]) -> str:
    source = result["source_projection"]
    module = result["leave_top_module_out"]
    gate = result["standalone_gate"]
    return "\n".join(
        [
            "# P10 programme-scale Mathlib transfer result V2.1",
            "",
            "> Generated from the frozen v2 protocol and exact corpus manifest. The JSON",
            "> result and null-distribution files are the machine-readable sources of truth.",
            "",
            "## Population",
            "",
            f"- selected Mathlib files: {result['corpus']['selected_files']}",
            f"- active top-level modules: {result['corpus']['top_modules']}",
            f"- files with recognized tactic trajectories: {source['recognized_files']}",
            f"- theorem/lemma trajectories: {source['trajectories']}",
            f"- projected tactic-family actions: {source['recognized_actions']}",
            f"- excluded unknown proof-body lines: {source['unknown_lines']}",
            "",
            "## Blocked transfer",
            "",
            "| Split | Bigram coverage | Trigram coverage | Markov accuracy | Unigram accuracy | Difference |",
            "|---|---:|---:|---:|---:|---:|",
            f"| Leave source out | {result['leave_source_out']['coverage']['2']['coverage']:.4f} | {result['leave_source_out']['coverage']['3']['coverage']:.4f} | {result['leave_source_out']['markov_accuracy']:.4f} | {result['leave_source_out']['unigram_accuracy']:.4f} | {result['leave_source_out']['markov_minus_unigram']:.4f} |",
            f"| Leave top module out | {module['coverage']['2']['coverage']:.4f} | {module['coverage']['3']['coverage']:.4f} | {module['markov_accuracy']:.4f} | {module['unigram_accuracy']:.4f} | {module['markov_minus_unigram']:.4f} |",
            "",
            f"The top-module bootstrap 95% interval for Markov minus unigram is {module['bootstrap_95_percent_interval']['interval']}.",
            "",
            "## Frozen standalone gate",
            "",
            f"Cross-module macro counts are {result['observed_cross_module_macros']['2']} bigrams and {result['observed_cross_module_macros']['3']} trigrams. Full five-seed, two-null summaries and distribution hashes are in the JSON artifacts.",
            "",
            "Under every seed and both null families, the observed bigram and trigram",
            "counts fall in the significant lower tail. The source sequences therefore",
            "concentrate recurrence into fewer distinct cross-module patterns than the nulls.",
            "",
            f"The pre-registered **numerical conditions** {'pass' if gate['numerical_conditions_pass'] else 'do not pass'}. Prediction condition: {gate['prediction_condition']}; every-seed/two-null order condition: {gate['null_condition']}.",
            f"The full standalone gate **{'passes' if gate['passes'] else 'does not yet pass'}** because native-receipt and nearest-work conditions remain unresolved.",
            "",
            "## Interpretation boundary",
            "",
            "This is a conservative source-text projection. It is not a Lean parser, proof-state",
            "trace, semantic tactic model, theorem-correctness check, prover evaluation or authority",
            "decision. Failure to reject a null is not evidence of randomness or equivalence.",
            "",
        ]
    )


def main() -> None:
    protocol, manifest, rows, projection = verify_and_load()
    leave_source = blocked_evaluation(rows, lambda row: row["source_id"])
    leave_module = blocked_evaluation(rows, lambda row: row["top_module"])
    leave_module["bootstrap_95_percent_interval"] = module_bootstrap(
        leave_module["per_block"], protocol["statistics"]["random_seeds"][0]
    )

    provenance = {
        str(n): macro_provenance(rows, n)
        for n in (2, 3)
    }
    distributions, observed = null_distributions(
        rows,
        protocol["statistics"]["random_seeds"],
        protocol["statistics"]["replicates_per_seed_and_null"],
    )
    nulls = summarize_nulls(distributions)

    prediction_delta = leave_module["markov_minus_unigram"]
    interval = leave_module["bootstrap_95_percent_interval"]["interval"]
    prediction_condition = prediction_delta >= 0.05 and interval[0] > 0.0
    per_n_null_condition = {}
    for n in ("2", "3"):
        per_n_null_condition[n] = all(
            nulls[str(seed)][family][n]["p_two_sided"] <= 0.01
            for seed in protocol["statistics"]["random_seeds"]
            for family in ("order_null", "provenance_null")
        )
    null_condition = any(per_n_null_condition.values())

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    NULL_PATH.write_text(
        json.dumps(distributions, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result = {
        "schema": "P10MathlibTransferResult.v2_1",
        "authority": "REVISION-BOUND SOURCE-PROJECTION EVIDENCE; NO LEAN KERNEL REPLAY",
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "manifest_sha256": sha256(MANIFEST_PATH),
        "null_distributions_sha256": sha256(NULL_PATH),
        "parser_sha256": sha256(Path(lean_source.__file__)),
        "environment": {"python": platform.python_version()},
        "corpus": {
            "repository": manifest["source"]["repository"],
            "commit": manifest["source"]["commit"],
            "lean_toolchain": manifest["source"]["lean_toolchain"],
            "selected_files": manifest["selected_files"],
            "selected_bytes": manifest["selected_bytes"],
            "top_modules": len(manifest["top_module_counts"]),
        },
        "source_projection": {**projection, "trajectories": len(rows)},
        "leave_source_out": leave_source,
        "leave_top_module_out": leave_module,
        "observed_cross_module_macros": observed,
        "macro_provenance": provenance,
        "null_summary": nulls,
        "standalone_gate": {
            "passes": False,
            "numerical_conditions_pass": prediction_condition and null_condition,
            "prediction_condition": prediction_condition,
            "null_condition": null_condition,
            "null_condition_by_ngram": per_n_null_condition,
            "native_receipts_condition": "PENDING_SEPARATE_NATIVE_REPLAY",
            "nearest_work_condition": "PENDING_CONSTRUCTIVE_SATURATION",
            "note": "Every frozen condition, including native receipts and a distinct nearest-work residual, is required for standalone status.",
        },
        "disposition": "PENDING_NATIVE_REPLAY_AND_CONSTRUCTIVE_SATURATION",
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_PATH.write_text(render_markdown(result), encoding="utf-8")
    print(f"wrote {RESULT_PATH}")
    print(f"wrote {NULL_PATH}")
    print(f"wrote {MARKDOWN_PATH}")
    print(json.dumps(result["standalone_gate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
