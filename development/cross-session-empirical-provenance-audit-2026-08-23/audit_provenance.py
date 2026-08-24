#!/usr/bin/env python3
"""Bounded, read-only provenance audit for cross-session P1/P3 evidence.

The reducer emits only paths, hashes, schemas, counts, provenance tokens, and
aggregate integrity results. It never copies notes, rationales, source text,
model outputs, case payloads, or checkpoint predictions into the audit packet.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/billy/Desktop/projects/ORION-claude")
OUT = ROOT / "development/cross-session-empirical-provenance-audit-2026-08-23"
P1_RAW = ROOT / "papers/paper-01-recursive-epistemic-reconstruction/results/raw"
P3 = ROOT / "papers/paper-03-global-knowledge-portrait"
P3_GOLD = P3 / "gold"
P3_FULL = P3 / "evaluation/run-full"
P3_SMOKE = P3 / "evaluation/run-smoke"
P3_ANALYSIS = P3 / "evaluation/analysis"
PARENT_OBSERVED_HEAD = "b55f553b7b16b488cf4c515ba286578783a5fd83"
OVERALL_TERMINAL = (
    "CROSS_SESSION_EMPIRICAL_PROVENANCE_AUDIT_P1_P3_COMPLETE__"
    "NO_RECORD_PROMOTED__TOP_TIER_EMPIRICAL_CLAIMS_CANNOT_CHECK"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, binary: bool = False) -> str | bytes:
    value = subprocess.check_output(["git", "-C", str(ROOT), *args])
    return value if binary else value.decode().strip()


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def counter(values) -> dict:
    return dict(sorted(Counter(values).items(), key=lambda item: str(item[0])))


def stat_record(path: Path, tracked: set[str]) -> dict:
    st = path.stat()
    rel = str(path.relative_to(ROOT))
    return {
        "path": rel,
        "bytes": st.st_size,
        "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
        "sha256": sha(path),
        "git_tracked": rel in tracked,
    }


def source_status() -> dict:
    raw = git("status", "--porcelain=v1", "-z", binary=True)
    assert isinstance(raw, bytes)
    entries = [item for item in raw.split(b"\0") if item]
    excluded_prefix = b"?? development/cross-session-empirical-provenance-audit-2026-08-23/"
    source_entries = [item for item in entries if not item.startswith(excluded_prefix)]
    canonical = b"\0".join(source_entries) + (b"\0" if source_entries else b"")
    decoded = [
        {"code": item[:2].decode(errors="replace"), "path": item[3:].decode(errors="replace")}
        for item in source_entries
    ]
    return {
        "entry_count": len(decoded),
        "status_code_counts": counter(item["code"] for item in decoded),
        "porcelain_v1_z_sha256": hashlib.sha256(canonical).hexdigest(),
        "entries": decoded,
    }


def p1_file_summary(name: str) -> dict:
    path = P1_RAW / name
    rows = jsonl(path)
    keyset = {(row.get("case_id"), row.get("system_id"), row.get("seed")) for row in rows}
    result = {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
        "rows": len(rows),
        "unique_case_system_seed": len(keyset),
        "unique_cases": len({row.get("case_id") for row in rows}),
        "systems": sorted({row.get("system_id") for row in rows}),
        "seeds": sorted({row.get("seed") for row in rows}),
        "status_counts": counter(row.get("status") for row in rows),
        "suite_fingerprints": sorted({row.get("suite_fingerprint") for row in rows}),
        "subject_revisions": sorted({row.get("subject_revision") for row in rows}),
    }
    if name.endswith("_runs.jsonl"):
        elapsed = [float(row["elapsed_seconds"]) for row in rows]
        token_rows = [
            row for row in rows if float(row["trace"]["resources"].get("model_tokens", 0)) != 0
        ]
        result.update(
            {
                "protocol_ids": sorted({row.get("protocol_id") for row in rows}),
                "excluded_true": sum(bool(row.get("excluded")) for row in rows),
                "error_nonempty": sum(bool(row.get("error")) for row in rows),
                "elapsed_seconds_min": min(elapsed),
                "elapsed_seconds_max": max(elapsed),
                "model_token_nonzero_rows": len(token_rows),
                "model_token_nonzero_system_counts": counter(row["system_id"] for row in token_rows),
                "model_tokens_sum": int(
                    sum(float(row["trace"]["resources"].get("model_tokens", 0)) for row in rows)
                ),
                "raw_trace_wallclock_nonzero_rows": sum(
                    float(row["trace"]["resources"].get("wallclock_seconds", 0)) != 0
                    for row in rows
                ),
            }
        )
    else:
        result.update(
            {
                "hidden_shift_rows": sum(bool(row.get("is_hidden_shift")) for row in rows),
                "control_rows": sum(bool(row.get("is_control")) for row in rows),
                "trace_fidelity_false_rows": sum(not bool(row.get("trace_fidelity")) for row in rows),
                "cannot_check_reason_nonempty_rows": sum(
                    bool(row.get("cannot_check_reason")) for row in rows
                ),
            }
        )
    return result


def checkpoint_summary(path: Path) -> tuple[dict, set[tuple[str, int, int]]]:
    rows = jsonl(path)
    grouped: dict[tuple[str, int, int], list[dict]] = defaultdict(list)
    exact = Counter()
    for row in rows:
        key = (str(row["sid"]), int(row["ci"]), int(row["seed"]))
        grouped[key].append(row)
        canonical = json.dumps(row, sort_keys=True, separators=(",", ":"))
        exact[hashlib.sha256(canonical.encode()).hexdigest()] += 1
    duplicate_groups = {key: values for key, values in grouped.items() if len(values) > 1}
    conflicting = sum(
        len({json.dumps(row, sort_keys=True, separators=(",", ":")) for row in values}) > 1
        for values in duplicate_groups.values()
    )
    multiplicity = counter(len(values) for values in grouped.values())
    by_system: dict[str, Counter] = defaultdict(Counter)
    for key, values in grouped.items():
        sid = key[0]
        by_system[sid]["rows"] += len(values)
        by_system[sid]["unique_keys"] += 1
        by_system[sid]["duplicate_excess"] += len(values) - 1
        by_system[sid]["keys_with_duplicates"] += int(len(values) > 1)
    summary = {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
        "rows": len(rows),
        "systems": len({row["sid"] for row in rows}),
        "case_indices": len({int(row["ci"]) for row in rows}),
        "seeds": len({int(row["seed"]) for row in rows}),
        "unique_sid_case_seed": len(grouped),
        "duplicate_excess": len(rows) - len(grouped),
        "keys_with_duplicates": len(duplicate_groups),
        "duplicate_keys_with_conflicting_payloads": conflicting,
        "exact_duplicate_excess": sum(count - 1 for count in exact.values()),
        "max_key_multiplicity": max(map(len, grouped.values())),
        "key_multiplicity_distribution": multiplicity,
        "per_system": {sid: dict(values) for sid, values in sorted(by_system.items())},
    }
    return summary, set(grouped)


def ast_signature_evidence() -> dict:
    metrics_path = ROOT / "src/orion/study/metrics.py"
    evaluate_path = ROOT / "src/orion/study/evaluate.py"
    analyze_path = P3 / "evaluation/analyze_run.py"
    metrics_tree = ast.parse(metrics_path.read_text())
    cost_args = None
    compute_call_args = []
    current = None
    for node in ast.walk(metrics_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "cost_metrics":
                cost_args = len(node.args.args)
            if node.name == "compute_all_metrics":
                current = node
    if current is not None:
        compute_call_args = [
            len(node.args)
            for node in ast.walk(current)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "fn"
        ]
    analyze_text = analyze_path.read_text()
    evaluate_text = evaluate_path.read_text()
    return {
        "metrics_py_sha256": sha(metrics_path),
        "evaluate_py_sha256": sha(evaluate_path),
        "analyze_run_py_sha256": sha(analyze_path),
        "cost_metrics_declared_positional_parameters": cost_args,
        "metric_dispatch_positional_argument_counts": compute_call_args,
        "cost_metric_signature_mismatch_present": cost_args == 1 and 2 in compute_call_args,
        "checkpoint_analysis_last_write_wins_dict_comprehension_present": (
            'ordered = {c: p for c, p in zip(per_run_cases[(sid, seed)], preds)}'
            in analyze_text
        ),
        "full_orion_stub_marker_present": "ORION_FULL_NOT_YET_BOUND" in evaluate_text,
        "zero_cost_metadata_literal_present": (
            '"wallclock_seconds": 0.0, "model_tokens": 0' in evaluate_text
        ),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    head_start = str(git("rev-parse", "HEAD"))
    branch = str(git("rev-parse", "--abbrev-ref", "HEAD"))
    status_start = source_status()
    tracked = set(str(git("ls-files", "-z")).split("\0"))

    p1_names = ["pilot_runs.jsonl", "pilot_scored.jsonl", "test_runs.jsonl", "test_scored.jsonl"]
    p1_files = {name: p1_file_summary(name) for name in p1_names}
    p1_files["pilot_runs.jsonl"]["git_tracked"] = False
    p1_files["pilot_scored.jsonl"]["git_tracked"] = False
    p1_files["test_runs.jsonl"]["git_tracked"] = True
    p1_files["test_scored.jsonl"]["git_tracked"] = True

    annotations = [json.loads(path.read_text()) for path in sorted((P3_GOLD / "annotations").glob("*.json"))]
    annotation_paths = sorted((P3_GOLD / "annotations").glob("*.json"))
    source_refs = [record[side] for record in annotations for side in ("source_a", "source_b")]
    source_hash_counts = Counter(ref["text_hash"] for ref in source_refs)
    combined_path = P3_GOLD / "combined_gold.json"
    combined = json.loads(combined_path.read_text())["annotations"]
    combined_by_case = {row["case_id"]: row for row in combined}
    coordinate_keys = [
        "referent_relation", "construct_relation", "measurement_relation", "context_relation",
        "polarity_relation", "modality_relation", "attribution_relation", "discourse_relation",
        "mapping_relation", "contradiction_verdict", "integration_verdict",
    ]
    coordinates_matching = 0
    sources_matching = 0
    for record in annotations:
        parent = combined_by_case.get(record["sample_id"])
        if parent and all(record["coordinates"][key] == parent[key] for key in coordinate_keys):
            coordinates_matching += 1
        if parent and all(
            record[side][key] == parent[side][key]
            for side in ("source_a", "source_b")
            for key in ("document_id", "document_version", "discipline", "span_start", "span_end", "text_hash")
        ):
            sources_matching += 1
    combined_refs = [row[side] for row in combined for side in ("source_a", "source_b")]
    freeze = json.loads((P3_GOLD / "GOLD_ATLAS_FREEZE_V1.json").read_text())

    results = jsonl(P3_FULL / "results.jsonl")
    manifest = json.loads((P3_FULL / "MANIFEST.json").read_text())
    raw_hash_key_matches = sum(
        row["raw_artifact_hash"]
        == hashlib.sha256(f'{row["system_id"]}|{row["seed"]}'.encode()).hexdigest()
        for row in results
    )
    checkpoint_final, final_keys = checkpoint_summary(P3_FULL / "checkpoint.jsonl")
    checkpoint_pre, pre_keys = checkpoint_summary(P3_FULL / "checkpoint_pre_retry.jsonl")
    checkpoint_final["keys_not_in_pre_retry"] = len(final_keys - pre_keys)
    checkpoint_final["pre_retry_keys_missing_final"] = len(pre_keys - final_keys)

    analysis_aggregates = json.loads((P3_ANALYSIS / "aggregates.json").read_text())
    analysis_metrics = json.loads((P3_ANALYSIS / "metrics_by_system_seed.json").read_text())
    code_evidence = ast_signature_evidence()

    inventory_paths = [
        P1_RAW / name for name in p1_names
    ] + [
        ROOT / "papers/paper-01-recursive-epistemic-reconstruction/README.md",
        ROOT / "papers/paper-01-recursive-epistemic-reconstruction/protocol/PROTOCOL_V1.json",
        ROOT / "papers/paper-01-recursive-epistemic-reconstruction/protocol/EXECUTION_MANIFEST_V1.md",
        P3_GOLD / "combined_gold.json",
        P3_GOLD / "GOLD_ATLAS_FREEZE_V1.json",
        P3_GOLD / "generate_source_texts.py",
        P3 / "evaluation/analyze_run.py",
        ROOT / "src/orion/study/evaluate.py",
        ROOT / "src/orion/study/metrics.py",
    ] + annotation_paths
    for directory in (P3_FULL, P3_SMOKE, P3_ANALYSIS):
        inventory_paths.extend(sorted(path for path in directory.rglob("*") if path.is_file()))
    inventory_paths = sorted(set(inventory_paths))
    inventory = [stat_record(path, tracked) for path in inventory_paths]

    tracked_parent_matches = 0
    tracked_parent_missing = 0
    tracked_parent_differs = 0
    for item in inventory:
        if not item["git_tracked"]:
            continue
        rel = item["path"]
        parent = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", f"{PARENT_OBSERVED_HEAD}:{rel}"],
            capture_output=True,
            text=True,
        )
        current = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", f"{head_start}:{rel}"],
            capture_output=True,
            text=True,
        )
        if parent.returncode != 0:
            tracked_parent_missing += 1
        elif current.returncode == 0 and parent.stdout.strip() == current.stdout.strip():
            tracked_parent_matches += 1
        else:
            tracked_parent_differs += 1

    head_end = str(git("rev-parse", "HEAD"))
    status_end = source_status()
    receipt = {
        "schema_version": "orion.cross-session-empirical-provenance.source-checkout-receipt.v1",
        "audit_started_at": started_at,
        "audit_completed_at": datetime.now(timezone.utc).isoformat(),
        "repository": str(ROOT),
        "parent_observed_head": PARENT_OBSERVED_HEAD,
        "head_at_audit_start": head_start,
        "head_at_audit_end": head_end,
        "head_stable_during_audit": head_start == head_end,
        "branch": branch,
        "parent_observed_head_is_ancestor": subprocess.call(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", PARENT_OBSERVED_HEAD, head_end]
        ) == 0,
        "commits_after_parent_observed_head": int(
            str(git("rev-list", "--count", f"{PARENT_OBSERVED_HEAD}..{head_end}"))
        ),
        "source_status_at_start_excluding_audit_path": status_start,
        "source_status_at_end_excluding_audit_path": status_end,
        "source_status_stable_during_audit": status_start == status_end,
        "selected_file_count": len(inventory),
        "selected_git_tracked_file_count": sum(item["git_tracked"] for item in inventory),
        "selected_tracked_files_identical_parent_observed_to_audit_head": tracked_parent_matches,
        "selected_tracked_files_missing_at_parent_observed_head": tracked_parent_missing,
        "selected_tracked_files_different_parent_observed_to_audit_head": tracked_parent_differs,
        "selected_files": inventory,
        "selected_inventory_sha256": hashlib.sha256(
            json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "boundary": {
            "source_checkout_edited_outside_owned_audit_directory": False,
            "raw_data_imported": False,
            "record_promoted": False,
            "payload_bodies_emitted": False,
            "pytest_or_repo_ci_run": False,
        },
    }
    (OUT / "SOURCE_CHECKOUT_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )

    evidence = {
        "schema_version": "orion.cross-session-empirical-provenance.audit-evidence.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_checkout_receipt_sha256": sha(OUT / "SOURCE_CHECKOUT_RECEIPT.json"),
        "p1": {
            "files": p1_files,
            "grid_identity": {
                "pilot": "18 cases x 11 systems x 5 seeds = 990 unique rows",
                "test": "48 cases x 12 systems x 5 seeds = 2,880 unique rows",
            },
            "pilot_subject_revision_dirty": all(
                revision.endswith("+dirty")
                for revision in p1_files["pilot_runs.jsonl"]["subject_revisions"]
            ),
            "pilot_model_token_nonzero_rows": p1_files["pilot_runs.jsonl"][
                "model_token_nonzero_rows"
            ],
            "test_live_provider_rows": p1_files["test_runs.jsonl"][
                "model_token_nonzero_system_counts"
            ].get("orion_live_provider", 0),
            "test_live_provider_model_tokens_sum": p1_files["test_runs.jsonl"][
                "model_tokens_sum"
            ],
            "evidence_class": "HIDDEN_FORMULATION_HARNESS",
            "naturalistic_v2_v3_action_evidence_admissible": False,
            "reason": (
                "All four files are explicitly bound to P1.hidden-formulation.v1 and frozen hidden-shift "
                "suite fingerprints. Even the 240 live-provider test rows score hidden-formulation cases "
                "against host-side gold; they are not naturalistic P1 V2/V3 postpublication-action evidence."
            ),
            "terminal": (
                "P1_CROSS_SESSION_RAW_EVIDENCE_IS_HIDDEN_FORMULATION_HARNESS_ONLY__"
                "NATURALISTIC_V2_V3_ACTION_EVIDENCE_CANNOT_CHECK"
            ),
        },
        "p3": {
            "annotations": {
                "files": len(annotations),
                "sample_ids": len({record["sample_id"] for record in annotations}),
                "discipline_counts": counter(record["discipline"] for record in annotations),
                "annotator_counts": counter(record["annotator"] for record in annotations),
                "annotator_a_filename_count": sum(
                    path.name.endswith(".annotator-a.json") for path in annotation_paths
                ),
                "annotator_b_filename_count": sum(
                    ".annotator-b." in path.name for path in annotation_paths
                ),
                "source_references": len(source_refs),
                "unique_document_ids": len({ref["document_id"] for ref in source_refs}),
                "document_ids_with_seed_placeholder": sum(
                    "SEED-" in ref["document_id"] for ref in source_refs
                ),
                "text_hash_seed_prefix": sum(
                    str(ref["text_hash"]).startswith("seed:sha256:") for ref in source_refs
                ),
                "valid_64_hex_text_hashes": sum(
                    bool(re.fullmatch(r"[0-9a-f]{64}", str(ref["text_hash"])))
                    for ref in source_refs
                ),
                "unique_placeholder_text_hashes": len(source_hash_counts),
                "duplicate_placeholder_hash_values": sum(
                    count > 1 for count in source_hash_counts.values()
                ),
                "duplicate_placeholder_hash_excess": sum(
                    count - 1 for count in source_hash_counts.values()
                ),
                "source_text_field_present_in_untracked_annotations": sum(
                    "text" in ref for ref in source_refs
                ),
                "coordinates_matching_tracked_combined_gold": coordinates_matching,
                "source_metadata_matching_tracked_combined_gold": sources_matching,
                "tracked_combined_gold_source_text_nonempty": sum(
                    bool(ref.get("text")) for ref in combined_refs
                ),
                "tracked_combined_gold_text_hash_matches_text_sha256": sum(
                    ref.get("text") is not None
                    and ref["text_hash"] == hashlib.sha256(ref["text"].encode()).hexdigest()
                    for ref in combined_refs
                ),
                "tracked_combined_gold_text_length_min": min(
                    len(ref.get("text", "")) for ref in combined_refs
                ),
                "tracked_combined_gold_text_length_max": max(
                    len(ref.get("text", "")) for ref in combined_refs
                ),
                "freeze_two_annotator_status": freeze["two_annotator_status"],
                "freeze_source_span_status": freeze["source_span_status"],
            },
            "run_full": {
                "manifest": {
                    "path": str((P3_FULL / "MANIFEST.json").relative_to(ROOT)),
                    "sha256": sha(P3_FULL / "MANIFEST.json"),
                    "systems": len(manifest["systems"]),
                    "seeds": manifest["seeds"],
                    "gold_hash": manifest["gold_hash"],
                    "current_combined_gold_byte_sha256": sha(combined_path),
                    "gold_hash_matches_current_combined_gold_bytes": (
                        manifest["gold_hash"] == sha(combined_path)
                    ),
                    "run_manifest_hash": manifest["run_manifest_hash"],
                    "resource_policy": manifest["resource_policy"],
                    "source_revision_bound": False,
                },
                "results": {
                    "path": str((P3_FULL / "results.jsonl").relative_to(ROOT)),
                    "bytes": (P3_FULL / "results.jsonl").stat().st_size,
                    "sha256": sha(P3_FULL / "results.jsonl"),
                    "rows": len(results),
                    "unique_system_seed": len(
                        {(row["system_id"], int(row["seed"])) for row in results}
                    ),
                    "systems": len({row["system_id"] for row in results}),
                    "seeds": sorted({int(row["seed"]) for row in results}),
                    "status_counts": counter(row["status"] for row in results),
                    "failure_class_counts": counter(str(row["failure_class"]) for row in results),
                    "orion_full_pass_rows": sum(
                        row["system_id"] == "ORION_FULL" and row["status"] == "PASS"
                        for row in results
                    ),
                    "zero_cost_field_rows": {
                        key: sum(float(row["cost"].get(key, 0)) == 0 for row in results)
                        for key in (
                            "wallclock_seconds", "model_tokens", "tool_calls", "reported_currency_cost"
                        )
                    },
                    "cost_metrics_error_counts": counter(
                        float(row["metrics"]["cost_metrics_error"]) for row in results
                    ),
                    "raw_artifact_hash_valid_sha256_rows": sum(
                        bool(re.fullmatch(r"[0-9a-f]{64}", row["raw_artifact_hash"]))
                        for row in results
                    ),
                    "raw_artifact_hash_unique": len(
                        {row["raw_artifact_hash"] for row in results}
                    ),
                    "raw_artifact_hash_matches_system_seed_key_rows": raw_hash_key_matches,
                    "run_manifest_hash_values": sorted(
                        {row["run_manifest_hash"] for row in results}
                    ),
                    "source_revision_bound": False,
                },
                "checkpoint_final": checkpoint_final,
                "checkpoint_pre_retry": checkpoint_pre,
                "code_evidence": code_evidence,
            },
            "analysis_directory": {
                "aggregates_sha256": sha(P3_ANALYSIS / "aggregates.json"),
                "aggregates_bytes": (P3_ANALYSIS / "aggregates.json").stat().st_size,
                "aggregate_system_count": len(analysis_aggregates),
                "metrics_by_system_seed_sha256": sha(
                    P3_ANALYSIS / "metrics_by_system_seed.json"
                ),
                "metric_systems": sorted(analysis_metrics),
                "metric_seed_counts": {
                    system: len(values) for system, values in analysis_metrics.items()
                },
            },
            "empirical_promotion_allowed": False,
            "terminal": (
                "P3_CROSS_SESSION_STRUCTURAL_OUTPUTS_PRESENT__REAL_SOURCE_PROVENANCE_"
                "ANNOTATOR_INDEPENDENCE_COST_AND_DEDUPLICATED_EMPIRICAL_BINDING_CANNOT_CHECK"
            ),
        },
        "overall_terminal": OVERALL_TERMINAL,
        "boundary": {
            "raw_data_imported": False,
            "record_promoted": False,
            "model_or_comparator_executed": False,
            "payload_bodies_retained": False,
            "source_checkout_mutated_outside_audit_directory": False,
        },
    }
    (OUT / "PROVENANCE_AUDIT_EVIDENCE.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "status": "AUDIT_COMPLETE",
                "head": head_end,
                "p1_pilot_rows": p1_files["pilot_runs.jsonl"]["rows"],
                "p1_test_rows": p1_files["test_runs.jsonl"]["rows"],
                "p3_results": len(results),
                "p3_checkpoint_rows": checkpoint_final["rows"],
                "p3_checkpoint_duplicate_excess": checkpoint_final["duplicate_excess"],
                "terminal": OVERALL_TERMINAL,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
