#!/usr/bin/env python3
"""Finalize the self-contained P3 BERTMap V7 evidence packet."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V6 = REPO / "development/p3-comparator-native-preflight-v6-2026-08-23"
DEEPO = ROOT / "_runtime/deeponto"
BERTMAP = ROOT / "_runtime/bertmap"
TERMINAL = (
    "P3_V7_BERTMAP_PAPER_SOURCE_AND_DEPENDENCY_CONSTRUCTOR_COMPATIBILITY_BOUND__"
    "CLOSED_FIVE_ARTIFACT_PARSER_BOUND__NONEMPTY_SOURCE_TABLE_READER_DEFECT_AND_"
    "FULL_NATIVE_SMOKE_CANNOT_CHECK__NATIVE_READINESS_TWO_OF_THREE__SCIENTIFIC_READINESS_ZERO_OF_THREE"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def dump(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def file_record(repo: Path, relpath: str) -> dict:
    path = repo / relpath
    return {"path": relpath, "bytes": path.stat().st_size, "sha256": sha(path)}


def tree_census(repo: Path) -> dict:
    lines = git(repo, "ls-tree", "-r", "-l", "HEAD").splitlines()
    top = defaultdict(lambda: {"blob_files": 0, "blob_bytes": 0})
    blobs = []
    nonblobs = []
    for line in lines:
        meta, relpath = line.split("\t", 1)
        mode, obj_type, object_id, size_text = meta.split()
        if obj_type != "blob" or size_text == "-":
            nonblobs.append({"path": relpath, "mode": mode, "object_type": obj_type, "object_id": object_id})
            continue
        size = int(size_text)
        blobs.append({"path": relpath, "git_blob": object_id, "bytes": size})
        item = top[relpath.split("/", 1)[0]]
        item["blob_files"] += 1
        item["blob_bytes"] += size
    jars = [item for item in blobs if item["path"].endswith(".jar")]
    return {
        "method": "git ls-tree -r -l HEAD metadata only",
        "blob_files": len(blobs),
        "blob_bytes": sum(x["bytes"] for x in blobs),
        "top_level": [{"path": key, **top[key]} for key in sorted(top)],
        "jar_files": len(jars),
        "jar_bytes": sum(x["bytes"] for x in jars),
        "nonblob_entries": nonblobs,
        "_blobs": blobs,
    }


def main() -> None:
    protocol = json.loads((ROOT / "PROTOCOL_V7.json").read_text())
    freeze = json.loads((ROOT / "PROTOCOL_FREEZE_RECEIPT_V7.json").read_text())
    runtime = json.loads((ROOT / "RUNTIME_COMPATIBILITY_RECEIPT_V7.json").read_text())
    parser_receipt = json.loads((ROOT / "PARSER_SELF_TEST_RECEIPT_V7.json").read_text())
    crossref = json.loads((ROOT / "_runtime/crossref.json").read_text())["message"]

    deep_census = tree_census(DEEPO)
    bert_census = tree_census(BERTMAP)
    bert_data = next(item for item in bert_census["_blobs"] if item["path"] == "data.zip")
    deep_census.pop("_blobs")
    bert_census.pop("_blobs")

    deep_allowlist = [
        "LICENSE",
        "README.md",
        "pyproject.toml",
        "uv.lock",
        "scripts/bertmap.py",
        "docs/deeponto/align/bertmap/index.md",
        "docs/ontology.md",
        "src/deeponto/align/bertmap/default_config.yaml",
        "src/deeponto/align/bertmap/bert_classifier.py",
        "src/deeponto/align/bertmap/mapping_prediction.py",
        "src/deeponto/align/bertmap/mapping_refinement.py",
        "src/deeponto/align/bertmap/pipeline.py",
        "src/deeponto/align/bertmap/text_semantics.py",
        "src/deeponto/align/mapping.py",
        "src/deeponto/align/logmap/__init__.py",
        "src/deeponto/onto/ontology.py",
        "src/deeponto/utils/file_utils.py",
    ]
    bert_allowlist = ["LICENSE", "README.md"]
    paper = {
        "doi": crossref["DOI"],
        "title": crossref["title"][0],
        "authors": [f"{x['given']} {x['family']}" for x in crossref["author"]],
        "container_title": crossref["container-title"][0],
        "published_date_parts": crossref["published"]["date-parts"],
        "url": crossref["URL"],
        "crossref_response_sha256": sha(ROOT / "_runtime/crossref.json"),
        "crossref_license_metadata": crossref.get("license"),
        "article_contents_opened": False,
    }
    distributions = runtime["distributions"]
    rights = {
        "schema_version": "orion.p3.bertmap-execution-binding.source-rights-manifest.v7",
        "generated_at": now(),
        "authority": "PUBLIC_SOURCE_IDENTITY_RIGHTS_METADATA_AND_OUTCOME_BLIND_SOURCE_AUDIT__NOT_LEGAL_ADVICE",
        "paper": paper,
        "canonical_original": {
            "repository": "https://github.com/KRR-Oxford/BERTMap",
            "commit": git(BERTMAP, "rev-parse", "HEAD"),
            "tree": git(BERTMAP, "rev-parse", "HEAD^{tree}"),
            "commit_time": git(BERTMAP, "show", "-s", "--format=%cI", "HEAD"),
            "root_license": {"spdx": "Apache-2.0", "sha256": sha(BERTMAP / "LICENSE")},
            "source_files_hashed": [file_record(BERTMAP, p) for p in bert_allowlist],
            "metadata_census": bert_census,
            "paper_data_payload": {
                **bert_data,
                "content_opened": False,
                "readme_description": "preprocessed paper ontologies together with reference mappings",
                "disposition": "EXCLUDED_FROM_V7",
            },
        },
        "maintained_implementation": {
            "repository": "https://github.com/KRR-Oxford/DeepOnto",
            "commit": git(DEEPO, "rev-parse", "HEAD"),
            "tree": git(DEEPO, "rev-parse", "HEAD^{tree}"),
            "commit_time": git(DEEPO, "show", "-s", "--format=%cI", "HEAD"),
            "package_version": "0.9.3",
            "root_license": {"spdx": "Apache-2.0", "sha256": sha(DEEPO / "LICENSE")},
            "source_files_hashed": [file_record(DEEPO, p) for p in deep_allowlist],
            "metadata_census": deep_census,
            "unopened_submodule": {
                "path": "OAEI-Bio-ML",
                "commit": "916350ca97a2ad546f6c9b283a94974c90939841",
                "content_opened": False,
                "disposition": "EXCLUDED_FROM_V7",
            },
        },
        "paper_source_bridge": {
            "original_readme_states_maintained_in_deeponto": True,
            "deeponto_readme_links_original_repository": True,
            "deeponto_readme_and_docs_link_aaai_paper": True,
            "adjudication": "PAPER_LINKED_MAINTAINED_IMPLEMENTATION_IDENTITY_BOUND",
        },
        "compatibility_island": {
            "requirements_input_sha256": sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.in"),
            "requirements_lock_sha256": sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.txt"),
            "installed_distribution_count": len(distributions),
            "all_installed_distributions_expose_license_metadata": all(
                bool(x["license"] or x["license_expression"] or x["license_classifiers"]) for x in distributions
            ),
            "distribution_license_metadata": distributions,
            "boundary": "This 26-distribution compatibility island is not a complete DeepOnto runtime or Java SBOM.",
        },
        "rights_closed": [
            "public inspection of exact BERTMap and DeepOnto source identities",
            "Apache-2.0 root source layers for the two pinned repositories",
            "license-metadata inventory for the installed 26-distribution constructor-only compatibility island",
        ],
        "rights_not_closed": [
            "208 bundled DeepOnto JAR entries and 106 bundled original-BERTMap JAR entries require component-level provenance/licence/SBOM adjudication",
            "the unopened BERTMap data.zip paper ontologies and reference mappings",
            "the unopened OAEI-Bio-ML submodule and any ontology, benchmark, reference or protected outcome bytes",
            "the complete DeepOnto Python/JVM runtime beyond the 26-distribution constructor-only island",
            "pretrained-model bytes and generated checkpoints, mappings, logs and derived artifacts",
            "independent protected evaluation custody and article redistribution rights",
        ],
        "temporary_source_clones_retained_in_final_packet": False,
    }
    dump("SOURCE_RIGHTS_MANIFEST_V7.json", rights)

    lock_text = (ROOT / "V7_COMPATIBILITY_REQUIREMENTS.txt").read_text()
    installed_versions = {x["name"]: x["version"] for x in distributions}
    compatibility_island = {
        "schema_version": "orion.p3.bertmap-execution-binding.compatibility-island.v7",
        "authority": "CONSTRUCTOR_ONLY_DEPENDENCY_COMPATIBILITY__NOT_COMPLETE_DEEPONTO_RUNTIME",
        "platform": "aarch64-apple-darwin",
        "python": runtime["environment"]["python"],
        "uv": "0.11.1",
        "compile_command": "uv pip compile V7_COMPATIBILITY_REQUIREMENTS.in --python-version 3.10 --python-platform aarch64-apple-darwin --generate-hashes --no-emit-index-url --output-file V7_COMPATIBILITY_REQUIREMENTS.txt",
        "install_command": "uv pip install --python _runtime/compat-venv/bin/python --require-hashes -r V7_COMPATIBILITY_REQUIREMENTS.txt",
        "requirements_input_sha256": sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.in"),
        "requirements_lock_sha256": sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.txt"),
        "hashes_required_at_install": True,
        "resolved_distribution_count": len(distributions),
        "installed_versions": installed_versions,
        "primary_expected_wheel_hashes_present_in_lock": {
            filename: expected in lock_text
            for filename, expected in protocol["single_intended_compatibility_change"]["expected_primary_wheel_sha256"].items()
        },
        "exact_primary_versions_match": runtime["compatibility"]["exact_versions_match"],
        "constructor_terminal": runtime["terminal"],
        "boundary": "DeepOnto itself, pandas, JPype, JVM/JARs, ontologies, model and artifacts are intentionally absent; this cannot be called a complete BERTMap lock or execution.",
    }
    dump("COMPATIBILITY_ISLAND_MANIFEST_V7.json", compatibility_island)

    contract = {
        "schema_version": "orion.p3.bertmap-execution-binding.native-artifact-contract.v7",
        "authority": "SOURCE_NATIVE_ARTIFACT_STRUCTURE_AND_FAIL_CLOSED_COMPLETENESS_ONLY",
        "source_identity": rights["maintained_implementation"],
        "required_artifacts": [
            {"path": "bertmap/match/raw_mappings.json", "format": "JSON object: exact eligible source IRI keys; values are lists of [source IRI, target IRI, score]"},
            {"path": "bertmap/match/raw_mappings.tsv", "format": "exact tab header SrcEntity,TgtEntity,Score; row multiset equals raw JSON"},
            {"path": "bertmap/match/extended_mappings.tsv", "format": "same exact tab schema; retains all raw rows"},
            {"path": "bertmap/match/filtered_mappings.tsv", "format": "same exact tab schema; exact thresholded extended set"},
            {"path": "bertmap/match/repaired_mappings.tsv", "format": "same exact tab schema; repaired pairs remain within filtered pairs"},
        ],
        "source_anchors": {
            "checkpointed_raw_outputs": {"path": "src/deeponto/align/bertmap/mapping_prediction.py", "lines": "295-330", "sha256": sha(DEEPO / "src/deeponto/align/bertmap/mapping_prediction.py")},
            "extension_filter_and_existing_file_trust": {"path": "src/deeponto/align/bertmap/mapping_refinement.py", "lines": "93-198", "sha256": sha(DEEPO / "src/deeponto/align/bertmap/mapping_refinement.py")},
            "repair_and_existing_file_trust": {"path": "src/deeponto/align/bertmap/mapping_refinement.py", "lines": "270-319", "sha256": sha(DEEPO / "src/deeponto/align/bertmap/mapping_refinement.py")},
            "nonempty_table_reader_defect": runtime["source_native_reader_audit"],
        },
        "parser": {
            "path": "bertmap_native_parser_v7.py",
            "sha256": sha(ROOT / "bertmap_native_parser_v7.py"),
            "self_test_receipt": {"path": "PARSER_SELF_TEST_RECEIPT_V7.json", "sha256": sha(ROOT / "PARSER_SELF_TEST_RECEIPT_V7.json"), "passed": parser_receipt["passed"], "failed": parser_receipt["failed"]},
            "does_not_open_ontologies_models_gold_or_protected_outcomes": True,
        },
        "completion_rules": [
            "All five required regular non-symlink artifacts must exist and hash.",
            "The raw JSON key set must equal the prospectively frozen eligible source universe, including keys with empty mapping lists.",
            "Raw JSON and TSV row multisets must agree; every row must stay in the frozen source/target universes with a finite score in [0,1].",
            "Extended mappings retain raw rows; filtered mappings equal the frozen-threshold subset; repaired pairs stay within filtered pairs.",
            "Any missing, partial, stale, invalid or out-of-universe artifact is CANNOT_CHECK, never an empty alignment or obstruction.",
        ],
        "scientific_boundary": "Parser pass is interface conformance only and cannot establish mapping correctness, coverage, harm, transport, superiority or absence-as-obstruction.",
    }
    # Do not duplicate the very large nested source manifest inside this contract.
    contract["source_identity"] = {
        "repository": rights["maintained_implementation"]["repository"],
        "commit": rights["maintained_implementation"]["commit"],
        "tree": rights["maintained_implementation"]["tree"],
        "package_version": "0.9.3",
    }
    dump("NATIVE_ARTIFACT_CONTRACT_V7.json", contract)

    negatives = [
        {"id": "P3V7-N01", "negative_result": "V6 stopped before training because Transformers 4.51.3 rejected DeepOnto's evaluation_strategy keyword.", "cause": "The source lock's Python-3.10 branch selects an API-incompatible Transformers version.", "positive_progress": "The exact V7 four-package tuple imports on Python 3.10.20 and TrainingArguments accepts the source-native keyword in a constructor-only probe.", "residual": "DeepOnto, JVM, model, ontologies and BERTMap were not executed; native K3 smoke is still CANNOT_CHECK.", "next_discriminator": "Freeze a full repaired runtime only after the nonempty table-reader defect and rights/SBOM layers are closed, then run the unchanged no-gold five-artifact smoke."},
        {"id": "P3V7-N02", "negative_result": "The V7 four-package tuple is not the source lock's Python-3.10 resolution.", "cause": "Those versions coexist in uv.lock only under Python below 3.9, although matching cp310/macOS-arm64 wheels exist.", "positive_progress": "A separately hashed 26-distribution Python-3.10 compatibility island was resolved and installed with hashes.", "residual": "It excludes DeepOnto's full Python/JVM dependency closure and cannot be called a complete native lock.", "next_discriminator": "Build a complete content-addressed Python-3.10 and Java runtime for a separately named repaired successor."},
        {"id": "P3V7-N03", "negative_result": "Transformers 4.46.3 already deprecates evaluation_strategy.", "cause": "The compatible constructor retains the old keyword only through a deprecation bridge to eval_strategy.", "positive_progress": "The exact source hash and successful constructor are retained.", "residual": "The repair is version-fragile and cannot justify floating upgrades.", "next_discriminator": "Keep 4.46.3 exact or source-version a DeepOnto keyword repair; never float Transformers."},
        {"id": "P3V7-N04", "negative_result": "Pinned DeepOnto's non-reference table reader uses dp['Score'] on rows returned by pandas.DataFrame.itertuples().", "cause": "itertuples returns namedtuples, which support positional/attribute access rather than string-key indexing.", "positive_progress": "AST evidence and a synthetic nonempty namedtuple reproduce TypeError without opening outputs.", "residual": "Any nonempty raw TSV reaching MappingRefiner is conditionally blocked; an empty table avoids only this loop.", "next_discriminator": "Freeze a separately identified source repair (for example dp.Score), then exercise nonempty and empty synthetic tables before any model run."},
        {"id": "P3V7-N05", "negative_result": "raw_mappings.json and raw_mappings.tsv are checkpoint/resume artifacts, not intrinsically completion proofs.", "cause": "Pinned source saves at index 0, every 100 classes and the final class, and loads existing JSON on resume.", "positive_progress": "The V7 parser requires the exact predeclared eligible source-key set and JSON/TSV equivalence.", "residual": "No native artifacts were produced in V7.", "next_discriminator": "Apply the closed parser to a fresh isolated execution directory and reject any missing source key or stale sidecar."},
        {"id": "P3V7-N06", "negative_result": "Pinned refinement trusts pre-existing extended, filtered or repaired TSV files after only native table loading.", "cause": "The released resume paths do not bind provenance or derivation completeness.", "positive_progress": "The external parser binds universe, raw retention, exact filter derivation, repaired-pair containment and hashes.", "residual": "Parser conformance is authored adapter evidence, not native execution evidence.", "next_discriminator": "Require an empty execution directory plus before/after file census and the closed parser on every future run."},
        {"id": "P3V7-N07", "negative_result": "Complete runtime rights and SBOM closure is absent.", "cause": "DeepOnto tracks 208 JARs and the original repository 106 JARs; the constructor island is not the full runtime.", "positive_progress": "Both root Apache-2.0 source layers, all exact source hashes, metadata censuses and 26 installed distribution licence metadata records are retained.", "residual": "Bundled Java components, full Python closure, model, generated artifacts and evaluation custody remain unadjudicated.", "next_discriminator": "Produce component-level Python/Java SBOM and rights decisions before retaining or distributing a full runtime."},
        {"id": "P3V7-N08", "negative_result": "The original BERTMap repository contains a paper data.zip described as ontologies plus reference mappings.", "cause": "The canonical research repository packages outcome-bearing paper data beside source.", "positive_progress": "Only ls-tree metadata was recorded; the 2,017,453-byte blob was not opened and is excluded.", "residual": "Paper-data rights, custody and independence are CANNOT_CHECK.", "next_discriminator": "Use only separately rights-cleared, independently custodied inputs under a frozen evaluation protocol."},
        {"id": "P3V7-N09", "negative_result": "BERTMap still has zero of five required native artifacts in the retained evidence chain.", "cause": "V7 intentionally prohibited model and ontology execution while resolving source/runtime/parser blockers.", "positive_progress": "Dependency constructor and fail-closed parser bindings are now independently reproducible.", "residual": "Three-family native smoke remains 2/3.", "next_discriminator": "After a versioned source repair and complete runtime/rights closure, run one fresh no-gold BERTMap smoke under the unchanged five-artifact gate."},
        {"id": "P3V7-N10", "negative_result": "No BERTMap scientific comparison is available.", "cause": "No gold/reference, naturalistic ontology, protected outcome, training, prediction, repair or scoring was opened or performed.", "positive_progress": "The evidence boundary is explicit and machine-checked.", "residual": "V5 scientific comparator readiness remains 0/3; correctness, coverage, harm, transport and superiority are CANNOT_CHECK.", "next_discriminator": "Only after 3/3 native readiness, freeze independently custodied rights-valid evaluation data and score all comparators under one no-feedback protocol."},
    ]
    dump("NEGATIVE_RESULT_LEDGER_V7.json", {"schema_version": "orion.p3.bertmap-execution-binding.negative-ledger.v7", "rule": "Every negative remains a research object with cause, positive progress, residual and next discriminator.", "entries": negatives})
    lines = ["# P3 BERTMap V7 recursive negative-result ledger", "", "Every negative remains an active research object. Progress is bounded to what the evidence establishes.", "", "| ID | Negative result | Cause | Positive progress | Residual | Next discriminator |", "|---|---|---|---|---|---|"]
    for item in negatives:
        lines.append("| " + " | ".join(item[k].replace("|", "\\|") for k in ["id", "negative_result", "cause", "positive_progress", "residual", "next_discriminator"]) + " |")
    (ROOT / "NEGATIVE_RESULT_LEDGER_V7.md").write_text("\n".join(lines) + "\n")

    result = {
        "schema_version": "orion.p3.bertmap-execution-binding.result.v7",
        "protocol_id": protocol["protocol_id"],
        "authority": protocol["authority"],
        "terminal": TERMINAL,
        "paper_source_identity": "BOUND",
        "source_root_rights": "BOUND_APACHE_2_0__FULL_RUNTIME_RIGHTS_NOT_CLOSED",
        "dependency_api_compatibility": runtime["terminal"],
        "native_parser_binding": "BOUND__SEVEN_OF_SEVEN_SYNTHETIC_CONTRACT_CHECKS",
        "full_native_bertmap_execution": "CANNOT_CHECK__NOT_RUN",
        "required_native_artifacts": {"present": 0, "required": 5},
        "readiness_delta": {
            "api_keyword_compatibility": "CANNOT_CHECK_IN_V6_TO_CONSTRUCTOR_PASS_IN_V7",
            "native_artifact_parser": "GENERIC_SHAPE_GATE_TO_CLOSED_COMPLETENESS_AND_DERIVATION_PARSER",
            "paper_maintained_source_bridge": "REVALIDATED_EXACT",
            "native_smoke_ready_before": "2/3",
            "native_smoke_ready_after": "2/3",
            "scientific_comparator_ready_before": "0/3",
            "scientific_comparator_ready_after": "0/3",
            "net_comparator_readiness_change": 0,
        },
        "material_source_defect": runtime["source_native_reader_audit"],
        "remaining_blockers": [
            "separately versioned repair of the nonempty EntityMapping table-reader defect",
            "complete content-addressed DeepOnto Python/JVM runtime rather than a constructor-only island",
            "component-level rights/SBOM closure for bundled Java and full Python/model/generated-artifact layers",
            "fresh isolated no-model-feedback BERTMap run producing all five parseable artifacts",
            "independently custodied rights-valid evaluation before any correctness, performance, harm, coverage, transport or superiority claim",
        ],
        "outcome_boundary": {
            "model_opened_or_run": False,
            "ontology_or_benchmark_opened_or_run": False,
            "paper_data_zip_opened": False,
            "gold_or_reference_opened": False,
            "protected_outcomes_opened": False,
            "training_prediction_repair_or_scoring": False,
        },
        "preserved_terminals": {
            "v6": json.loads((V6 / "RESULT_V6.json").read_text())["terminal"],
            "v5_scientific_comparator_readiness": "0/3",
        },
        "evidence": {
            "protocol_sha256": freeze["protocol_sha256"],
            "runtime_receipt_sha256": sha(ROOT / "RUNTIME_COMPATIBILITY_RECEIPT_V7.json"),
            "parser_sha256": sha(ROOT / "bertmap_native_parser_v7.py"),
            "parser_self_test_sha256": sha(ROOT / "PARSER_SELF_TEST_RECEIPT_V7.json"),
            "source_rights_manifest_sha256": sha(ROOT / "SOURCE_RIGHTS_MANIFEST_V7.json"),
            "native_artifact_contract_sha256": sha(ROOT / "NATIVE_ARTIFACT_CONTRACT_V7.json"),
            "compatibility_lock_sha256": sha(ROOT / "V7_COMPATIBILITY_REQUIREMENTS.txt"),
            "compatibility_island_manifest_sha256": sha(ROOT / "COMPATIBILITY_ISLAND_MANIFEST_V7.json"),
        },
    }
    dump("RESULT_V7.json", result)

    report = f"""# P3 BERTMap execution binding V7

