#!/usr/bin/env python3
"""Run the exact RSE formal-mechanics closure and emit a content-addressable JSON result."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CORE = HERE / "formal_verification_core.py"


def _load_core():
    spec = importlib.util.spec_from_file_location("rse_formal_verification_core_runner", CORE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    core = _load_core()
    result = core.build_closure_report()
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    envelope = {
        "result": result,
        "result_sha256": hashlib.sha256(canonical).hexdigest(),
        "source_files": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(HERE.glob("*.py"))
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n")
    print(json.dumps(envelope, sort_keys=True))
    return 0 if result["terminal"] == "RSE_FORMAL_MECHANICS_VERIFIED_WITH_DONOR_SUBSUMPTION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
