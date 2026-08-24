#!/usr/bin/env python3
"""Run the frozen BERTMap V7 dependency-constructor compatibility probe.

This script deliberately does not import DeepOnto, start a JVM, open a model,
load an ontology, train, predict, repair, or score.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import inspect
import json
import os
import platform
import sys
import tempfile
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEEPO = ROOT / "_runtime/deeponto"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_reader_audit() -> dict:
    mapping_path = DEEPO / "src/deeponto/align/mapping.py"
    source = mapping_path.read_text()
    tree = ast.parse(source)
    target = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "read_table_mappings":
            # There are EntityMapping and ReferenceMapping methods.  The defect
            # is the method containing a subscript dp["Score"].
            if any(
                isinstance(child, ast.Subscript)
                and isinstance(child.value, ast.Name)
                and child.value.id == "dp"
                and isinstance(child.slice, ast.Constant)
                and child.slice.value == "Score"
                for child in ast.walk(node)
            ):
                target = node
                break
    if target is None:
        raise RuntimeError("source-native dp['Score'] expression not found")
    row_type = namedtuple("Pandas", ["Index", "SrcEntity", "TgtEntity", "Score"])
    row = row_type(0, "urn:s:A", "urn:t:A", 1.0)
    observed_error = None
    try:
        row["Score"]
    except Exception as exc:  # exact source expression under namedtuple semantics
        observed_error = f"{type(exc).__name__}: {exc}"
    return {
        "source_path": "src/deeponto/align/mapping.py",
        "source_sha256": sha(mapping_path),
        "function_line_span": [target.lineno, target.end_lineno],
        "dp_string_subscript_found": True,
        "pandas_itertuples_row_semantics": "namedtuple; positional or attribute access, not string-key indexing",
        "synthetic_nonempty_row_error": observed_error,
        "conditional_effect": "Any nonempty non-reference table read reaches dp['Score'] and raises TypeError; an empty table does not enter the loop.",
        "authority": "SOURCE_SEMANTIC_AND_SYNTHETIC_LANGUAGE_LEVEL_REPRODUCTION_ONLY__NO_BERTMAP_OUTPUT_OPENED",
    }


def distribution_manifest() -> list[dict]:
    rows = []
    for distribution in importlib.metadata.distributions():
        metadata = distribution.metadata
        classifiers = metadata.get_all("Classifier") or []
        rows.append(
            {
                "name": metadata.get("Name") or "UNKNOWN",
                "version": distribution.version,
                "license": metadata.get("License"),
                "license_expression": metadata.get("License-Expression"),
                "license_classifiers": sorted(x for x in classifiers if x.startswith("License ::")),
                "home_page": metadata.get("Home-page"),
            }
        )
    return sorted(rows, key=lambda x: (x["name"].casefold(), x["version"]))


def main() -> None:
    os.environ.update(
        {
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
        }
    )
    import accelerate
    import tokenizers
    import torch
    import transformers
    from transformers import TrainingArguments

    versions = {
        "accelerate": accelerate.__version__,
        "tokenizers": tokenizers.__version__,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
    }
    expected = {"accelerate": "1.0.1", "tokenizers": "0.20.3", "torch": "2.5.1", "transformers": "4.46.3"}
    exact_versions = versions == expected
    signature = inspect.signature(TrainingArguments)
    evaluation_strategy_present = "evaluation_strategy" in signature.parameters
    with tempfile.TemporaryDirectory(prefix="p3v7-training-arguments-") as temp:
        args = TrainingArguments(
            output_dir=temp,
            num_train_epochs=3.0,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            warmup_ratio=0.0,
            weight_decay=0.01,
            logging_steps=2,
            logging_dir=f"{temp}/tensorboard",
            eval_steps=20,
            evaluation_strategy="steps",
            do_train=True,
            do_eval=True,
            save_steps=20,
            save_total_limit=2,
            load_best_model_at_end=True,
            report_to=[],
        )
        observed_strategy = str(args.evaluation_strategy)
        if observed_strategy.startswith("IntervalStrategy."):
            observed_strategy = observed_strategy.split(".", 1)[1].lower()
        constructed = observed_strategy == "steps" and args.eval_steps == 20 and args.save_steps == 20
    training_args_file = Path(inspect.getsourcefile(TrainingArguments) or "")
    training_args_source = training_args_file.read_text()
    evaluation_strategy_deprecated = (
        "`evaluation_strategy` is deprecated" in training_args_source
        and "Use `eval_strategy` instead" in training_args_source
    )
    distributions = distribution_manifest()
    terminal = (
        "DEPENDENCY_API_CONSTRUCTOR_PASS"
        if exact_versions and evaluation_strategy_present and constructed
        else "CANNOT_CHECK_DEPENDENCY_API_CONSTRUCTOR"
    )
    receipt = {
        "schema_version": "orion.p3.bertmap-execution-binding.runtime-compatibility.v7",
        "probed_at": now(),
        "terminal": terminal,
        "authority": "DEPENDENCY_SIGNATURE_AND_CONSTRUCTOR_COMPATIBILITY_ONLY__NOT_DEEPONTO_OR_BERTMAP_EXECUTION",
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "offline_guards": {key: os.environ[key] for key in ["HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "TOKENIZERS_PARALLELISM", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"]},
        },
        "compatibility": {
            "expected_versions": expected,
            "observed_versions": versions,
            "exact_versions_match": exact_versions,
            "training_arguments_signature_has_evaluation_strategy": evaluation_strategy_present,
            "training_arguments_constructor_pass": constructed,
            "training_arguments_source_marks_evaluation_strategy_deprecated": evaluation_strategy_deprecated,
            "training_arguments_source_path_within_disposable_venv": str(training_args_file),
            "training_arguments_source_sha256": sha(training_args_file),
        },
        "source_native_reader_audit": source_reader_audit(),
        "distribution_count": len(distributions),
        "distributions": distributions,
        "forbidden_operations": {
            "deeponto_imported": "deeponto" in sys.modules,
            "jvm_started": False,
            "model_opened_or_run": False,
            "ontology_or_benchmark_opened_or_run": False,
            "gold_or_reference_opened": False,
            "protected_outcomes_opened": False,
            "training_prediction_repair_or_scoring": False,
        },
    }
    (ROOT / "RUNTIME_COMPATIBILITY_RECEIPT_V7.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"terminal": terminal, "versions": versions, "distribution_count": len(distributions)}, sort_keys=True))
    if terminal != "DEPENDENCY_API_CONSTRUCTOR_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
