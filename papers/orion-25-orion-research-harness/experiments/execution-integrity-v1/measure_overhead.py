#!/usr/bin/env python3
"""ORION-25 ARM-NOATT overhead baseline.

The registered overhead endpoint needs a no-attestation baseline, which PROTOCOL.json
records as absent. This supplies it WITHOUT modifying any frozen byte: it imports the
frozen runner and reuses its own facts_for/canonical/link_digest, so the attested and
un-attested arms differ in exactly one thing -- Ed25519 key derivation and signing.

Reimplementing the composition instead would risk measuring my reimplementation.

  0 = measured
  3 = could not check (frozen runner not importable / arms disagree on payloads)
"""
import hashlib
import importlib.util
import json
import pathlib
import statistics
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
RUNNER = HERE / "run_attestation_composition_v2.py"
REPEATS = 40


def load_runner():
    spec = importlib.util.spec_from_file_location("frozen_runner", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["frozen_runner"] = mod
    spec.loader.exec_module(mod)
    return mod


def compose_noatt(M, cid, e):
    """ARM-NOATT: identical chain construction, no key derivation and no signing.

    Reuses the frozen runner's facts_for / canonical, so payload bytes are identical to
    the attested arm by construction.
    """
    running, links = M.GENESIS, []
    for role in M.ROLES:
        payload = {"role": role, "previous_digest": running, "facts": M.facts_for(role, cid, e)}
        link = {"payload": payload}
        links.append(link)
        running = hashlib.sha256(M.canonical({"payload": payload})).hexdigest()
    return links


def main() -> int:
    if not RUNNER.exists():
        print(json.dumps({"terminal": "CANNOT_CHECK_RUNNER_ABSENT"})); return 3
    M = load_runner()
    real = json.loads((HERE / "p15_real_workflow_receipts_v1.json").read_text())["receipts"]
    cases = []
    for c in real:
        try:
            e, _sci = M.norm_real(c)
            cases.append((c["id"], e))
        except Exception:
            continue
    if not cases:
        print(json.dumps({"terminal": "CANNOT_CHECK_NO_USABLE_CASES"})); return 3

    # Control, corrected. Full payloads CANNOT match: compose() sets
    # running = link_digest(link), which hashes the signature and public key into the
    # chain, so previous_digest necessarily differs from link 2 onward. That is a
    # structural property of the design, not a defect -- there is no such thing as
    # "the same chain without signatures". The invariant that MUST hold is that both
    # arms attest the same FACTS over the same roles.
    for cid, e in cases:
        a = [(l["payload"]["role"], l["payload"]["facts"]) for l in M.compose(cid, e)]
        b = [(l["payload"]["role"], l["payload"]["facts"]) for l in compose_noatt(M, cid, e)]
        if a != b:
            print(json.dumps({"terminal": "CANNOT_CHECK_ARMS_DISAGREE_ON_FACTS",
                              "case": cid})); return 3

    def bench(fn):
        ts = []
        for _ in range(REPEATS):
            t0 = time.perf_counter()
            for cid, e in cases:
                fn(cid, e)
            ts.append(time.perf_counter() - t0)
        return ts

    att = bench(lambda cid, e: M.compose(cid, e))
    noatt = bench(lambda cid, e: compose_noatt(M, cid, e))

    a_med, n_med = statistics.median(att), statistics.median(noatt)
    att_bytes = sum(len(M.canonical(l)) for cid, e in cases for l in M.compose(cid, e))
    noatt_bytes = sum(len(M.canonical(l)) for cid, e in cases for l in compose_noatt(M, cid, e))

    print(json.dumps({
        "schema": "orion.orion25.overhead.v1",
        "successor_id": "ORION25.EXECUTION_INTEGRITY.v1",
        "box": "measure overhead",
        "authority": "MEASUREMENT_ONLY",
        "scientific_authority_delta": "NONE",
        "method": ("ARM-NOATT reuses the frozen runner's facts_for/canonical, so the two "
                   "arms differ only in Ed25519 key derivation and signing. Per-role "
                   "FACTS equality is asserted per case before timing."),
        "structural_note": ("Full payload equality is impossible by design: compose() "
                            "sets running = link_digest(link), which hashes the signature "
                            "and public key into the chain, so previous_digest differs "
                            "from link 2 onward. There is no 'same chain without "
                            "signatures'. The overhead below is therefore the cost of "
                            "attesting the same facts, not of appending signatures to an "
                            "otherwise identical structure."),
        "cases": len(cases), "roles_per_case": len(M.ROLES), "repeats": REPEATS,
        "attested_seconds": {"median": a_med, "min": min(att), "max": max(att)},
        "no_attestation_seconds": {"median": n_med, "min": min(noatt), "max": max(noatt)},
        "overhead_seconds_median": a_med - n_med,
        "overhead_multiple": (a_med / n_med) if n_med else None,
        "per_link_overhead_microseconds": ((a_med - n_med) / (len(cases) * len(M.ROLES))) * 1e6,
        "bytes": {"attested": att_bytes, "no_attestation": noatt_bytes,
                  "expansion_multiple": att_bytes / noatt_bytes if noatt_bytes else None},
        "scope": ("Composition-side cost only. Excludes verification, I/O and the "
                  "orchestration around the runner."),
        "terminal": "OVERHEAD_MEASURED",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
