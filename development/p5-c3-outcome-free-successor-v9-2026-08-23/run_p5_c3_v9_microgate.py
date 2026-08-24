#!/usr/bin/env python3
"""Run exactly one cheapest decisive V9 static microgate and freeze receipts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V8 = ROOT / "development" / "p5-c3-native-environment-v8-2026-08-23"
SEED = V8 / "P5_C3_CANDIDATE_SAFE_SEED_V8.tar.gz"
PREREG = HERE / "P5_C3_V9_SUCCESSOR_ADAPTER_PREREGISTRATION.json"
ADAPTER = HERE / "p5_c3_outcome_free_initializer_v9.py"
RECEIPT = HERE / "P5_C3_V9_MICROGATE_RECEIPT.json"
TERMINAL = (
    "P5_C3_V9_OUTCOME_FREE_INITIALIZATION_ADAPTER_STOPPED__"
    "UNCHANGED_NATIVE_PARENT_SELECTION_REQUIRES_PRIOR_OUTCOME_METADATA__"
    "NO_LAWFUL_SEMANTICS_PRESERVING_ADAPTER__RUNTIME_TASK_ENVIRONMENT_REMAINS_BLOCKING"
)
EXPECTED_CORE = {
    "candidate/shared_core/APACHE-2.0-LICENSE.txt": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "candidate/shared_core/APACHE-NOTICE.txt": "3b1830189d4da56ebc6e43f32a96b92caa3392cdc0c5ba4af7c399f81696545d",
    "candidate/shared_core/CASE_BODY_V6.json": "3e5d001eee38d62c93c5f00acf59adba0a55cadf6df7040bdb2c432c1c16f921",
    "candidate/shared_core/PACKET-CONTENT-CC0-1.0.txt": "a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499",
    "candidate/shared_core/TASK_SPECIFICATION_V6.md": "a455eec2d32b031b6e49d06c73e0cf3befbe9e2cd461e5417efbade5f39f5098",
    "candidate/shared_core/source/commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz": "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08",
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    v8_hashes_before = {
        "seed": file_digest(SEED),
        "receipt": file_digest(V8 / "P5_C3_NATIVE_TASK_ENVIRONMENT_RECEIPT_V8.json"),
        "input_certificate": file_digest(V8 / "P5_C3_INPUT_NATIVE_CERTIFICATE_V8.json"),
        "mutable_immutable_split": file_digest(V8 / "P5_C3_MUTABLE_IMMUTABLE_SPLIT_V8.json"),
    }
    with tempfile.TemporaryDirectory(prefix="p5-c3-v9-microgate-") as temp_text:
        adapter_output = Path(temp_text) / "adapter-result.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(ADAPTER),
                "--seed",
                str(SEED),
                "--preregistration",
                str(PREREG),
                "--output",
                str(adapter_output),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 3:
            raise RuntimeError(f"adapter did not stop fail-closed: {completed.returncode} {completed.stderr}")
        adapter_result = load(adapter_output)

    v8_hashes_after = {
        "seed": file_digest(SEED),
        "receipt": file_digest(V8 / "P5_C3_NATIVE_TASK_ENVIRONMENT_RECEIPT_V8.json"),
        "input_certificate": file_digest(V8 / "P5_C3_INPUT_NATIVE_CERTIFICATE_V8.json"),
        "mutable_immutable_split": file_digest(V8 / "P5_C3_MUTABLE_IMMUTABLE_SPLIT_V8.json"),
    }
    if v8_hashes_before != v8_hashes_after:
        raise RuntimeError("V8 predecessor mutation detected")

    core_observed = {}
    forbidden = []
    with tarfile.open(SEED, "r:gz") as archive:
        names = archive.getnames()
        forbidden = [
            name
            for name in names
            if name.startswith("candidate/dgm/initial/")
            or name.startswith("candidate/dgm/initial_polyglot/")
            or name.startswith("candidate/dgm/swe_bench/ref_agent_results/")
        ]
        for name, expected in EXPECTED_CORE.items():
            handle = archive.extractfile(name)
            if handle is None:
                raise RuntimeError(f"missing immutable core member: {name}")
            observed = digest(handle.read())
            if observed != expected:
                raise RuntimeError(f"immutable core mismatch: {name}")
            core_observed[name] = observed
    if forbidden:
        raise RuntimeError(f"excluded prior outcome prefix entered V8 seed: {forbidden}")

    if adapter_result["terminal"] != TERMINAL:
        raise RuntimeError("terminal drift")
    if adapter_result["native_semantics_preservable"] is not False:
        raise RuntimeError("native semantics verdict drift")
    if adapter_result["field_instances_closed"] != 0:
        raise RuntimeError("field closure inflation")

    receipt = {
        "schema_version": "orion.p5.c3.outcome-free-successor-microgate-receipt.v9",
        "protocol_id": "P5.C3.DGM.OUTCOME_FREE_INITIALIZATION.SUCCESSOR.V9",
        "adapter_id": "DGM_OUTCOME_FREE_INITIALIZATION_ADAPTER_V9",
        "authority": "ONE_STATIC_EXACT_BYTE_AND_AST_MICROGATE_ONLY",
        "preregistration": {
            "path": PREREG.name,
            "sha256": file_digest(PREREG),
            "frozen_before_microgate": True,
        },
        "adapter_implementation": {
            "path": ADAPTER.name,
            "sha256": file_digest(ADAPTER),
            "exit_code": 3,
            "fail_closed": True,
        },
        "predecessor_v8": {
            "packet": str(V8.relative_to(ROOT)),
            "hashes_before": v8_hashes_before,
            "hashes_after": v8_hashes_after,
            "mutated": False,
        },
        "immutable_lang1_core": {
            "member_count": len(core_observed),
            "members": core_observed,
            "mutated": False,
            "extracted_for_mutation": False,
        },
        "excluded_prior_outcome_prefixes": {
            "absent_from_seed": True,
            "forbidden_members_observed": forbidden,
            "excluded_payload_contents_opened": False,
        },
        "adapter_result": adapter_result,
        "microgates_run": 1,
        "microgate_type": "STATIC_EXACT_BYTE_AND_AST_DATAFLOW_GATE",
        "executions": {"dgm": 0, "model": 0, "benchmark": 0, "scorer": 0, "outcomes": 0, "tests": 0},
        "verdict": "STOP_NO_LAWFUL_SEMANTICS_PRESERVING_OUTCOME_FREE_INITIALIZATION_ADAPTER",
        "field_closure_effect": {
            "field": "runtime.task_environment",
            "v8_status": "BLOCKING",
            "v9_status": "BLOCKING",
            "field_instances_closed": 0,
            "c3_blocker_delta": 0,
        },
        "scientific_boundary": {
            "native_c3_semantics_preserved_by_stopping": True,
            "prior_performance_fabricated": False,
            "native_execution_readiness": "NOT_ESTABLISHED",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
        },
        "next_discriminator": adapter_result["next_discriminator"],
        "terminal": TERMINAL,
    }
    write_json(RECEIPT, receipt)
    (HERE / "TERMINAL_V9.txt").write_text(TERMINAL + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": TERMINAL,
        "verdict": receipt["verdict"],
        "microgates_run": 1,
        "field_instances_closed": 0,
        "c3_blocker_delta": 0,
        "dgm_model_benchmark_scorer_outcome_executions": "0/0/0/0/0",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
