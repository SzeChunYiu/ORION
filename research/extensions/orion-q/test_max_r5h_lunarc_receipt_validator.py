#!/usr/bin/env python3
"""Selftest for max_r5h_lunarc_receipt_validator.py.

The validator's SUBJECT payload branch was written before any real receipt
existed and would have rejected the actual SubjectFast.v1 result shape (it
read result as arms->variants while the real result carries scalar provenance,
stats leaves, frontier sizes and window-meta lists at that level). This
selftest pins the corrected shape against the REAL frozen H4 receipt values
(from the orion-q-max-r5h CI run on merged head tierb/o6r4c-ns1,
run 33757745298, 2026-09-03) so the branch can never silently drift again.

Cases: a valid real-shaped envelope VALIDATES; an empty directory reports
PENDING; each corruption (budget-hit wall, zero CNOT, short partition hash,
wrong subject, missing B0, empty named variants, duplicate legs, bad envelope
schema, non-positive frontier size) is INVALID with exit 2. A no-alarm case
(valid receipt) is asserted alongside every alarm case -- a checker that
cries wolf on its first real receipt gets switched off.

Standalone: python3 test_max_r5h_lunarc_receipt_validator.py
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import max_r5h_lunarc_receipt_validator as v  # noqa: E402

# Real frozen CI values (SubjectFast.v1, subject H4, merged-head run above).
H0 = "281ea2e2add5cbfa37143b288c0b51c2cb667baeb0d134eb47ef3ad245f5d3be"
H1 = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
H2 = "ead1365263ba4ba0e288be7f3715125f4d0a4fb5a14b7979f97c7237792ad1fc"
HFT = "21eab856d7c61130e71cf0ff6e36cd2d400463606e866ad8305fe6f002da09bd"
HL = "2ae612568459ad86c34aa110a19d0a09d2bc7702c2c70b8cfe84a5c0927e7896"


def _leaf(cnot: int, part: str, lam: float, blocks: int) -> dict:
    return {"CNOT": cnot, "Lambda": lam, "block_internal_T": 0, "blocks": blocks,
            "ancilla": 0, "histogram": {}, "partition_sha256": part}


def real_h4_payload() -> dict:
    named = {"P_BALANCED": _leaf(1428, H2, 4.862157873932594, 246),
             "P_CNOT": _leaf(1428, H2, 4.862157873932594, 246),
             "P_FT": _leaf(1452, HFT, 4.862, 240),
             "P_LAMBDA": _leaf(2784, HL, 5.15, 268)}
    return {
        "schema": "ORIONQ.MAXR5H.SubjectFast.v1",
        "authority": "DEVELOPMENT_ONLY__FROZEN_R5H_SEMANTICS",
        "subject": "H4",
        "result": {
            "subject": "H4", "source_blob": "b98792b1055d" + "0" * 52,
            "n_qubits": 8, "terms": 268, "max_imag": 6.938893903907228e-18,
            "B0_Pauli_LCU": _leaf(1160, H0, 5.158046205600001, 268),
            "B1_R5G_pair_reference": _leaf(4198, H1, 4.862865511405695, 134),
            "donor_direct_frontier_size": 4249, "mixed_frontier_size": 5150,
            "donor_window_meta": [{"start": 0, "size": 12, "frontier": 1,
                                   "global_frontier_after": 1}],
            "mixed_window_meta": [{"start": 0, "size": 12, "frontier": 25,
                                   "global_frontier_after": 25}],
            "B2_donor_named": named, "B3_mixed_named": dict(named),
            "mixed_balanced_uses_TARE": False,
            "mixed_balanced_distinct_from_all_donor_resources": False,
            "r5h_subject_development_pass": False,
        },
        "chunked": {"instrument": "max_r5h_subject_chunked.py",
                    "checkpoint_schema": "ORIONQ.MAXR5H.SubjectChunk.V1"},
    }


def envelope(payload: dict, wall: int = 130, timeout: int = 1200) -> dict:
    return {"schema": "ORIONQ.MAXR5H.LunarcReceipt.V1", "leg": "SUBJECT:H4",
            "exec_host": "lunarc-cosmos slurm (n12)", "slurm_job_id": "3572284",
            "wall_seconds": wall, "timeout_seconds": timeout,
            "completed_utc": "2026-09-03T18:40:00Z",
            "log_sha256": "0" * 64, "payload": payload}


def run_dir(docs: list[dict]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        for i, doc in enumerate(docs):
            (tdir / f"MAX_R5H_LUNARC_RECEIPT_T{i}.json").write_text(
                json.dumps(doc, sort_keys=True))
        import io
        from contextlib import redirect_stdout, redirect_stderr
        buf_out, buf_err = io.StringIO(), io.StringIO()
        import os
        code = -1
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            try:
                code = v.run(tdir)
            except SystemExit as e:  # _fail paths raise SystemExit in older shape
                code = int(e.code or 0)
        del os
        return code, buf_out.getvalue() + buf_err.getvalue()


def main() -> int:
    cases: list[tuple[str, callable, tuple[int, str]]] = []

    def case(name, fn, expect_code, expect_marker):
        cases.append((name, fn, (expect_code, expect_marker)))

    base = envelope(real_h4_payload())
    case("valid real-shaped H4 receipt", lambda: [base], 0, "VALIDATED")
    case("no receipts -> PENDING", lambda: [], 0, "PENDING")

    def budget_hit():
        d = envelope(real_h4_payload(), wall=1200, timeout=1200)
        return [d]
    case("wall>=timeout budget-hit is not a receipt", budget_hit, 2, "INVALID")

    def zero_cnot():
        d = copy.deepcopy(base)
        d["payload"]["result"]["B3_mixed_named"]["P_FT"]["CNOT"] = 0
        return [d]
    case("zero CNOT in a named variant", zero_cnot, 2, "INVALID")

    def short_hash():
        d = copy.deepcopy(base)
        d["payload"]["result"]["B0_Pauli_LCU"]["partition_sha256"] = "abc"
        return [d]
    case("non-64-hex partition_sha256", short_hash, 2, "INVALID")

    def wrong_subject():
        d = copy.deepcopy(base)
        d["payload"]["subject"] = "N2"
        return [d]
    case("payload subject mismatch with leg", wrong_subject, 2, "INVALID")

    def missing_b0():
        d = copy.deepcopy(base)
        del d["payload"]["result"]["B0_Pauli_LCU"]
        return [d]
    case("missing B0_Pauli_LCU", missing_b0, 2, "INVALID")

    def empty_named():
        d = copy.deepcopy(base)
        d["payload"]["result"]["B2_donor_named"] = {}
        return [d]
    case("empty B2_donor_named", empty_named, 2, "INVALID")

    def none_variant():
        d = copy.deepcopy(base)
        d["payload"]["result"]["B3_mixed_named"]["P_LAMBDA"] = None
        return [d]
    case("None named variant is legal", none_variant, 0, "VALIDATED")

    def dup_legs():
        return [copy.deepcopy(base), copy.deepcopy(base)]
    case("duplicate leg receipts", dup_legs, 2, "INVALID")

    def bad_schema():
        d = copy.deepcopy(base)
        d["schema"] = "SOMETHING.ELSE.V1"
        return [d]
    case("wrong envelope schema", bad_schema, 2, "INVALID")

    def zero_frontier():
        d = copy.deepcopy(base)
        d["payload"]["result"]["mixed_frontier_size"] = 0
        return [d]
    case("non-positive frontier size", zero_frontier, 2, "INVALID")

    failures = []
    for name, fn, (expect_code, expect_marker) in cases:
        code, out = run_dir(fn())
        if code != expect_code or expect_marker not in out:
            failures.append(f"{name}: expected ({expect_code}, {expect_marker}) "
                            f"got ({code}, {out.strip()[:100]!r})")
    for f in failures:
        print(f"SELFTEST-FAIL {f}", file=sys.stderr)
    print(f"ORIONQ_R5H_VALIDATOR_SELFTEST={'PASS' if not failures else 'FAIL'} "
          f"n_cases={len(cases)} failures={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
