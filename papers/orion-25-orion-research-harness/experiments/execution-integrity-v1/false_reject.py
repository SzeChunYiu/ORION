#!/usr/bin/env python3
"""ORION-25 FALSE REJECTION endpoint against the frozen ARM-K3-D1 artifact.

The false-promotion test asked: does a corrupted artifact ever pass?
This asks the opposite: does an UNCORRUPTED artifact ever fail?

A verifier that rejects semantically identical input is not "merely strict" -- it
manufactures adverse results, and a suite that cries wolf gets switched off.

Transformations below are semantics-preserving by construction: the decoded JSON
object is asserted equal to the original before each trial. Any rejection is
therefore a false rejection, not a detection.

  0 = no false rejection
  2 = false rejection observed
  3 = could not check (setup failed / baseline not green)
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CHECKER = HERE / "check_attestation_composition_independent_v2.py"
PRIMARY = HERE / "p15_attestation_composition_v2.json"
GREEN = "P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN"


def run():
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True, cwd=HERE)
    try:
        return r.returncode, json.loads(r.stdout).get("terminal", "")
    except Exception:
        return r.returncode, (GREEN if GREEN in r.stdout else "")


def main() -> int:
    if not (PRIMARY.exists() and CHECKER.exists()):
        print(json.dumps({"terminal": "CANNOT_CHECK_SETUP_INCOMPLETE"}))
        return 3
    original = PRIMARY.read_bytes()
    doc = json.loads(original)

    rc0, t0 = run()
    if t0 != GREEN:
        PRIMARY.write_bytes(original)
        print(json.dumps({"terminal": "CANNOT_CHECK_BASELINE_NOT_GREEN", "observed": t0}))
        return 3

    variants = {
        "V1_REPEAT_IDENTICAL": lambda: original,
        "V2_INDENT_2_TO_4": lambda: (json.dumps(doc, indent=4) + "\n").encode(),
        "V3_COMPACT_SEPARATORS": lambda: json.dumps(doc, separators=(",", ":")).encode(),
        "V4_KEY_ORDER_SORTED": lambda: (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode(),
        "V5_KEY_ORDER_REVERSED": lambda: (
            json.dumps({k: doc[k] for k in reversed(list(doc))}, indent=2) + "\n").encode(),
        "V6_TRAILING_NEWLINES": lambda: original.rstrip(b"\n") + b"\n\n\n",
    }

    results = []
    try:
        for name, make in variants.items():
            payload = make()
            # semantics-preserving control: refuse to score a variant that changed meaning
            if json.loads(payload) != doc:
                results.append({"variant": name, "applied": False,
                                "result": "CANNOT_CHECK_VARIANT_CHANGED_SEMANTICS"})
                continue
            PRIMARY.write_bytes(payload)
            rc, term = run()
            results.append({"variant": name, "applied": True, "checker_rc": rc,
                            "checker_terminal": term or "(none)",
                            "bytes_differ_from_original": payload != original,
                            "falsely_rejected": term != GREEN})
    finally:
        PRIMARY.write_bytes(original)

    applied = [r for r in results if r.get("applied")]
    bad = [r for r in applied if r.get("falsely_rejected")]
    print(json.dumps({
        "schema": "orion.orion25.false-rejection.v1",
        "successor_id": "ORION25.EXECUTION_INTEGRITY.v1",
        "box": "false-rejection endpoint",
        "arm": "ARM-K3-D1",
        "authority": "MEASUREMENT_ONLY",
        "scientific_authority_delta": "NONE",
        "baseline_terminal": t0,
        "variants_applied": len(applied),
        "false_rejections": len(bad),
        "false_rejection_rate": (len(bad) / len(applied)) if applied else None,
        "results": results,
        "scope": ("Semantics-preserving re-encodings of the committed result. Does NOT "
                  "cover false rejection caused by transient host conditions (clock, "
                  "filesystem, memory pressure), which needs the fault harness the "
                  "protocol still lists as absent."),
        "terminal": ("NO_FALSE_REJECTION_UNDER_SEMANTICS_PRESERVING_REENCODING"
                     if not bad else "FALSE_REJECTION_OBSERVED"),
    }, indent=2, sort_keys=True))
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
