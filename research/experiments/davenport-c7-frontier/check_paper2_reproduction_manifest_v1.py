#!/usr/bin/env python3
"""Validate that the Paper 2 manifest and reproduction runner agree exactly."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import run_paper2_reproduction_v1 as runner  # noqa: E402

MANIFEST_PATH = HERE / "PAPER2_REPRODUCIBILITY_MANIFEST_V1.json"
EXPECTED_CONTRACT = {
    "compiler": "g++",
    "flags": ["-std=c++17", "-O3", "-Wall", "-Wextra"],
    "assertions": "ENABLED",
    "forbidden_flags": ["-DNDEBUG"],
}


class ManifestError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def validate(data: dict[str, Any], *, check_files: bool = True) -> dict[str, int]:
    require(data.get("schema") == "ORION.PAPER2_REPRODUCIBILITY_MANIFEST_V1", "schema drift")
    require(data.get("as_of_date") == "2026-09-04", "date drift")
    require(data.get("cpp_compile_contract") == EXPECTED_CONTRACT, "compiler contract drift")
    require(data["cpp_compile_contract"]["flags"] == runner.SAFE_CXX_FLAGS, "runner flags differ from manifest")
    require(not any("NDEBUG" in flag for flag in runner.SAFE_CXX_FLAGS), "runner suppresses assertions")
    require("-DNDEBUG" in data["cpp_compile_contract"]["forbidden_flags"], "missing forbidden flag")

    python_entries = data.get("python_executables")
    cpp_entries = data.get("cpp_executables")
    authority_files = data.get("authority_files")
    require(isinstance(python_entries, list) and len(python_entries) == 12, "python executable census drift")
    require(isinstance(cpp_entries, list) and len(cpp_entries) == 2, "C++ executable census drift")
    require(isinstance(authority_files, list) and len(authority_files) == 4, "authority-file census drift")

    seen: set[str] = set()
    for group, key in ((python_entries, "path"), (cpp_entries, "source")):
        for entry in group:
            require(isinstance(entry, dict), "entry must be object")
            entry_id = entry.get("id")
            require(isinstance(entry_id, str) and entry_id and entry_id not in seen, "duplicate or missing id")
            seen.add(entry_id)
            relative = entry.get(key)
            require(isinstance(relative, str) and not relative.startswith("/"), "unsafe path")
            require(".." not in Path(relative).parts, "path traversal")
            if check_files:
                require((ROOT / relative).is_file(), f"missing executable source: {relative}")

    require("paper2_reproduction_manifest" in seen, "manifest self-check is not bound")
    require("paper2_surface_references" in seen, "surface audit is not bound")
    require("paper2_claim_ledger" in seen, "claim validator is not bound")

    if check_files:
        for relative in authority_files:
            require((ROOT / relative).is_file(), f"missing authority file: {relative}")
        runner.validate_manifest(data)

    require(data.get("claim_boundary") == {
        "exact_D3_C7": "OPEN",
        "all_prime_first_corridor_support7": "OPEN",
        "novelty_priority": "CANNOT_CHECK",
        "top_specialist_state": "DEVELOPMENT_READY",
    }, "claim boundary drift")

    return {
        "python_executables": len(python_entries),
        "cpp_executables": len(cpp_entries),
        "authority_files": len(authority_files),
        "unique_executable_ids": len(seen),
    }


def expect_rejected(mutant: dict[str, Any], label: str) -> None:
    try:
        validate(mutant, check_files=False)
    except ManifestError:
        return
    raise AssertionError(f"hostile manifest mutation accepted: {label}")


def hostile_mutations(data: dict[str, Any]) -> int:
    mutants: list[tuple[str, dict[str, Any]]] = []

    mutant = copy.deepcopy(data)
    mutant["cpp_compile_contract"]["flags"].append("-DNDEBUG")
    mutants.append(("enable NDEBUG", mutant))

    mutant = copy.deepcopy(data)
    mutant["cpp_compile_contract"]["assertions"] = "DISABLED"
    mutants.append(("disable assertions label", mutant))

    mutant = copy.deepcopy(data)
    mutant["cpp_compile_contract"]["forbidden_flags"] = []
    mutants.append(("erase forbidden flags", mutant))

    mutant = copy.deepcopy(data)
    mutant["python_executables"] = mutant["python_executables"][:-1]
    mutants.append(("drop manifest self-check", mutant))

    mutant = copy.deepcopy(data)
    mutant["python_executables"][1]["id"] = mutant["python_executables"][0]["id"]
    mutants.append(("duplicate executable id", mutant))

    mutant = copy.deepcopy(data)
    mutant["cpp_executables"] = mutant["cpp_executables"][:1]
    mutants.append(("drop independent C++ verifier", mutant))

    mutant = copy.deepcopy(data)
    mutant["authority_files"] = mutant["authority_files"][:3]
    mutants.append(("drop authority surface", mutant))

    mutant = copy.deepcopy(data)
    mutant["claim_boundary"]["exact_D3_C7"] = "PROVED"
    mutants.append(("promote exact D3", mutant))

    for label, mutant in mutants:
        expect_rejected(mutant, label)
    return len(mutants)


def main() -> None:
    raw = MANIFEST_PATH.read_bytes()
    data = json.loads(raw)
    require(isinstance(data, dict), "manifest root must be object")
    counts = validate(data)
    rejected = hostile_mutations(data)
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    print(json.dumps({
        "status": "PAPER2_REPRODUCTION_MANIFEST_GREEN",
        "counts": counts,
        "hostile_mutations_rejected": rejected,
        "manifest_bytes_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_json_sha256": hashlib.sha256(canonical).hexdigest(),
        "assertions_enabled": True,
        "authority": "reproduction-governance check only",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
