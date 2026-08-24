#!/usr/bin/env python3
"""Freeze the outcome-blind BERTMap V7 compatibility/parser audit."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V6 = REPO / "development/p3-comparator-native-preflight-v6-2026-08-23"
DEEPO = ROOT / "_runtime/deeponto"
BERTMAP = ROOT / "_runtime/bertmap"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def dump(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    deeponto_commit = git(DEEPO, "rev-parse", "HEAD")
    deeponto_tree = git(DEEPO, "rev-parse", "HEAD^{tree}")
    bertmap_commit = git(BERTMAP, "rev-parse", "HEAD")
    bertmap_tree = git(BERTMAP, "rev-parse", "HEAD^{tree}")
    assert deeponto_commit == "74ca8d47f01bad0b8739f19ee2c392bdf6d9c090"
    assert deeponto_tree == "b499cb5780bbe749f7db44d0bc872d275a2737ea"
    assert bertmap_commit == "ce848402b40e2f9513bf2d004894d3f82635022c"
    assert bertmap_tree == "6659aca8db43a74921ff5f5176b0dd9a80eb8554"

    requirements = """# Exact V7 constructor-compatibility island only; not a complete DeepOnto runtime lock.\naccelerate==1.0.1\ntokenizers==0.20.3\ntorch==2.5.1\ntransformers==4.46.3\n"""
    (ROOT / "V7_COMPATIBILITY_REQUIREMENTS.in").write_text(requirements)

    protocol = {
        "schema_version": "orion.p3.bertmap-execution-binding.protocol.v7",
        "protocol_id": "P3_V7_BERTMAP_OUTCOME_BLIND_COMPATIBILITY_AND_PARSER_BINDING",
        "frozen_at": now(),
        "authority": "PAPER_SOURCE_IDENTITY__DEPENDENCY_CONSTRUCTOR_COMPATIBILITY__NATIVE_ARTIFACT_INTERFACE_ONLY",
        "predecessor": {
            "v6_result": {"path": str(V6 / "RESULT_V6.json"), "sha256": sha(V6 / "RESULT_V6.json")},
            "v6_k3_result": {"path": str(V6 / "K3_BERTMAP_RESULT_V6.json"), "sha256": sha(V6 / "K3_BERTMAP_RESULT_V6.json")},
            "v7_successor": {"path": str(V6 / "K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json"), "sha256": sha(V6 / "K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json")},
            "terminal": "CANNOT_CHECK_PINNED_DEPENDENCY_API_INCOMPATIBILITY",
            "native_smoke_readiness": "2/3",
            "scientific_comparator_readiness": "0/3",
        },
        "authoritative_source": {
            "paper": {
                "title": "BERTMap: A BERT-Based Ontology Alignment System",
                "doi": "10.1609/aaai.v36i5.20510",
                "arxiv": "2112.02682",
                "paper_outcomes_opened": False,
            },
            "canonical_original": {
                "repository": "https://github.com/KRR-Oxford/BERTMap",
                "commit": bertmap_commit,
                "tree": bertmap_tree,
            },
            "maintained_implementation": {
                "repository": "https://github.com/KRR-Oxford/DeepOnto",
                "commit": deeponto_commit,
                "tree": deeponto_tree,
                "package_version": "0.9.3",
            },
            "bridge_rule": "The original repository says BERTMap is maintained in DeepOnto; the pinned DeepOnto README links the original repository and AAAI paper, and its BERTMap documentation links the same paper.",
        },
        "single_intended_compatibility_change": {
            "python": "3.10.20",
            "platform": "macOS arm64",
            "requirements_input": "V7_COMPATIBILITY_REQUIREMENTS.in",
            "requirements_input_sha256": sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.in"),
            "tuple": {
                "accelerate": "1.0.1",
                "tokenizers": "0.20.3",
                "torch": "2.5.1",
                "transformers": "4.46.3",
            },
            "source_lock_boundary": "These four versions coexist in the DeepOnto uv.lock only under the Python-below-3.9 resolution branch. Using them on Python 3.10 is an explicit separately hashed compatibility island, not the source lock's native Python-3.10 resolution.",
            "expected_primary_wheel_sha256": {
                "accelerate-1.0.1-py3-none-any.whl": "c6aa0c7b8a797cb150471e90e3ca36ac41f5d4b40512cdd6f058b8bf25589467",
                "tokenizers-0.20.3-cp310-cp310-macosx_11_0_arm64.whl": "c6361191f762bda98c773da418cf511cbaa0cb8d0a1196f16f8c0119bde68ff8",
                "torch-2.5.1-cp310-none-macosx_11_0_arm64.whl": "23d062bf70776a3d04dbe74db950db2a5245e1ba4f27208a87f0d743b0d06e86",
                "transformers-4.46.3-py3-none-any.whl": "a12ef6f52841fd190a3e5602145b542d03507222f2c64ebb7ee92e8788093aef",
            },
        },
        "runtime_probe": {
            "allowed": [
                "resolve and install the exact four-package compatibility island and its transitive dependencies into a disposable Python-3.10 environment",
                "import the four exact packages",
                "inspect TrainingArguments signature",
                "construct TrainingArguments with the source-native evaluation_strategy keyword and bounded local output path",
                "run a synthetic language-level reproduction of the source-native table-reader indexing expression",
            ],
            "forbidden": [
                "import DeepOnto or start its JVM",
                "open or run any pretrained model or model payload",
                "open or run any ontology, benchmark, gold/reference alignment, protected outcome, prediction, or paper data.zip payload",
                "train, predict, repair, score, tune, or interpret row absence as obstruction",
            ],
            "api_success_gate": "Exact versions import; TrainingArguments signature contains evaluation_strategy; constructor returns without model/data/network access.",
            "api_failure_gate": "Any resolution, hash, import, signature, or constructor failure is CANNOT_CHECK; no in-run version substitution.",
        },
        "parser_binding": {
            "artifact_directory": "<output_path>/bertmap/match",
            "required_files": [
                "raw_mappings.json",
                "raw_mappings.tsv",
                "extended_mappings.tsv",
                "filtered_mappings.tsv",
                "repaired_mappings.tsv",
            ],
            "parser": "bertmap_native_parser_v7.py",
            "parser_sha256": sha(ROOT / "bertmap_native_parser_v7.py"),
            "authority": "Structural completeness, universe, score, JSON/TSV equivalence, derivation and hash checks only.",
            "absence_rule": "All source keys with zero rows is structurally valid and never obstruction.",
        },
        "preserved_invariants": {
            "inputs_model_thresholds_offline_guards_and_budget": "Referenced from V6 and not opened or executed here.",
            "gold_or_reference_accessed": False,
            "protected_outcomes_accessed": False,
            "model_opened_or_run": False,
            "ontology_or_benchmark_opened_or_run": False,
            "performance_scoring_performed": False,
            "scientific_claims": "performance, harm, coverage, transport and superiority remain CANNOT_CHECK",
        },
    }
    dump("PROTOCOL_V7.json", protocol)
    receipt = {
        "schema_version": "orion.p3.bertmap-execution-binding.protocol-freeze.v7",
        "frozen_at": now(),
        "protocol_sha256": sha(ROOT / "PROTOCOL_V7.json"),
        "runtime_probe_started": False,
        "model_opened_or_run": False,
        "ontology_or_benchmark_opened_or_run": False,
        "gold_or_reference_opened": False,
        "protected_outcomes_opened": False,
        "paper_or_repository_payload_opened": False,
        "status": "FROZEN_BEFORE_COMPATIBILITY_RUNTIME_PROBE",
    }
    dump("PROTOCOL_FREEZE_RECEIPT_V7.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
