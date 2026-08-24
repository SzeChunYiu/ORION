#!/usr/bin/env python3
"""Outcome-blind language-level execution of the prospectively frozen V8 repair.

This script does not import DeepOnto, start a JVM, or open any model, ontology,
benchmark, gold/reference alignment, protected outcome, prediction, or score.
"""
from __future__ import annotations

import ast
import csv
import difflib
import hashlib
import importlib.util
import inspect
import json
import platform
import shutil
import sys
sys.dont_write_bytecode = True
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
V7 = ROOT.parent / "p3-bertmap-execution-binding-v7-2026-08-23"
SOURCE = ROOT / "PINNED_MAPPING_V7.py"
PROTOCOL = ROOT / "PROTOCOL_V8.json"
PATCH = ROOT / "mapping_dp_score_v8.patch"
RECEIPT = ROOT / "LANGUAGE_LEVEL_EXECUTION_RECEIPT_V8.json"
OLD = 'dp["Score"]'
NEW = "dp.Score"
EXPECTED_SOURCE_SHA = "9cf0dce1c5bd142e4175f628f8f3267f54ed6deac9f31e165a25b4a073eedff0"
EXPECTED_PARSER_SHA = "d1184dc129082bdcf18b415b551f244a695b4e34417286afc37a3f3a5d788bc5"
TERMINAL = (
    "P3_V8_BERTMAP_TABLE_READER_MINIMAL_REPAIR_SOURCE_HASH_AND_SYNTHETIC_EMPTY_NONEMPTY_EXECUTION_BOUND__"
    "MALFORMED_STALE_AND_PROHIBITED_CASES_FAIL_CLOSED__V7_PARSER_SYNTHETIC_COMPATIBILITY_BOUND__"
    "NATIVE_SMOKE_AND_SCIENTIFIC_READINESS_UNCHANGED"
)


class SourceIdentityError(ValueError):
    pass


class ProhibitedOperation(ValueError):
    pass


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def strict_repair(source: str) -> str:
    if sha_bytes(source.encode()) != EXPECTED_SOURCE_SHA:
        raise SourceIdentityError("source SHA-256 is not the prospectively frozen DeepOnto mapping.py identity")
    if source.count(OLD) != 1:
        raise SourceIdentityError("frozen source must contain exactly one dp[\"Score\"] expression")
    repaired = source.replace(OLD, NEW, 1)
    expected = json.loads(PROTOCOL.read_text())["single_intended_change"]["expected_repaired_mapping_sha256"]
    if sha_bytes(repaired.encode()) != expected:
        raise SourceIdentityError("repaired source SHA-256 differs from prospective freeze")
    return repaired


def exact_patch(original: str, repaired: str) -> str:
    lines = list(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            repaired.splitlines(keepends=True),
            fromfile="a/src/deeponto/align/mapping.py",
            tofile="b/src/deeponto/align/mapping.py",
        )
    )
    return "".join(lines)


def target_method(tree: ast.AST) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "read_table_mappings":
            return node
    raise AssertionError("read_table_mappings absent")


