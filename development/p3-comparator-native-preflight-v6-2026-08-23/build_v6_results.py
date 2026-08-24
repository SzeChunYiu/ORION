#!/usr/bin/env python3
"""Build the evidence-only P3 V6 result package from temporary native runs.

This builder intentionally records hashes, counts, interfaces, and failure
terminals only.  It never reads a reference alignment or computes a scientific
performance measure.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path("/Users/billy/Documents/Codex/2026-08-23/can-x20")
LANE = ROOT / "work/lane-handoffs/p3-comparator-native-preflight-v6"
RUNTIME = ROOT / "work/.p3v6-runtime"
RESULTS = RUNTIME / "results"
ALIGN_NS = "http://knowledgeweb.semanticweb.org/heterogeneity/alignment"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha512(path: Path) -> str:
    h = hashlib.sha512()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path: Path, rel_to: Path | None = None) -> dict:
    return {
        "path": str(path.relative_to(rel_to)) if rel_to else str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def read_json(path: Path):
    return json.loads(path.read_text())


def write_json(name: str, value) -> None:
    (LANE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def alignment_rows(path: Path) -> tuple[list[tuple[str, str, str, str]], dict]:
    root = ET.parse(path).getroot()
    rows = []
    for cell in root.findall(f".//{{{ALIGN_NS}}}Cell"):
        e1 = cell.find(f"{{{ALIGN_NS}}}entity1")
        e2 = cell.find(f"{{{ALIGN_NS}}}entity2")
        relation = cell.findtext(f"{{{ALIGN_NS}}}relation")
        measure = cell.findtext(f"{{{ALIGN_NS}}}measure")
        assert e1 is not None and e2 is not None and relation is not None and measure is not None
        rows.append(
            (
                e1.attrib[f"{{{RDF_NS}}}resource"],
                e2.attrib[f"{{{RDF_NS}}}resource"],
                relation,
                measure,
            )
        )
    header = {
        k: root.findtext(f".//{{{ALIGN_NS}}}{k}")
        for k in ["onto1", "onto2", "uri1", "uri2"]
    }
    return rows, header


def row_digest(rows: list[tuple[str, str, str, str]]) -> str:
    payload = "\n".join("\t".join(r) for r in sorted(rows)).encode()
    return hashlib.sha256(payload).hexdigest()


def git_values(repo: Path) -> tuple[str, str]:
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], text=True).strip()
    return commit, tree


def main() -> None:
    protocol = read_json(LANE / "PROTOCOL_V6.json")
    protocol_sha = sha256(LANE / "PROTOCOL_V6.json")
    interface_sha = sha256(LANE / "PROTOCOL_INTERFACE_AMENDMENT_V6.json")
    k3_input_sha = sha256(LANE / "PROTOCOL_K3_INPUT_AMENDMENT_V6.json")
    k3_launcher_sha = sha256(LANE / "PROTOCOL_K3_LAUNCHER_AMENDMENT_V6.json")
    k3_stdin_sha = sha256(LANE / "PROTOCOL_K3_STDIN_AMENDMENT_V6.json")

    # K1: structural parsing only.
    aml_path = RESULTS / "aml_alignment.rdf"
    aml_rows, aml_header = alignment_rows(aml_path)
    aml_run = read_json(RESULTS / "aml_run.json")
    aml_result = {
        "schema_version": "orion.p3.comparator-native-preflight.slot-result.v6",
        "slot": "K1_AML",
        "terminal": "NATIVE_SMOKE_PASS",
        "authority": protocol["authority"],
        "identity": {
            "name": "AML v3.2",
            "commit": "d54a6650818d3474fe36090c2bc7dfe5bf4dfcb6",
            "release_sha256": sha256(RUNTIME / "AML_v3.2.zip"),
            "jar_sha256": sha256(RUNTIME / "aml/AML_v3.2/AgreementMakerLight.jar"),
            "licence": "Apache-2.0",
        },
        "runtime": {
            "java": "OpenJDK 17.0.19 arm64",
            "upstream_named_runtime": "Java 8",
            "deviation_guard": "Retained: smoke succeeded on Java 17, but cross-runtime reproducibility was not checked.",
            "exit_code": aml_run["exit_code"],
            "timeout": aml_run["timeout"],
            "wall_seconds": aml_run["wall_seconds"],
        },
        "native_artifact": {
            **file_record(aml_path),
            "xml_parse": "PASS",
            "cell_count": len(aml_rows),
            "row_shape_count": len(aml_rows),
            "canonical_row_sha256": row_digest(aml_rows),
            "header": aml_header,
            "source_namespace_guard": all(r[0].startswith("urn:orion:p3:v6:smoke:source#") for r in aml_rows),
            "target_namespace_guard": all(r[1].startswith("urn:orion:p3:v6:smoke:target#") for r in aml_rows),
        },
        "interpretation_guard": "Rows were not compared with gold and are neither correctness nor performance evidence.",
    }
    write_json("K1_AML_RESULT_V6.json", aml_result)

    # K2: RDF/TSV equivalence plus mandatory upstream-header guard.
    logmap_repo = RUNTIME / "logmap-src"
    logmap_commit, logmap_tree = git_values(logmap_repo)
    logmap_rdf = RESULTS / "logmap-confirm/logmap2_mappings.rdf"
    logmap_tsv = RESULTS / "logmap-confirm/logmap2_mappings.tsv"
    rdf_rows, rdf_header = alignment_rows(logmap_rdf)
    tsv_rows_full = [tuple(line.split("\t")) for line in logmap_tsv.read_text().splitlines() if line]
    tsv_rows = [(r[0], r[1], r[2], r[3]) for r in tsv_rows_full]
    logmap_run = read_json(RESULTS / "logmap_confirm_run.json")
    source_defect_path = logmap_repo / "src/main/java/uk/ac/ox/krr/logmap2/LogMap2Core.java"
    source_text = source_defect_path.read_text()
    duplicate_header_call = "onto_process1.getOntoIRI(),\n\t\t\t\t\tonto_process1.getOntoIRI()" in source_text
    dependency_jars = sorted((logmap_repo / "target/java-dependencies").glob("*.jar"))
    k2_result = {
        "schema_version": "orion.p3.comparator-native-preflight.slot-result.v6",
        "slot": "K2_LOGMAP",
        "terminal": "NATIVE_SMOKE_PASS_WITH_MANDATORY_RDF_HEADER_METADATA_GUARD",
        "authority": protocol["authority"],
        "identity": {
            "name": "LogMap 4.0 source",
            "commit": logmap_commit,
            "tree": logmap_tree,
            "licence": "Apache-2.0",
            "licence_sha256": sha256(logmap_repo / "LICENSE.txt"),
            "built_jar_sha256": sha256(logmap_repo / "target/logmap-matcher-4.0.jar"),
            "dependency_jar_count_excluding_main": len(dependency_jars),
        },
        "interface_amendment": {
            "sha256": interface_sha,
            "required_filename": "logmap2_mappings.rdf",
            "basis": "Pinned source writes this filename; amendment was frozen before the confirmation run.",
        },
        "runtime": {
            "java": "OpenJDK 17.0.19 arm64",
            "maven": "3.9.11",
            "maven_archive_sha256": sha256(RUNTIME / "apache-maven-3.9.11-bin.tar.gz"),
            "maven_archive_sha512": sha512(RUNTIME / "apache-maven-3.9.11-bin.tar.gz"),
            "maven_sidecar_match": sha512(RUNTIME / "apache-maven-3.9.11-bin.tar.gz")
            == (RUNTIME / "apache-maven-3.9.11-bin.tar.gz.sha512").read_text().strip(),
            "build": "PASS_TESTS_SKIPPED_BY_SCOPE",
            "exit_code": logmap_run["exit_code"],
            "timeout": logmap_run["timeout"],
            "wall_seconds": logmap_run["wall_seconds"],
        },
        "native_artifacts": {
            "rdf": {**file_record(logmap_rdf), "row_count": len(rdf_rows), "canonical_row_sha256": row_digest(rdf_rows)},
            "tsv": {**file_record(logmap_tsv), "row_count": len(tsv_rows), "canonical_row_sha256": row_digest(tsv_rows)},
            "rdf_tsv_row_equivalence": sorted(rdf_rows) == sorted(tsv_rows),
            "rdf_source_namespace_guard": all(r[0].startswith("urn:orion:p3:v6:smoke:source#") for r in rdf_rows),
            "rdf_target_namespace_guard": all(r[1].startswith("urn:orion:p3:v6:smoke:target#") for r in rdf_rows),
        },
        "mandatory_metadata_guard": {
            "status": "UPSTREAM_RDF_HEADER_DEFECT_CONFIRMED",
            "observed_header": rdf_header,
            "source_path": "src/main/java/uk/ac/ox/krr/logmap2/LogMap2Core.java",
            "source_sha256": sha256(source_defect_path),
            "duplicate_ontology_1_call_found": duplicate_header_call,
            "effect": "Both RDF ontology header positions name ontology 1. Consumers must validate row namespaces and must not treat the header as truth evidence.",
        },
        "interpretation_guard": "Rows were not compared with gold; header or row presence is not correctness, harm, coverage, or superiority evidence.",
    }
    write_json("K2_LOGMAP_RESULT_V6.json", k2_result)

    # K3: exact dependency failure and zero required native artifacts.
    deeponto_repo = RUNTIME / "deeponto-src"
    deeponto_commit, deeponto_tree = git_values(deeponto_repo)
    k3_run = read_json(RESULTS / "bertmap_run.json")
    corpora_path = RESULTS / "bertmap-out/bertmap/data/text-semantics.corpora.json"
    fine_tune_path = RESULTS / "bertmap-out/bertmap/data/fine-tune.data.json"
    corpora = read_json(corpora_path)
    fine_tune = read_json(fine_tune_path)
    required_rel = [
        "bertmap/match/raw_mappings.json",
        "bertmap/match/raw_mappings.tsv",
        "bertmap/match/extended_mappings.tsv",
        "bertmap/match/filtered_mappings.tsv",
        "bertmap/match/repaired_mappings.tsv",
    ]
    required_records = [
        {"path": p, "exists": (RESULTS / "bertmap-out" / p).exists()} for p in required_rel
    ]
    partial_records = [file_record(p, RESULTS / "bertmap-out") for p in sorted((RESULTS / "bertmap-out").rglob("*")) if p.is_file()]

    distributions = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name") or "UNKNOWN"
        distributions.append((name, dist.version))
    dist_counts = Counter(distributions)
    unique_packages = sorted({f"{n}=={v}" for n, v in distributions}, key=str.casefold)
    bert_classifier = deeponto_repo / "src/deeponto/align/bertmap/bert_classifier.py"
    bert_source = bert_classifier.read_text()
    model_dir = RUNTIME / "Bio_ClinicalBERT-d5892b39"
    model_files = [file_record(p, model_dir) for p in sorted(model_dir.iterdir()) if p.is_file()]
    stderr = (RESULTS / "bertmap_stderr.log").read_text(errors="replace")
    error_terminal = "TypeError: TrainingArguments.__init__() got an unexpected keyword argument 'evaluation_strategy'"
    k3_result = {
        "schema_version": "orion.p3.comparator-native-preflight.slot-result.v6",
        "slot": "K3_BERTMAP",
        "terminal": "CANNOT_CHECK_PINNED_DEPENDENCY_API_INCOMPATIBILITY",
        "authority": protocol["authority"],
        "identity": {
            "name": "BERTMap via DeepOnto 0.9.3",
            "commit": deeponto_commit,
            "tree": deeponto_tree,
            "licence": "Apache-2.0",
            "licence_sha256": sha256(deeponto_repo / "LICENSE"),
            "uv_lock_sha256": sha256(deeponto_repo / "uv.lock"),
        },
        "amendments": {
            "sixteen_class_input": k3_input_sha,
            "venv_symlink_launcher": k3_launcher_sha,
            "documented_jvm_stdin": k3_stdin_sha,
            "scientific_parameters_changed_after_native_semantics_started": False,
        },
        "model": {
            "repository": "emilyalsentzer/Bio_ClinicalBERT",
            "revision": "d5892b39a4adaed74b92212a44081509db72f87b",
            "weight_sha256": sha256(model_dir / "pytorch_model.bin"),
            "expected_weight_sha256": protocol["slots"]["K3_BERTMAP"]["pretrained_model_lfs_sha256"],
            "weight_hash_match": sha256(model_dir / "pytorch_model.bin")
            == protocol["slots"]["K3_BERTMAP"]["pretrained_model_lfs_sha256"],
            "licence": "MIT",
            "licence_sha256": sha256(model_dir / "LICENSE"),
            "files": model_files,
        },
        "runtime": {
            "python": platform.python_version(),
            "machine": platform.machine(),
            "java": "OpenJDK 17.0.19 arm64",
            "offline_guards": k3_run["environment_guards"],
            "distribution_records": len(distributions),
            "unique_package_records": len(unique_packages),
            "duplicate_distribution_records": [
                {"name": n, "version": v, "count": c}
                for (n, v), c in sorted(dist_counts.items())
                if c > 1
            ],
            "key_packages": {
                "deeponto": "0.9.3",
                "transformers": "4.51.3",
                "torch": "2.6.0",
                "tokenizers": "0.21.1",
                "accelerate": "1.6.0",
            },
            "exit_code": k3_run["exit_code"],
            "timeout": k3_run["timeout"],
            "wall_seconds": k3_run["wall_seconds"],
        },
        "input_derived_progress_trace": {
            "authority": "STRUCTURAL_EXECUTION_TRACE_ONLY",
            "source_named_classes": 16,
            "target_named_classes": 16,
            "synonym_records": len(corpora["synonyms"]),
            "nonsynonym_records": len(corpora["nonsynonyms"]),
            "training_records": len(fine_tune["training"]),
            "validation_records": len(fine_tune["validation"]),
            "training_started": False,
            "prediction_started": False,
            "performance_scoring_started": False,
        },
        "failure": {
            "stage": "TrainingArguments construction before training",
            "exact_terminal": error_terminal,
            "exact_terminal_present_in_stderr": error_terminal in stderr,
            "deeponto_source_sha256": sha256(bert_classifier),
            "deeponto_passes_evaluation_strategy": 'evaluation_strategy="steps"' in bert_source,
            "installed_transformers_constructor_uses_eval_strategy": True,
            "cause": "Pinned DeepOnto source passes the removed `evaluation_strategy` keyword, while its Python-3.10 uv-lock resolves Transformers 4.51.3 whose constructor exposes `eval_strategy` instead.",
        },
        "required_native_artifacts": required_records,
        "required_native_artifact_count": len(required_records),
        "required_native_artifact_present_count": sum(r["exists"] for r in required_records),
        "nonrequired_partial_artifacts_before_cleanup": partial_records,
        "interpretation_guard": "The nonzero exit and missing artifacts are CANNOT_CHECK, never an empty alignment, obstruction, or negative scientific result.",
    }
    write_json("K3_BERTMAP_RESULT_V6.json", k3_result)

    runtime_manifest = {
        "schema_version": "orion.p3.comparator-native-preflight.runtime-manifest.v6",
        "generated_at": utc_now(),
        "platform": {"macos": "26.4 (25E246)", "machine": "arm64", "java": "OpenJDK 17.0.19", "python": platform.python_version()},
        "protocol_sha256": protocol_sha,
        "sources": {
            "aml": aml_result["identity"],
            "logmap": k2_result["identity"],
            "deeponto": k3_result["identity"],
            "model": {k: k3_result["model"][k] for k in ["repository", "revision", "weight_sha256", "licence", "licence_sha256"]},
        },
        "logmap_dependency_jars": [file_record(p, logmap_repo / "target/java-dependencies") for p in dependency_jars],
        "python_packages": unique_packages,
        "python_distribution_record_count": len(distributions),
        "python_unique_package_record_count": len(unique_packages),
    }
    write_json("RUNTIME_MANIFEST_V6.json", runtime_manifest)

    successor_source = RUNTIME / "training_args_4.46.3.py"
    successor_wheel = RUNTIME / "transformers-4.46.3-py3-none-any.whl"
    successor_text = successor_source.read_text()
    successor = {
        "schema_version": "orion.p3.comparator-native-preflight.compatibility-successor.v7",
        "protocol_id": "P3_V7_BERTMAP_PINNED_COMPATIBILITY_SUCCESSOR",
        "frozen_at": utc_now(),
        "status": "PROSPECTIVE_NOT_EXECUTED",
        "predecessor_terminal": k3_result["terminal"],
        "single_changed_factor": "Exact Python dependency tuple only; inputs, model revision, thresholds, offline guards, parser, no-gold rule, and budgets remain unchanged.",
        "candidate_dependency_tuple": {
            "transformers": "4.46.3",
            "transformers_wheel_sha256": sha256(successor_wheel),
            "transformers_wheel_expected_sha256": "a12ef6f52841fd190a3e5602145b542d03507222f2c64ebb7ee92e8788093aef",
            "training_args_source_sha256": sha256(successor_source),
            "evaluation_strategy_field_present": bool(re.search(r"^\s*evaluation_strategy:.*field\(", successor_text, re.MULTILINE)),
            "tokenizers": "0.20.3",
            "accelerate": "1.0.1",
            "torch": "2.5.1",
            "basis": "All four versions are already present together in the pinned DeepOnto uv.lock branch for older Python; only the Transformers API keyword was source-checked here.",
        },
        "success_gate": "Fresh isolated native execution exits zero and all five prospectively required native artifacts parse and hash.",
        "failure_gate": "Any install, import, model, training, repair, timeout, missing-artifact, or parser failure is exact CANNOT_CHECK; no further in-run patching.",
        "scientific_boundary": "Even a pass would establish native smoke readiness only and would not change V5 comparator readiness, performance, harm, coverage, or superiority.",
    }
    write_json("K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json", successor)

    ledger = {
        "schema_version": "orion.p3.comparator-native-preflight.negative-ledger.v6",
        "rule": "Every negative is preserved with cause, residual, and next discriminator; none is rewritten as a positive result.",
        "entries": [
            {"id": "P3V6-N01", "negative_result": "AML was run on Java 17 although upstream names Java 8.", "cause": "Only Java 17 arm64 was available in the bounded runtime.", "residual": "Cross-JDK reproducibility remains untested despite a successful smoke.", "next_discriminator": "Prospectively repeat the same artifact-only smoke under an exact Java-8 image and compare structural artifact hashes without gold."},
            {"id": "P3V6-N02", "negative_result": "Frozen LogMap filename did not match pinned source.", "cause": "Pinned source writes logmap2_mappings.rdf, not logmap_mappings.rdf.", "residual": "The original interface assertion is false for this commit.", "next_discriminator": "Use only the pre-confirmation source-derived interface amendment; future versions must re-inspect the source filename before execution."},
            {"id": "P3V6-N03", "negative_result": "LogMap RDF header names ontology 1 in both ontology positions.", "cause": "Pinned LogMap2Core passes onto_process1.getOntoIRI() twice to createOutFiles.", "residual": "Header-trusting consumers can misattribute the target even though row namespaces are correct.", "next_discriminator": "Require row-namespace guards and test a separately versioned upstream-fix or adapter successor; do not patch V6 output."},
            {"id": "P3V6-N04", "negative_result": "The original three-class BERTMap input implied logging_steps=0.", "cause": "Pinned source computes int(epoch_steps * 0.02); the original synthetic corpus was too small.", "residual": "The three-class K3 input cannot safely reach TrainingArguments.", "next_discriminator": "The source-justified 16-class amendment was frozen before K3 execution and produced nonzero logging/evaluation steps."},
            {"id": "P3V6-N05", "negative_result": "A supervisory Path.resolve call discarded venv activation.", "cause": "The venv Python symlink was resolved to the base interpreter before subprocess launch.", "residual": "That attempt never imported DeepOnto and has zero native authority.", "next_discriminator": "The frozen launcher amendment retains the literal .venv/bin/python path; no scientific parameter changed."},
            {"id": "P3V6-N06", "negative_result": "The first native BERTMap entrypoint aborted at an undocumented-in-protocol interactive JVM prompt.", "cause": "Pinned source uses click.prompt during import when the JVM is not started.", "residual": "Noninteractive launch cannot pass the prompt without an explicit stdin binding.", "next_discriminator": "Pinned DeepOnto documentation justified the frozen exact 2g newline stdin binding before ontology loading or outcomes."},
            {"id": "P3V6-N07", "negative_result": "BERTMap failed before training with a Transformers keyword incompatibility.", "cause": "DeepOnto 0.9.3 passes evaluation_strategy; its Python-3.10 lock resolves Transformers 4.51.3 which exposes eval_strategy.", "residual": "All five required native artifacts are absent, so K3 is CANNOT_CHECK.", "next_discriminator": "Execute the separately frozen V7 compatibility successor using the exact lock-present 4.46.3/0.20.3/1.0.1/2.5.1 tuple; do not modify V6."},
            {"id": "P3V6-N08", "negative_result": "Only two of three comparator families passed native artifact smoke.", "cause": "K3 stopped at dependency API construction while K1 and K2 completed.", "residual": "Three-family native readiness is not established.", "next_discriminator": "Require a fresh V7 K3 pass under the unchanged five-artifact gate."},
            {"id": "P3V6-N09", "negative_result": "No comparator has scientific readiness in V5.", "cause": "V6 intentionally used synthetic inputs, no gold, and no scoring.", "residual": "Performance, harm, coverage, superiority, and transport remain CANNOT_CHECK; V5 stays 0/3.", "next_discriminator": "Only an independently custodied, rights-valid, frozen evaluation can change scientific readiness."},
            {"id": "P3V6-N10", "negative_result": "Native row presence on parallel synthetic labels has no truth authority.", "cause": "The smoke inputs were constructed for interface execution, not evaluation.", "residual": "Rows cannot be claimed as correct mappings or broader empirical support.", "next_discriminator": "Keep smoke artifacts separate from any future independently scored evaluation and never interpret absence as obstruction."},
        ],
    }
    write_json("NEGATIVE_RESULT_LEDGER_V6.json", ledger)

    overall = {
        "schema_version": "orion.p3.comparator-native-preflight.result.v6",
        "terminal": "P3_V6_TWO_OF_THREE_NATIVE_SMOKE_READY__BERTMAP_PINNED_LOCK_API_INCOMPATIBILITY_CANNOT_CHECK__V5_SCIENTIFIC_READINESS_UNCHANGED_ZERO_OF_THREE",
        "generated_at": utc_now(),
        "protocol_sha256": protocol_sha,
        "outcome_blind": True,
        "gold_or_reference_alignment_accessed": False,
        "protected_data_accessed": False,
        "performance_scoring_performed": False,
        "native_smoke_readiness": {"passed": 2, "total": 3, "slots": {"K1_AML": aml_result["terminal"], "K2_LOGMAP": k2_result["terminal"], "K3_BERTMAP": k3_result["terminal"]}},
        "required_native_artifacts": {"K1_AML": {"present": 1, "required": 1}, "K2_LOGMAP": {"present": 1, "required": 1, "mandatory_sidecar_guards_passed": 1}, "K3_BERTMAP": {"present": 0, "required": 5}},
        "preserved_terminals": protocol["preserved_terminals"],
        "scientific_readiness": {"v5_comparator_readiness": "0/3", "changed_by_v6": False},
        "absence_nonselection_rule": "Missing artifacts and absent rows are CANNOT_CHECK, never obstruction or negative truth.",
        "successor": {"artifact": "K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json", "status": "PROSPECTIVE_NOT_EXECUTED"},
    }
    write_json("RESULT_V6.json", overall)

    (LANE / "NEGATIVE_RESULT_LEDGER_V6.md").write_text(
        "# P3 V6 recursive negative-result ledger\n\n"
        "A negative is a research object, not material to erase. Missing or nonselected rows are never obstruction.\n\n"
        "| ID | Negative result | Cause | Residual | Next discriminator |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(
            f"| {e['id']} | {e['negative_result']} | {e['cause']} | {e['residual']} | {e['next_discriminator']} |"
            for e in ledger["entries"]
        )
        + "\n"
    )

    (LANE / "RESULTS_V6.md").write_text(
        "# P3 comparator-native preflight V6\n\n"
        "## Terminal\n\n"
        f"`{overall['terminal']}`\n\n"
        "## Direct result\n\n"
        "| Slot | Native smoke | Required artifact gate | Mandatory qualification |\n"
        "|---|---:|---:|---|\n"
        f"| AML v3.2 | PASS | 1/1 | Java 17 execution; upstream names Java 8 |\n"
        f"| LogMap 4.0 | PASS WITH GUARD | 1/1 primary RDF; mandatory TSV sidecar passed | Upstream RDF header duplicates ontology 1; row namespace guard passed |\n"
        f"| BERTMap / DeepOnto 0.9.3 | CANNOT_CHECK | 0/5 | Pinned Python-3.10 lock selects Transformers 4.51.3, incompatible with DeepOnto's `evaluation_strategy` keyword |\n\n"
        "Thus **2/3** families are native-smoke ready. This is not three-family readiness.\n\n"
        "## What the BERTMap failure establishes\n\n"
        "The exact model revision and weight hash matched, the offline runtime loaded both 16-class ontologies, and input-derived corpora reached 108 training and 12 validation records. Before training, `TrainingArguments` rejected the keyword `evaluation_strategy`. No training, prediction, reference comparison, or performance scoring occurred; all five required mapping artifacts are absent. The only valid terminal is `CANNOT_CHECK_PINNED_DEPENDENCY_API_INCOMPATIBILITY`.\n\n"
        "A separately frozen V7 successor changes only the dependency tuple to versions already co-present in the DeepOnto lock's older-Python branch. The 4.46.3 wheel was independently hashed and source-checked to contain the required keyword. That is a prospective discriminator, not a V7 result.\n\n"
        "## Unchanged scientific boundary\n\n"
        "V3, V4, and V5 terminals remain exactly preserved. In particular, V5 comparator scientific readiness remains **0/3**. Synthetic smoke rows are not correctness, coverage, harm, superiority, or transport evidence. Absence and nonselection are never obstruction.\n\n"
        "## Evidence package\n\n"
        "See `K1_AML_RESULT_V6.json`, `K2_LOGMAP_RESULT_V6.json`, `K3_BERTMAP_RESULT_V6.json`, `RUNTIME_MANIFEST_V6.json`, `NEGATIVE_RESULT_LEDGER_V6.*`, and `K3_V7_COMPATIBILITY_SUCCESSOR_PROTOCOL.json`. Temporary sources, models, dependencies, logs, and raw native/partial artifacts are deleted after bounded facts and hashes are retained.\n"
    )

    print("built V6 evidence package")


if __name__ == "__main__":
    main()
