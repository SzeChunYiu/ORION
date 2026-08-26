#!/usr/bin/env python3
"""Emit issue #279 revival receipts from committed artifacts.

This command never mutates P2 V1. It hashes the frozen 390-task summary, binds
the matched Wide runner without executing arXiv, and projects the one-stage
failure ledger from the Deep 0.000 archive plus the archived Wide probe.

Examples::

    python3 papers/paper-02-open-world-scientific-discovery/scripts/emit_issue279_revival_receipts.py --check
    python3 papers/paper-02-open-world-scientific-discovery/scripts/emit_issue279_revival_receipts.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orion.study.p2.arb_systems import SYSTEM_IDS
from orion.study.p2.arb_wide import BUNDLE_SHA256
from orion.study.p2.corpus import sha256_digest
from orion.study.p2.one_stage_attribution import ledger_from_artifacts

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
# The 2026-08-17 receipt is historical verification evidence.  Rebuild it
# against the exact summary bytes that were verified then, not against the
# later canonical-vocabulary projection now living at RESULTS_SUMMARY_V1.json.
SUMMARY = (
    PAPER
    / "evidence"
    / "offline_results"
    / "RESULTS_SUMMARY_PRE_CANONICAL_VOCABULARY_2026-08-25.json"
)
DEEP_ATTR = PAPER / "evidence" / "external_results" / "DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json"
DEEP_ARCHIVE = PAPER / "evidence" / "external_results" / "DEEP_OFFICIAL_ARCHIVE_V1.json"
WIDE_PROBE = PAPER / "evidence" / "external_results" / "AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json"
SUBSAMPLE = PAPER / "protocol" / "ARB_WIDE_SUBSAMPLE_V1.json"
PROTOCOL_V1 = PAPER / "protocol" / "PROTOCOL_V1.json"
PROTOCOL_V2 = PAPER / "protocol" / "P2_V2_CANDIDATE_GENERATION_DISCRIMINATOR_V1.json"
RECEIPT = PAPER / "evidence" / "external_results" / "OFFLINE_390_REPRODUCTION_RECEIPT_V1.json"
WIDE_FREEZE = PAPER / "evidence" / "external_results" / "WIDE_MATCHED_CAMPAIGN_FREEZE_V1.json"
LEDGER = PAPER / "evidence" / "external_results" / "ONE_STAGE_FAILURE_ATTRIBUTION_LEDGER_V1.json"

PINNED_ARB = "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d"
EXPECTED_N_TASKS = 390
EXPECTED_N_SYSTEMS = 14
EXPECTED_N_REPEATS = 3
EXPECTED_N_RECORDS = 16380
EXPECTED_ORION_RECALL = 0.979487
EXPECTED_BASELINE = "protocol_driven_systematic_review"
EXPECTED_BASELINE_RECALL = 0.666667
EXPECTED_PAIRED = 0.312821
EXPECTED_PREMATURE = 0.0
EXPECTED_TIER = "TIER_B_committed"

WIDE_RUN_COMMAND = """# Outputs only under /tmp. Do not call arXiv.
# 1. Decrypt the pinned AutoResearchBench bundle (credential-free; not an arXiv call).
git clone --filter=blob:none https://github.com/CherYou/AutoResearchBench.git /tmp/arb-upstream
git -C /tmp/arb-upstream checkout a46c9bfb8968786f73f0a6a5b365b5384cd0f96d
mkdir -p /tmp/arb-run
curl --fail --location --retry 4 --retry-delay 3 \\
  --output /tmp/arb-run/AutoResearchBench.jsonl.obf.json \\
  https://huggingface.co/datasets/Lk123/AutoResearchBench/resolve/main/AutoResearchBench.jsonl.obf.json
python /tmp/arb-upstream/decrypt_benchmark.py \\
  --input-file /tmp/arb-run/AutoResearchBench.jsonl.obf.json \\
  --output-file /tmp/arb-run/AutoResearchBench.jsonl
# expected sha256(AutoResearchBench.jsonl) == db1839438033a32dd7d76913575d4b76f144d5e442aaac29be4eda32326392c6
python papers/paper-02-open-world-scientific-discovery/scripts/run_autoresearchbench_wide_compat.py prepare \\
  --full /tmp/arb-run/AutoResearchBench.jsonl \\
  --public /tmp/arb-run/wide_public.jsonl \\
  --gt /tmp/arb-run/wide_gt.jsonl \\
  --manifest /tmp/arb-run/split_manifest.json