## Terminal

`{TERMINAL}`

## Exact result

The exact paper/source bridge is bound: the canonical original repository at
`ce848402b40e2f9513bf2d004894d3f82635022c` says BERTMap is now maintained in
DeepOnto, and DeepOnto 0.9.3 at
`74ca8d47f01bad0b8739f19ee2c392bdf6d9c090` links both that repository and the
AAAI paper (DOI `10.1609/aaai.v36i5.20510`). Both root source layers are
Apache-2.0.

The V6 dependency failure is repaired **only at constructor level**. In a
hash-locked Python-3.10.20/macOS-arm64 compatibility island, exact versions
Transformers 4.46.3, Tokenizers 0.20.3, Accelerate 1.0.1 and Torch 2.5.1
imported, the `evaluation_strategy` signature existed, and the exact
`TrainingArguments` construction returned. The installed source hash is
`{runtime['compatibility']['training_arguments_source_sha256']}`. That keyword
is already deprecated in 4.46.3, so floating upgrades remain forbidden.

This is not a BERTMap run. DeepOnto was not imported, no JVM was started, and
no model, ontology, benchmark, paper `data.zip`, gold/reference alignment,
protected outcome, training, prediction, repair or scoring was opened or run.

## New downstream blocker

Pinned `src/deeponto/align/mapping.py` lines 119--151 iterates
`pandas.DataFrame.itertuples()` rows and then uses `dp["Score"]`. Such rows are
namedtuples; the synthetic nonempty source-semantic fixture returns
`{runtime['source_native_reader_audit']['synthetic_nonempty_row_error']}`.
Therefore any nonempty raw TSV reaching `MappingRefiner` is conditionally
blocked. This defect was not patched: a repair requires a new source identity.