def compile_exact_entity_mapping(source: str, read_table):
    tree = ast.parse(source)
    class_node = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "EntityMapping"
    )
    keep = [
        node
        for node in class_node.body
        if isinstance(node, ast.FunctionDef) and node.name in {"__init__", "read_table_mappings"}
    ]
    assert {node.name for node in keep} == {"__init__", "read_table_mappings"}
    reduced_class = ast.ClassDef(
        name="EntityMapping",
        bases=[],
        keywords=[],
        body=keep,
        decorator_list=[],
    )
    module = ast.Module(
        body=[
            ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
            reduced_class,
        ],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    namespace: dict[str, Any] = {
        "Optional": __import__("typing").Optional,
        "List": __import__("typing").List,
        "DEFAULT_REL": "<?rel>",
        "read_table": read_table,
    }
    exec(compile(module, "<exact-pinned-mapping-method>", "exec"), namespace)
    namespace["ReferenceMapping"] = type("ReferenceMapping", (), {})
    return namespace["EntityMapping"]


def canonical_method_dump(source: str, normalize_bad_access: bool) -> str:
    node = target_method(ast.parse(source))
    if normalize_bad_access:
        class Normalize(ast.NodeTransformer):
            def visit_Subscript(self, child):  # noqa: N802
                child = self.generic_visit(child)
                if (
                    isinstance(child.value, ast.Name)
                    and child.value.id == "dp"
                    and isinstance(child.slice, ast.Constant)
                    and child.slice.value == "Score"
                ):
                    return ast.copy_location(ast.Attribute(value=child.value, attr="Score", ctx=child.ctx), child)
                return child
        node = Normalize().visit(node)
        ast.fix_missing_locations(node)
    return ast.dump(node, include_attributes=False)


def error(callable_) -> str | None:
    try:
        callable_()
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return None


def row_values(rows) -> list[dict[str, Any]]:
    return [
        {"head": row.head, "tail": row.tail, "relation": row.relation, "score": row.score}
        for row in rows
    ]


def load_v7_parser():
    parser_path = V7 / "bertmap_native_parser_v7.py"
    if sha(parser_path) != EXPECTED_PARSER_SHA:
        raise AssertionError("V7 parser identity mismatch")
    spec = importlib.util.spec_from_file_location("p3_v7_parser_for_v8", parser_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parser_synthetic_check(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Exercise the exact V7 parser on authored fixtures, then delete all five files."""
    parser = load_v7_parser()
    work = ROOT / "_synthetic_parser_work_v8"
    if work.exists():
        shutil.rmtree(work)
    out = work / "match"
    out.mkdir(parents=True)
    try:
        sources = ["urn:synthetic:source:A", "urn:synthetic:source:B"]
        targets = ["urn:synthetic:target:X", "urn:synthetic:target:Y"]
        remapped = [
            (sources[i], targets[i], str(row["score"])) for i, row in enumerate(rows)
        ]
        raw = {source: [] for source in sources}
        for source, target, score in remapped:
            raw[source].append([source, target, score])
        (out / "raw_mappings.json").write_text(json.dumps(raw, sort_keys=True) + "\n")

        def write_tsv(path: Path, values):
            with path.open("w", newline="") as handle:
                writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
                writer.writerow(["SrcEntity", "TgtEntity", "Score"])
                writer.writerows(values)

        write_tsv(out / "raw_mappings.tsv", remapped)
        write_tsv(out / "extended_mappings.tsv", remapped)
        filtered = [row for row in remapped if float(row[2]) >= 0.5]
        write_tsv(out / "filtered_mappings.tsv", filtered)
        write_tsv(out / "repaired_mappings.tsv", filtered)
        manifest = {
            "schema_version": "orion.p3.bertmap-universe-manifest.v7",
            "expected_source_iris": sources,
            "expected_target_iris": targets,
            "mapping_extension_threshold": "0.0",
            "mapping_filtered_threshold": "0.5",
            "for_oaei": False,
            "excluded_source_iris": [],
        }
        manifest_path = work / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n")
        parsed = parser.parse_contract(out, manifest_path)
        artifact_hashes = {name: sha(out / name) for name in parser.REQUIRED_FILES}
        return {
            "terminal": parsed["terminal"],
            "authority": "SYNTHETIC_INTERFACE_COMPATIBILITY_ONLY__NOT_NATIVE_BERTMAP_ARTIFACTS_OR_SMOKE",
            "parser_sha256": EXPECTED_PARSER_SHA,
            "synthetic_files_created_then_deleted": list(parser.REQUIRED_FILES),
            "synthetic_artifact_hashes": artifact_hashes,
            "row_counts": parsed["row_counts"],
            "actual_native_artifacts_present": 0,
            "actual_native_artifacts_required": 5,
            "native_smoke_claimed": False,
        }
    finally:
        if work.exists():
            shutil.rmtree(work)


def run() -> tuple[str, dict[str, Any]]:
    protocol = json.loads(PROTOCOL.read_text())
    original = SOURCE.read_text()
    repaired = strict_repair(original)
    patch_text = exact_patch(original, repaired)
    if patch_text.count('-                if not threshold or dp["Score"] >= threshold:') != 1:
        raise AssertionError("patch does not remove exactly the frozen defective line")
    if patch_text.count('+                if not threshold or dp.Score >= threshold:') != 1:
        raise AssertionError("patch does not add exactly the intended repaired line")

    registry = {
        "synthetic://empty": pd.DataFrame(columns=["SrcEntity", "TgtEntity", "Score"]),
        "synthetic://nonempty": pd.DataFrame(
            [
                {"SrcEntity": "urn:synthetic:source:A", "TgtEntity": "urn:synthetic:target:X", "Score": 0.9},
                {"SrcEntity": "urn:synthetic:source:B", "TgtEntity": "urn:synthetic:target:Y", "Score": 0.4},
            ]
        ),
        "synthetic://missing-score": pd.DataFrame(
            [{"SrcEntity": "urn:synthetic:source:A", "TgtEntity": "urn:synthetic:target:X"}]
        ),
        "synthetic://nonnumeric-score": pd.DataFrame(
            [{"SrcEntity": "urn:synthetic:source:A", "TgtEntity": "urn:synthetic:target:X", "Score": "not-a-number"}]
        ),
    }
    access_log: list[str] = []

    def read_table(uri: str):
        access_log.append(uri)
        if uri not in registry:
            raise ProhibitedOperation("only frozen in-memory synthetic fixture identifiers are allowed")
        return registry[uri].copy(deep=True)

    Original = compile_exact_entity_mapping(original, read_table)
    Repaired = compile_exact_entity_mapping(repaired, read_table)

    def guarded(cls, uri: str, *, threshold=None, is_reference=False):
        if is_reference:
            raise ProhibitedOperation("reference-mode access is prohibited in V8")
        if uri not in registry:
            raise ProhibitedOperation("external or unregistered table access is prohibited in V8")
        return cls.read_table_mappings(uri, threshold=threshold, is_reference=False)

    cases: list[dict[str, Any]] = []
    original_empty = row_values(guarded(Original, "synthetic://empty", threshold=0.5))
    repaired_empty = row_values(guarded(Repaired, "synthetic://empty", threshold=0.5))
    cases.append({"id": "SYN_EMPTY_NONREFERENCE", "pass": original_empty == repaired_empty == [], "original": original_empty, "repaired": repaired_empty})

    original_none = row_values(guarded(Original, "synthetic://nonempty", threshold=None))
    repaired_none = row_values(guarded(Repaired, "synthetic://nonempty", threshold=None))
    cases.append({"id": "SYN_NONEMPTY_THRESHOLD_NONE", "pass": original_none == repaired_none and len(repaired_none) == 2, "original": original_none, "repaired": repaired_none, "scope_correction": "The V7 defect does not trigger when threshold is None or another falsey value because Python short-circuits before dp[\"Score\"]."})

    original_threshold_error = error(lambda: guarded(Original, "synthetic://nonempty", threshold=0.5))
    repaired_threshold = row_values(guarded(Repaired, "synthetic://nonempty", threshold=0.5))
    cases.append({"id": "SYN_NONEMPTY_THRESHOLD", "pass": original_threshold_error is not None and original_threshold_error.startswith("TypeError:") and repaired_threshold == [{"head":"urn:synthetic:source:A","tail":"urn:synthetic:target:X","relation":"<?rel>","score":0.9}], "original_error": original_threshold_error, "repaired": repaired_threshold})

    missing_error = error(lambda: guarded(Repaired, "synthetic://missing-score", threshold=0.5))
    cases.append({"id": "MALFORMED_MISSING_SCORE", "pass": bool(missing_error and missing_error.startswith("AttributeError:")), "error": missing_error})
    nonnumeric_error = error(lambda: guarded(Repaired, "synthetic://nonnumeric-score", threshold=0.5))
    cases.append({"id": "MALFORMED_NONNUMERIC_SCORE", "pass": bool(nonnumeric_error and nonnumeric_error.startswith("TypeError:")), "error": nonnumeric_error})

    stale_error = error(lambda: strict_repair(original + "\n# stale mutation\n"))
    cases.append({"id": "STALE_SOURCE_HASH", "pass": bool(stale_error and stale_error.startswith("SourceIdentityError:")), "error": stale_error})

    before = len(access_log)
    reference_error = error(lambda: guarded(Repaired, "synthetic://nonempty", threshold=0.5, is_reference=True))
    cases.append({"id": "PROHIBITED_REFERENCE_MODE", "pass": bool(reference_error and reference_error.startswith("ProhibitedOperation:") and len(access_log) == before), "error": reference_error, "table_access_delta": len(access_log)-before})
    before = len(access_log)
    external_error = error(lambda: guarded(Repaired, "/tmp/external.tsv", threshold=0.5))
    cases.append({"id": "PROHIBITED_EXTERNAL_FIXTURE", "pass": bool(external_error and external_error.startswith("ProhibitedOperation:") and len(access_log) == before), "error": external_error, "table_access_delta": len(access_log)-before})

    parser_check = parser_synthetic_check(repaired_none)
    semantic_ast_equivalent = canonical_method_dump(original, True) == canonical_method_dump(repaired, False)
    all_cases_pass = all(case["pass"] for case in cases)
    patch_sha = sha_bytes(patch_text.encode())
    pandas_source = Path(inspect.getsourcefile(pd.DataFrame.itertuples) or pd.__file__ or "")

    receipt = {
        "schema_version": "orion.p3.bertmap-table-reader-repair.language-level-execution.v8",
        "protocol_id": protocol["protocol_id"],
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "terminal": TERMINAL if all_cases_pass and semantic_ast_equivalent and parser_check["terminal"] == "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS" else "P3_V8_BERTMAP_TABLE_READER_REPAIR_CANNOT_CHECK",
        "authority": "EXACT_SOURCE_PATCH_AND_OUTCOME_BLIND_SYNTHETIC_LANGUAGE_LEVEL_EXECUTION_ONLY__NOT_DEEPONTO_OR_NATIVE_BERTMAP_EXECUTION",
        "source_identity": {
            "repository": protocol["predecessor"]["deeponto_repository"],
            "commit": protocol["predecessor"]["deeponto_commit"],
            "tree": protocol["predecessor"]["deeponto_tree"],
            "path": protocol["predecessor"]["mapping_path"],
            "original_sha256": sha_bytes(original.encode()),
            "repaired_sha256": sha_bytes(repaired.encode()),
            "expected_repaired_sha256": protocol["single_intended_change"]["expected_repaired_mapping_sha256"],
            "root_license_spdx": "Apache-2.0",
            "upstream_license_sha256": sha(ROOT / "UPSTREAM_LICENSE.txt"),
            "patch_file": PATCH.name,
            "patch_sha256": patch_sha,
            "changed_expression_count": 1,
            "changed_source_lines_removed": 1,
            "changed_source_lines_added": 1,
        },
        "semantic_equivalence_boundary": {
            "ast_equivalent_after_normalizing_only_frozen_access": semantic_ast_equivalent,
            "changed_expression": {"before": OLD, "after": NEW},
            "changed_behavior": "Truthy-threshold comparison now reads the itertuples namedtuple Score attribute and can apply the existing >= threshold rule.",
            "unchanged_behavior": [
                "empty non-reference tables return an empty list",
                "falsey thresholds short-circuit comparison and retain all rows",
                "EntityMapping construction, source/target fields, relation and stored score are unchanged",
                "reference branch text and behavior are unchanged and were not executed",
                "table acquisition, model behavior, mapping generation, repair algorithms and evaluation are outside this patch",
            ],
            "v7_scope_correction": "The V7 statement that any nonempty non-reference table triggers TypeError was too broad: the defective subscript executes only when threshold is truthy."
        },
        "synthetic_execution": {
            "pandas_version": pd.__version__,
            "pandas_itertuples_source_path": str(pandas_source),
            "pandas_itertuples_source_sha256": sha(pandas_source),
            "case_count": len(cases),
            "pass_count": sum(case["pass"] for case in cases),
            "cases": cases,
            "fixture_authority": "authored in-memory IRIs and scores only; not an ontology, benchmark, gold/reference or protected outcome",
        },
        "parser_compatibility": parser_check,
        "v7_compatibility_island": {
            "distribution_count": protocol["predecessor"]["compatibility_island_distribution_count"],
            "lock_sha256": protocol["predecessor"]["compatibility_lock_sha256"],
            "manifest_sha256": protocol["predecessor"]["compatibility_manifest_sha256"],
            "status": "UNCHANGED_AND_NOT_REEXECUTED__CONSTRUCTOR_ONLY",
            "boundary": "The pandas language-level harness is not promoted into the V7 26-distribution island or a complete DeepOnto runtime."
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "forbidden_operations": {
            "deeponto_imported": "deeponto" in sys.modules,
            "jvm_started": False,
            "model_opened_or_run": False,
            "ontology_or_benchmark_opened_or_run": False,
            "paper_data_zip_opened": False,
            "gold_or_reference_opened": False,
            "protected_outcomes_opened": False,
            "training_prediction_repair_or_scoring": False,
        },
        "readiness_delta": {
            "table_reader_truthy_threshold_source_defect": "BLOCKING_TO_REPAIRED_AT_EXACT_PATCH_AND_SYNTHETIC_LANGUAGE_LEVEL_BOUNDARY",
            "native_smoke_ready_before": "2/3",
            "native_smoke_ready_after": "2/3",
            "scientific_comparator_ready_before": "0/3",
            "scientific_comparator_ready_after": "0/3",
            "net_native_smoke_readiness_change": 0,
            "net_scientific_comparator_readiness_change": 0,
            "actual_native_artifacts_present": 0,
            "actual_native_artifacts_required": 5,
        },
        "remaining_blockers": [
            "complete content-addressed DeepOnto Python runtime beyond the V7 constructor-only 26-distribution island",
            "component-level provenance, rights decisions and SBOM closure for the JVM/JAR layer",
            "one fresh isolated no-gold native BERTMap run under the exact repaired source producing all five actual parseable artifacts",
            "independently custodied rights-valid evaluation before correctness, coverage, harm, transport, performance or superiority claims",
        ],
        "next_discriminator": "Bind a complete content-addressed repaired Python/JVM runtime with component-level rights/SBOM, then run the unchanged no-gold five-artifact smoke; stop if any actual artifact is absent or fails the frozen V7 parser.",
    }
    return patch_text, receipt


def main() -> None:
    patch_text, receipt = run()
    PATCH.write_text(patch_text)
    receipt["source_identity"]["patch_sha256"] = sha(PATCH)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": receipt["terminal"], "cases": f"{receipt['synthetic_execution']['pass_count']}/{receipt['synthetic_execution']['case_count']}", "patch_sha256": receipt["source_identity"]["patch_sha256"], "actual_native_artifacts": "0/5"}, sort_keys=True))
    if receipt["terminal"] != TERMINAL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