# 2. Frozen matched two-system runner (BLOCKED on this lane: arXiv API).
python papers/paper-02-open-world-scientific-discovery/scripts/run_autoresearchbench_wide_comparison.py \\
  --public /tmp/arb-run/wide_public.jsonl \\
  --out-dir /tmp/p2-wide-matched
# Expected N = 399 distinct Wide tasks (400 released rows, 1 duplicate collapsed).
# Library matched systems: orion.study.p2.arb_systems.SYSTEM_IDS (also requires arXiv/OpenAlex).
"""


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_blob(path: Path) -> str:
    result = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def build_reproduction_receipt(
    *,
    regeneration: dict[str, Any] | None = None,
    subject_commit: str | None = None,
) -> dict[str, Any]:
    summary = _load(SUMMARY)
    frozen = summary["frozen_run"]
    orion = summary["systems"]["orion_full"]
    baseline = summary["systems"][EXPECTED_BASELINE]
    checks = {
        "n_tasks": frozen["n_tasks"] == EXPECTED_N_TASKS,
        "n_systems": frozen["n_systems"] == EXPECTED_N_SYSTEMS,
        "n_repeats": frozen["n_repeats"] == EXPECTED_N_REPEATS,
        "n_result_records": frozen["n_result_records"] == EXPECTED_N_RECORDS,
        "orion_complete_gold_recall": orion["mean_complete_gold_recall"] == EXPECTED_ORION_RECALL,
        "strongest_confirmatory_baseline": summary["headline"]["strongest_confirmatory_baseline"]
        == EXPECTED_BASELINE,
        "baseline_complete_gold_recall": baseline["mean_complete_gold_recall"]
        == EXPECTED_BASELINE_RECALL,
        "paired_recall_difference": abs(
            summary["headline"]["orion_minus_strongest_baseline_recall"] - 0.31282
        )
        < 1e-5
        and abs(
            summary["achieved_precision"]["paired_orion_minus_strongest_baseline_recall"]["mean"]
            - EXPECTED_PAIRED
        )
        < 1e-9,
        "orion_premature_task_closure": orion["premature_task_closure_rate"] == EXPECTED_PREMATURE,
        "achieved_precision_tier": summary["analysis_authority"] == EXPECTED_TIER,
        "primary_promoted": summary["achieved_precision"]["primary_promoted"] is False,
    }
    if not all(checks.values()):
        failed = [name for name, ok in checks.items() if not ok]
        raise ValueError("historical results summary failed issue #279 bindings: " + ", ".join(failed))
    receipt = {
        "schema_version": "orion.p2.offline-390-reproduction-receipt.v1",
        "issue": 279,
        "subject_commit": subject_commit or _git_head(),
        # Preserve the receipt exactly as issued: this was the artifact path at
        # verification time.  SUMMARY above is its byte-identical dated copy.
        "artifact": "evidence/offline_results/RESULTS_SUMMARY_V1.json",
        "content_hashes": {
            "results_summary_file_sha256": _file_sha256(SUMMARY),
            "results_summary_canonical_sha256": sha256_digest(summary),
            "record_digest_sha256": frozen["record_digest_sha256"],
            "raw_artifact_hash_list_digest_sha256": frozen[
                "raw_artifact_hash_list_digest_sha256"
            ],
            "results_summary_git_blob": _git_blob(SUMMARY),
        },
        "bindings": {
            "n_tasks": frozen["n_tasks"],
            "n_systems": frozen["n_systems"],
            "n_repeats": frozen["n_repeats"],
            "n_result_records": frozen["n_result_records"],
            "orion_complete_gold_recall": orion["mean_complete_gold_recall"],
            "strongest_confirmatory_baseline": EXPECTED_BASELINE,
            "baseline_complete_gold_recall": baseline["mean_complete_gold_recall"],
            "paired_recall_difference": summary["achieved_precision"][
                "paired_orion_minus_strongest_baseline_recall"
            ]["mean"],
            "orion_premature_task_closure_rate": orion["premature_task_closure_rate"],
            "achieved_precision_tier": summary["analysis_authority"],
            "primary_promoted": False,
            "external_primary_promoted_by_offline_module": False,
        },
        "mechanism_checks": summary["mechanism_checks"],
        "issue279_numeric_bindings_match": True,
        "regeneration": regeneration
        or {
            "command": (
                "python papers/paper-02-open-world-scientific-discovery/scripts/"
                "run_offline_companion.py --check"
            ),
            "verified": False,
            "match": None,
            "note": "Stamp with --stamp-regeneration after a successful --check run.",
        },
        "close_issue": False,
        "close_reason": "Offline 390-task positivity cannot close #279.",
    }
    return receipt


def build_wide_freeze(*, subject_commit: str | None = None) -> dict[str, Any]:
    subsample = _load(SUBSAMPLE)
    protocol_v1 = _load(PROTOCOL_V1)
    if protocol_v1.get("protocol_id") != "P2.open-world-discovery.v1":
        raise ValueError("PROTOCOL_V1.json identity drifted; refusing to freeze a Wide run against it")
    code_revision = str(subsample["benchmark"]["code_revision"])
    if not code_revision.endswith(PINNED_ARB):
        raise ValueError("ARB subsample code revision drifted from the freeze binding")
    if subsample["benchmark"]["bundle_sha256"] != BUNDLE_SHA256:
        raise ValueError("ARB subsample bundle hash drifted from arb_wide.BUNDLE_SHA256")
    return {
        "schema_version": "orion.p2.wide-matched-campaign-freeze.v1",
        "issue": 279,
        "status": "BLOCKED_NOT_EXECUTED",
        "p2_v1_mutation": "forbidden",
        "subject_commit": subject_commit or _git_head(),
        "freeze_bindings": {
            "orion_subject_commit": subject_commit or _git_head(),
            "autoresearchbench_revision": f"CherYou/AutoResearchBench@{PINNED_ARB}",
            "autoresearchbench_bundle_sha256": BUNDLE_SHA256,
            "official_wide_scorer": "evaluate/evaluate_wide_search.py --no-jina",
            "official_wide_scorer_upstream": PINNED_ARB,
            "subsample_manifest": "protocol/ARB_WIDE_SUBSAMPLE_V1.json",
            "subsample_content_hash": subsample["content_hash"],
            "expected_n_distinct_tasks": subsample["selection"]["n"],
            "released_wide_rows": subsample["population"]["wide_rows_in_bundle"],
            "candidate_generation_index_sources_frozen_runner": [
                "arxiv (BLOCKED on this lane)",
                "openalex (not in the keyless OpenAIRE/DBLP/Crossref set)",
            ],
            "keyless_backends_permitted_this_lane": ["openaire", "dblp", "crossref"],
            "semantic_scholar_429": "open_obligation_never_silent_drop",
            "matched_library_systems": list(SYSTEM_IDS),
            "matched_script_systems": [
                "wide_lexical_arxiv",
                "wide_governed_multiroute",
            ],
            "provider_requests_per_task": 3,
            "max_candidates_returned": 20,
            "repeat_policy": "single pass; official Wide scorer is deterministic",
            "contamination_policy": protocol_v1["access_policy"]["search_contamination_policy"],
            "primary_metric": "wide_official_iou",
            "decision_rule": (
                "Do not promote a Wide result from this freeze. Archive official "
                "scorer output first. Offline 390-task positivity is not a substitute."
            ),
            "failure_taxonomy": "orion.p2.one-stage-failure-attribution.v1",
        },
        "expected_n": subsample["selection"]["n"],
        "run_command": WIDE_RUN_COMMAND.strip(),
        "outputs_dir": "/tmp/p2-wide-matched",
        "blockers": [
            {
                "id": "ARXIV_API_FORBIDDEN",
                "detail": (
                    "The frozen matched runners on main "
                    "(run_autoresearchbench_wide_comparison.py::wide_lexical_arxiv and "
                    "orion.study.p2.arb_systems arXiv route) call export.arxiv.org. "
                    "This lane forbids arXiv API calls."
                ),
            },
            {
                "id": "KEYLESS_BACKEND_SET",
                "detail": (
                    "Admissible keyless backends for this lane are OpenAIRE, DBLP and "
                    "Crossref. The frozen matched library also requires OpenAlex for "
                    "dense_like_single_route. Semantic Scholar 429 is an open obligation, "
                    "never a silent drop."
                ),
            },
            {
                "id": "BUNDLE_NOT_IN_REPO",
                "detail": (
                    "Decrypted AutoResearchBench.jsonl is not committed. Regeneration "
                    "recipe is in orion.study.p2.arb_wide.REGENERATION_RECIPE. Preparing "
                    "the bundle does not execute the matched campaign."
                ),
            },
            {
                "id": "SAGE_OFFICIAL_CANNOT_CHECK",
                "detail": (
                    "SAGE retrieval corpus and official evaluator are unpublished. "
                    "Official SAGE cannot run; marked CANNOT_CHECK. Do not weaken."
                ),
            },
            {
                "id": "AGENTSLR_OFFICIAL_CANNOT_CHECK",
                "detail": (
                    "AgentSLR official pipeline is credential/PDF-bound and the pinned "
                    "harness tree has no licence grant. Official AgentSLR cannot run; "
                    "marked CANNOT_CHECK. Do not weaken a baseline to fit the ORION interface."
                ),
            },
        ],
        "already_archived_not_matched": {
            "artifact": "evidence/external_results/AUTORESEARCHBENCH_WIDE_KEYLESS_PROBE_V1.json",
            "n_tasks_attempted": 400,
            "avg_iou": 0.005226,
            "avg_recall": 0.020012,
            "scope": "external_probe_not_full_multi_provider_orion",
            "not_claimed": [
                "full multi-provider ORION execution",
                "matched ORION-vs-baseline superiority",
            ],
        },
    }


def build_protocol_v2() -> dict[str, Any]:
    return {
        "schema_version": "orion.p2.v2-candidate-generation-discriminator.v1",
        "protocol_id": "P2.open-world-discovery.v2-candidate-generation-discriminator",
        "parent_protocol_id": "P2.open-world-discovery.v1",
        "rewrites_parent": False,
        "issue": 279,
        "status": "FROZEN_DISCRIMINATOR_NOT_IMPLEMENTED",
        "allocator_architecture": "not_implemented",
        "why_now": (
            "Deep official scoring (PR #266) has hit rate 0.000 with a passing judge "
            "control and exact/substring title recovery 0/564 from frozen candidates. "
            "The earliest failing stage is candidate generation. A novel adaptive "
            "allocator is not licensed until a matched Wide run, or this discriminator, "
            "says what is broken in query/candidate generation."
        ),
        "dominant_earliest_stage": "CANDIDATE_GENERATION_MISS",
        "components_tested_separately": [
            {
                "id": "sage_style_metadata_keyword_augmentation",
                "disposition_seed": "ADAPT",
                "note": "SAGE-style corpus metadata/keyword augmentation. Not novel by itself.",
            },
            {
                "id": "concept_entity_constraint_query_decomposition",
                "disposition_seed": "ADAPT",
                "note": "Explicit scientific concept/entity/constraint query decomposition.",
            },
            {
                "id": "title_author_citation_field_aware_retrieval",
                "disposition_seed": "ADAPT",
                "note": "Title/author/citation-field aware retrieval when the task permits it.",
            },
            {
                "id": "query_diversification_with_content_identity_dedup",
                "disposition_seed": "COMPOSE",
                "note": "Query diversification with existing content-identity dedup. Not novel by itself.",
            },
            {
                "id": "route_selection_by_marginal_unique_relevant_gain",
                "disposition_seed": "DEFER",
                "note": (
                    "Retrieval-route selection based on observed marginal unique-relevant "
                    "gain. Deferred until the discriminator isolates whether route "
                    "allocation, rather than query generation, is the loss."
                ),
            },
        ],
        "baselines_and_ablations_if_allocator_later": [
            "fixed_v1_allocation",
            "no_safety_floor",
            "treat_censoring_as_zero_reward",
            "no_earned_route_identity",
            "optimistic_unknown_routes",
            "duplicate_route_identity_attack",
            "rejected_action_incorrectly_mutates_learning_state_attack",
        ],
        "primary_criterion": [
            "improve_external_wide_iou_or_recall_at_matched_budget",
            "or_preserve_external_recall_within_frozen_non_inferiority_margin_while_reducing_queries",
        ],
        "safety_floor": "no increase in premature closure beyond a frozen safety margin",
        "official_implementations": {
            "SAGE": "CANNOT_CHECK",
            "AgentSLR": "CANNOT_CHECK",
            "rule": "If an official implementation cannot run, mark CANNOT_CHECK. Do not weaken the baseline.",
        },
        "backends": {
            "permitted_keyless": ["openaire", "dblp", "crossref"],
            "arxiv": "forbidden_on_this_lane",
            "semantic_scholar_429": "open_obligation_never_silent_drop",
        },
        "not_in_scope": [
            "adaptive_allocation_architecture",
            "rewrite_of_PROTOCOL_V1",
            "closing_issue_279_on_offline_390_task_positivity",
        ],
    }


def build_all(
    *,
    regeneration: dict[str, Any] | None = None,
    subject_commit: str | None = None,
) -> dict[str, dict[str, Any]]:
    subject = subject_commit or _git_head()
    return {
        str(RECEIPT.relative_to(PAPER)): build_reproduction_receipt(
            regeneration=regeneration, subject_commit=subject
        ),
        str(WIDE_FREEZE.relative_to(PAPER)): build_wide_freeze(subject_commit=subject),
        str(LEDGER.relative_to(PAPER)): ledger_from_artifacts(
            deep_attribution=_load(DEEP_ATTR),
            deep_archive=_load(DEEP_ARCHIVE),
            wide_probe=_load(WIDE_PROBE),
        ),
        str(PROTOCOL_V2.relative_to(PAPER)): build_protocol_v2(),
    }


def _dump(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_all(payloads: dict[str, dict[str, Any]]) -> None:
    mapping = {
        str(RECEIPT.relative_to(PAPER)): RECEIPT,
        str(WIDE_FREEZE.relative_to(PAPER)): WIDE_FREEZE,
        str(LEDGER.relative_to(PAPER)): LEDGER,
        str(PROTOCOL_V2.relative_to(PAPER)): PROTOCOL_V2,
    }
    for relative, payload in payloads.items():
        path = mapping[relative]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_dump(payload), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


def check_all(payloads: dict[str, dict[str, Any]]) -> int:
    mapping = {
        str(RECEIPT.relative_to(PAPER)): RECEIPT,
        str(WIDE_FREEZE.relative_to(PAPER)): WIDE_FREEZE,
        str(LEDGER.relative_to(PAPER)): LEDGER,
        str(PROTOCOL_V2.relative_to(PAPER)): PROTOCOL_V2,
    }
    problems: list[str] = []
    for relative, payload in payloads.items():
        path = mapping[relative]
        if not path.is_file():
            problems.append(f"missing {relative}")
            continue
        committed = json.loads(path.read_text(encoding="utf-8"))
        expected = json.loads(_dump(payload))
        if committed != expected:
            problems.append(f"drift {relative}")
    v1 = _load(PROTOCOL_V1)
    if v1.get("protocol_id") != "P2.open-world-discovery.v1":
        problems.append("PROTOCOL_V1.json identity is not P2.open-world-discovery.v1")
    if json.loads(PROTOCOL_V2.read_text(encoding="utf-8")).get("rewrites_parent") is not False:
        problems.append("V2 discriminator must not rewrite V1")
    if problems:
        print("issue #279 revival receipts drifted:", file=sys.stderr)
        for item in problems:
            print("  " + item, file=sys.stderr)
        return 1
    print("issue #279 revival receipts match committed artifacts")
    return 0


def stamp_regeneration(match: bool, note: str) -> dict[str, Any]:
    return {
        "command": (
            "python papers/paper-02-open-world-scientific-discovery/scripts/"
            "run_offline_companion.py --check"
        ),
        "verified": True,
        "match": match,
        "verified_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": note,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--stamp-regeneration", action="store_true")
    parser.add_argument("--regeneration-match", action="store_true")
    parser.add_argument("--regeneration-note", default="")
    args = parser.parse_args(argv)

    regeneration = None
    subject_commit = None
    if RECEIPT.is_file():
        existing = json.loads(RECEIPT.read_text(encoding="utf-8"))
        subject_commit = existing.get("subject_commit")
        if not args.stamp_regeneration:
            regeneration = existing.get("regeneration")
    if args.stamp_regeneration:
        regeneration = stamp_regeneration(args.regeneration_match, args.regeneration_note)
    payloads = build_all(regeneration=regeneration, subject_commit=subject_commit)
    if args.write or args.stamp_regeneration:
        write_all(payloads)
    if args.check or not (args.write or args.stamp_regeneration):
        return check_all(payloads)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