## Closed native artifact parser

`bertmap_native_parser_v7.py` passed {parser_receipt['passed']}/{parser_receipt['check_count']}
direct synthetic checks. It requires all five files, exact eligible source-key
coverage (including empty lists), JSON/TSV equivalence, universe guards,
finite `[0,1]` scores, raw retention, exact filtering, repaired-pair
containment and SHA-256 hashes. A complete zero-row artifact set passes;
absence is never obstruction. Parser pass has interface authority only.

## Readiness delta

| Axis | Before | After | Delta |
|---|---:|---:|---|
| BERTMap dependency keyword | CANNOT_CHECK | constructor-only PASS | repaired locally |
| BERTMap closed artifact parser | generic shape gate | source-native fail-closed parser | bound |
| Three-family native smoke | 2/3 | 2/3 | 0 |
| V5 scientific comparator readiness | 0/3 | 0/3 | 0 |
| BERTMap required artifacts | 0/5 | 0/5 | 0 |

## Rights boundary

The constructor island contains {runtime['distribution_count']} installed distributions and all expose
some licence metadata. That is not a complete runtime SBOM. The pinned
DeepOnto tree contains {deep_census['jar_files']} JAR entries ({deep_census['jar_bytes']:,} bytes), and the
original BERTMap tree contains {bert_census['jar_files']} JAR entries ({bert_census['jar_bytes']:,} bytes).
Their component-level provenance/licences, the full Python/JVM closure, model,
generated artifacts, OAEI submodule and independent evaluation custody remain
unclosed. The original `data.zip` is a {bert_data['bytes']:,}-byte blob described
as paper ontologies plus reference mappings; it was not opened and is excluded.

