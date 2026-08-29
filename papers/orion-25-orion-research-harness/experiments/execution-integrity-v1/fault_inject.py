#!/usr/bin/env python3
"""ORION-25 host/process fault injection against the frozen ARM-K3-D1 artifact.

Measures the FALSE PROMOTION endpoint: does the independent checker ever return
GREEN on an artifact that has been corrupted or truncated?

Faults are applied EXTERNALLY to the frozen runner and checker. Neither is
modified, so this needs none of the new code the H1/H2 arms require.

Exit codes are distinct on purpose:
  0 = every fault detected (no false promotion)
  2 = at least one fault produced a GREEN checker verdict (FALSE PROMOTION)
  3 = could not check (setup failed) -- never reported as clean
"""
import copy
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CHECKER = HERE / "check_attestation_composition_independent_v2.py"
PRIMARY = HERE / "p15_attestation_composition_v2.json"
GREEN = "P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN"


def run_checker() -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True, cwd=HERE)
    terminal = ""
    try:
        terminal = json.loads(r.stdout).get("terminal", "")
    except Exception:
        for line in r.stdout.splitlines():
            if GREEN in line:
                terminal = GREEN
    return r.returncode, terminal


def find_first(node, pred, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if pred(k, v):
                return node, k
            got = find_first(v, pred, f"{path}/{k}")
            if got:
                return got
    elif isinstance(node, list):
        for i, v in enumerate(node):
            got = find_first(v, pred, f"{path}[{i}]")
            if got:
                return got
    return None


def main() -> int:
    if not PRIMARY.exists() or not CHECKER.exists():
        print(json.dumps({"terminal": "CANNOT_CHECK_SETUP_INCOMPLETE"}))
        return 3

    original = PRIMARY.read_bytes()
    base_rc, base_terminal = run_checker()
    if base_terminal != GREEN:
        PRIMARY.write_bytes(original)
        print(json.dumps({"terminal": "CANNOT_CHECK_BASELINE_NOT_GREEN",
                          "observed": base_terminal, "rc": base_rc}))
        return 3

    doc = json.loads(original)
    faults = []

    def attempt(name, mutate, why):
        try:
            d = copy.deepcopy(doc)
            if mutate(d) is False:
                faults.append({"fault": name, "applied": False,
                               "result": "CANNOT_CHECK_FAULT_NOT_APPLICABLE", "tests": why})
                return
            mutated = json.dumps(d, indent=2, sort_keys=True) + "\n"
            if json.loads(mutated) == json.loads(original.decode()):
                faults.append({"fault": name, "applied": False,
                               "result": "CANNOT_CHECK_MUTATION_WAS_A_NO_OP", "tests": why})
                return
            PRIMARY.write_text(mutated)
            rc, term = run_checker()
            faults.append({"fault": name, "applied": True, "checker_rc": rc,
                           "checker_terminal": term or "(none)",
                           "detected": term != GREEN, "tests": why})
        finally:
            PRIMARY.write_bytes(original)

    def truncate_bytes(_d):
        PRIMARY.write_bytes(original[: len(original) // 2])
        return True

    # F1 truncated write (process killed mid-write)
    try:
        PRIMARY.write_bytes(original[: len(original) // 2])
        rc, term = run_checker()
        faults.append({"fault": "F1_TRUNCATED_WRITE", "applied": True, "checker_rc": rc,
                       "checker_terminal": term or "(none)", "detected": term != GREEN,
                       "tests": "process killed mid-write leaves a half-written result"})
    finally:
        PRIMARY.write_bytes(original)

    # F2 single-byte flip in a signature
    def flip_sig(d):
        got = find_first(d, lambda k, v: k in ("signature", "signature_hex") and isinstance(v, str) and len(v) > 4)
        if not got:
            return False
        node, key = got
        s = node[key]
        node[key] = ("0" if s[0] != "0" else "1") + s[1:]
        return True
    attempt("F2_SIGNATURE_BYTE_FLIP", flip_sig, "one flipped hex digit in a link signature")

    # F3 chain-link removal
    def drop_link(d):
        got = find_first(d, lambda k, v: isinstance(v, list) and len(v) > 1
                         and all(isinstance(x, dict) for x in v)
                         and any("payload" in x or "signature" in x for x in v))
        if not got:
            return False
        node, key = got
        node[key] = node[key][:-1]
        return True
    attempt("F3_CHAIN_LINK_DROPPED", drop_link, "an attestation link removed from the chain")

    # F4 public-key substitution
    def swap_key(d):
        got = find_first(d, lambda k, v: "public_key" in k and isinstance(v, str) and len(v) > 8)
        if not got:
            return False
        node, key = got
        s = node[key]
        node[key] = s[2:4] + s[0:2] + s[4:]
        return True
    attempt("F4_PUBLIC_KEY_SUBSTITUTION", swap_key, "a link's public key replaced")

    # F5 terminal relabel (the adverse-to-favourable rewrite)
    def relabel(d):
        # A mutation must actually change the bytes. Setting a field to the value
        # it already holds is a no-op that a naive harness scores as "undetected",
        # which is a false positive in the harness, not a finding about the system.
        if "terminal" not in d:
            return False
        current = d["terminal"]
        replacement = "P15_ATTESTATION_COMPOSITION_V2_REFUTED"
        if current == replacement:
            replacement = "P15_ATTESTATION_COMPOSITION_V2_SUPPORTED"
        if current == replacement:
            return False
        d["terminal"] = replacement
        return True
    attempt("F5_TERMINAL_RELABEL", relabel, "result relabelled favourable without redoing work")

    # F6 count inflation
    def inflate(d):
        got = find_first(d, lambda k, v: k.endswith("_count") and isinstance(v, int))
        if not got:
            return False
        node, key = got
        node[key] = node[key] + 1
        return True
    attempt("F6_COUNT_INFLATION", inflate, "a reported count incremented by one")

    applied = [f for f in faults if f.get("applied")]
    undetected = [f for f in applied if not f.get("detected")]
    out = {
        "schema": "orion.orion25.fault-injection.v1",
        "successor_id": "ORION25.EXECUTION_INTEGRITY.v1",
        "box": "production-like host/process fault injection; false-promotion endpoint",
        "arm": "ARM-K3-D1",
        "authority": "MEASUREMENT_ONLY",
        "scientific_authority_delta": "NONE",
        "baseline_terminal": base_terminal,
        "faults_attempted": len(faults),
        "faults_applied": len(applied),
        "faults_not_applicable": len(faults) - len(applied),
        "false_promotions": len(undetected),
        "false_promotion_rate": (len(undetected) / len(applied)) if applied else None,
        "results": faults,
        "scope": ("Corruption of the committed result artifact, applied externally. Does NOT "
                  "cover faults inside the runner's own execution (mid-signing kill, clock skew, "
                  "reordered messages), which need instrumentation that does not exist."),
        "terminal": ("NO_FALSE_PROMOTION_UNDER_APPLIED_FAULTS" if not undetected
                     else "FALSE_PROMOTION_OBSERVED"),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 2 if undetected else 0


if __name__ == "__main__":
    raise SystemExit(main())
