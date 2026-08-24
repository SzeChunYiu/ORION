#!/usr/bin/env python3
"""Decode the frozen V20 direct-IRI surface once, then invoke frozen scoring."""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PROTOCOL_V21.json"
PREFLIGHT = ROOT / "RUNTIME_PREFLIGHT_V21.json"
LOCK = ROOT / "ATTEMPT_LOCK_V21.json"
RESULT = ROOT / "BERTMAP_RESULT_V21.json"
TERMINAL = ROOT / "TERMINAL_V21.txt"
PARSER_RECEIPT = ROOT / "PARSER_RECEIPT_V21.json"
PARSER_STDOUT = ROOT / "PARSER_STDOUT_V21.log"
PARSER_STDERR = ROOT / "PARSER_STDERR_V21.log"
PYTHON = Path("/Volumes/P3V17_RUNTIME/venv/bin/python")
NATIVE = ROOT / "frozen-native-interface"
DECODED = ROOT / "decoded-interface"
REQUIRED = (
    "raw_mappings.json",
    "raw_mappings.tsv",
    "extended_mappings.tsv",
    "filtered_mappings.tsv",
    "repaired_mappings.tsv",
)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def regular(path: Path) -> bool:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return False
    return stat.S_ISREG(mode) and not path.is_symlink()