## Remaining blockers

1. freeze a separately identified repair for the nonempty table-reader defect;
2. bind the complete Python/JVM runtime and component-level rights/SBOM;
3. run one fresh isolated no-gold smoke and require all five files to pass the closed parser;
4. only then freeze independent, rights-valid evaluation custody.

Correctness, coverage, harm, transport, performance, superiority and top-tier
readiness remain `CANNOT_CHECK` / not established.
"""
    (ROOT / "SCIENTIFIC_REPORT_V7.md").write_text(report)
    (ROOT / "README.md").write_text(
        "# P3 BERTMap execution binding V7\n\n"
        "Outcome-blind source/runtime/parser repair packet. Start with `SCIENTIFIC_REPORT_V7.md`, "
        "`RESULT_V7.json`, and `NEGATIVE_RESULT_LEDGER_V7.md`. No model, ontology, benchmark, "
        "gold/reference alignment, protected outcome, training, prediction, repair or scoring was opened or run.\n"
    )

    audit = {
        "schema_version": "orion.p3.bertmap-execution-binding.audit-receipt.v7",
        "audited_at": now(),
        "protocol_hash_match": freeze["protocol_sha256"] == sha(ROOT / "PROTOCOL_V7.json"),
        "paper_source_bridge": "PASS",
        "dependency_constructor": runtime["terminal"],
        "parser_self_test": parser_receipt["terminal"],
        "nonempty_reader_defect_retained": True,
        "native_bertmap_executed": False,
        "native_artifacts_opened": False,
        "paper_data_zip_opened": False,
        "model_or_ontology_opened_or_run": False,
        "gold_reference_or_protected_outcomes_opened": False,
        "performance_scoring_performed": False,
        "terminal": "PASS_OUTCOME_BLIND_BINDING__FULL_NATIVE_AND_SCIENTIFIC_CANNOT_CHECK",
    }
    dump("AUDIT_RECEIPT_V7.json", audit)
    print(TERMINAL)


if __name__ == "__main__":
    main()