def main() -> int:
    stale = [PREFLIGHT, LOCK, RESULT, TERMINAL, PARSER_RECEIPT, PARSER_STDOUT, PARSER_STDERR]
    if any(path.exists() for path in stale) or any(DECODED.iterdir()):
        raise SystemExit("REFUSE_RERUN_OR_STALE_V21_ARTIFACT")
    protocol = json.loads(PROTOCOL.read_text())
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    for name, expected in protocol["frozen_code"].items():
        check(f"code_{name}", regular(ROOT / name) and sha256(ROOT / name) == expected)
    for name, spec in protocol["frozen_inputs"].items():
        path = Path(spec["path"])
        check(
            f"input_{name}",
            regular(path) and path.stat().st_size == spec["bytes"] and sha256(path) == spec["sha256"],
            str(path),
        )
    v20 = json.loads(Path(protocol["frozen_inputs"]["v20_native_result"]["path"]).read_text())
    check("v20_native_success", v20.get("native_success") is True)
    check("v20_typed_failure_preserved", v20.get("typed_decoder_pass") is False)
    check("v20_scoring_not_authorized", v20.get("common_scoring_authorized") is False)
    check("v20_reference_unopened", v20.get("reference_semantically_opened") is False)
    check("decoder_grammar_frozen", protocol["typed_decoder"]["anchored_regex"] == r"\A[A-Za-z][A-Za-z0-9+.-]*:[^()\s]+\Z")
    authorized = all(item["pass"] for item in checks)
    preflight = {
        "schema_version": "orion.p3.direct-iri-decoder.preflight.v21",
        "evaluated_at_utc": now(),
        "protocol_sha256": sha256(PROTOCOL),
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "decoder_authorized": authorized,
        "terminal": "P3_V21_FROZEN_V20_OUTPUT_AND_DIRECT_IRI_DECODER_PREFLIGHT_PASS" if authorized else "P3_V21_PREFLIGHT_FAIL",
    }
    PREFLIGHT.write_text(json.dumps(preflight, indent=2, sort_keys=True) + "\n")
    if not authorized:
        TERMINAL.write_text(preflight["terminal"] + "\n")
        return 1

    started = now()
    LOCK.write_text(
        json.dumps(
            {
                "schema_version": "orion.p3.direct-iri-decoder.attempt-lock.v21",
                "protocol_sha256": sha256(PROTOCOL),
                "preflight_sha256": sha256(PREFLIGHT),
                "started_at_utc": started,
                "attempts": 1,
                "retries": 0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    universe = json.loads((ROOT / "UNIVERSE_MANIFEST_V21.json").read_text())
    role_sets = {
        "source": set(universe["expected_source_iris"]),
        "target": set(universe["expected_target_iris"]),
    }
    grammar = re.compile(protocol["typed_decoder"]["anchored_regex"])
    error: str | None = None
    decoder: dict[str, object]
    try:
        with (NATIVE / "repaired_mappings.tsv").open(newline="") as handle:
            rows = list(csv.reader(handle, delimiter="\t", strict=True))
        if not rows or rows[0] != ["SrcEntity", "TgtEntity", "Score"] or any(len(row) != 3 for row in rows[1:]):
            raise ValueError("frozen V20 repaired table shape mismatch")
        source_values: list[str] = []
        target_values: list[str] = []
        for source, target, _score in rows[1:]:
            if grammar.fullmatch(source) is None or source not in role_sets["source"]:
                raise ValueError("source value violates frozen direct-IRI grammar or role universe")
            if grammar.fullmatch(target) is None or target not in role_sets["target"]:
                raise ValueError("target value violates frozen direct-IRI grammar or role universe")
            source_values.append(source)
            target_values.append(target)
        if len(source_values) != len(set(source_values)) or len(target_values) != len(set(target_values)):
            raise ValueError("direct-IRI surface is not injective on observed role values")

        for name in REQUIRED:
            shutil.copyfile(NATIVE / name, DECODED / name)
        parser_command = [
            str(PYTHON),
            str(ROOT / "bertmap_native_parser_v7.py"),
            "--output-dir",
            str(DECODED),
            "--manifest",
            str(ROOT / "UNIVERSE_MANIFEST_V21.json"),
            "--write-receipt",
            str(PARSER_RECEIPT),
        ]
        parser = subprocess.run(parser_command, cwd=ROOT, capture_output=True, timeout=120, check=False)
        PARSER_STDOUT.write_bytes(parser.stdout)
        PARSER_STDERR.write_bytes(parser.stderr)
        parser_receipt = json.loads(PARSER_RECEIPT.read_text()) if PARSER_RECEIPT.is_file() else {}
        parser_pass = parser.returncode == 0 and parser_receipt.get("terminal") == "STRUCTURAL_NATIVE_ARTIFACT_CONTRACT_PASS"
        decoded_path = DECODED / "repaired_mappings.tsv"
        decoder = {
            "pass": parser_pass,
            "grammar": protocol["typed_decoder"]["anchored_regex"],
            "input_rows": len(rows) - 1,
            "decoded_rows": len(rows) - 1,
            "identity_transform": True,
            "exact_source_members": len(source_values),
            "exact_target_members": len(target_values),
            "source_injective": True,
            "target_injective": True,
            "parser": {"command": parser_command, "exit_code": parser.returncode, "receipt": parser_receipt},
            "decoded_repaired": {
                "path": str(decoded_path),
                "bytes": decoded_path.stat().st_size,
                "sha256": sha256(decoded_path),
            },
        }
        if not parser_pass:
            error = "frozen structural parser rejected direct-IRI interface"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        decoder = {"pass": False, "error": error}

    passed = bool(decoder.get("pass")) and error is None
    terminal = (
        "P3_V21_DIRECT_IRI_TYPED_DECODER_PASS__FROZEN_V20_NATIVE_OUTPUT_SAME_UNIVERSE__COMMON_REFERENCE_SCORING_AUTHORIZED"
        if passed
        else "P3_V21_DIRECT_IRI_TYPED_DECODER_FAIL__COMMON_SCORING_NOT_AUTHORIZED"
    )
    result = {
        "schema_version": "orion.p3.direct-iri-decoder.result.v21",
        "protocol_id": protocol["protocol_id"],
        "authority": "FROZEN_V20_NATIVE_OUTPUT_DIRECT_IRI_INTERFACE_CONFORMANCE_ONLY_BEFORE_COMMON_SCORING",
        "started_at_utc": started,
        "finished_at_utc": now(),
        "attempts": 1,
        "retries": 0,
        "native_success": True,
        "native_output_source": protocol["frozen_inputs"]["v20_native_result"],
        "typed_decoder": decoder,
        "typed_decoder_pass": passed,
        "decoded_repaired_artifact": decoder.get("decoded_repaired"),
        "reference_semantically_opened": False,
        "common_scoring_authorized": passed,
        "claim_boundary": protocol["claim_boundary"],
        "terminal": terminal,
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    TERMINAL.write_text(terminal + "\n")
    print(terminal)
    if not passed:
        return 1

    evaluator = subprocess.run(
        [str(PYTHON), str(ROOT / "common_pair_evaluator_v21.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    (ROOT / "COMMON_SCORING_STDOUT_V21.log").write_text(evaluator.stdout)
    (ROOT / "COMMON_SCORING_STDERR_V21.log").write_text(evaluator.stderr)
    if evaluator.returncode != 0:
        print(evaluator.stderr, end="")
        return evaluator.returncode
    print(evaluator.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
