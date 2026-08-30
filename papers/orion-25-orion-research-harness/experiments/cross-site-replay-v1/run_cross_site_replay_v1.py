#!/usr/bin/env python3
"""ORION25.CROSS_SITE_REPLAY.v1 driver.

Replays, on a second site, the two frozen ORION-25 result generators:
  A. top_tier/run_attestation_composition_v2.py  (chained attestation V2)
  B. experiments/trust-domain-law-v1/sweep_trust_domain_law.py (trust-domain law)
and compares their scientific endpoints against the committed references by
PARSED-OBJECT equality through one code path (no serialization ambiguity).
The attestation projection strips exactly {observed_environment,
receipt_sha256}; the sweep output is compared whole.

Custody boundary (frozen): a second site under the SAME programme custody is
portability evidence, not independent replication and not a second
custodian. scientific_authority_delta: NONE.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

FROZEN = {
    "top_tier/run_attestation_composition_v2.py": "000811c96a1204d3a2e8ffb35ca1accc8a02627135b62175683d22d36691a701",
    "top_tier/p15_real_workflow_receipts_v1.json": "87812194ad77f3cb2be19cd9dbeacb43b662bc35eb6df3b700f4521620f6d200",
    "top_tier/sei_fault_cases_v1.jsonl": "a9a29f9e457e0be3b42acf806c3fdeb3d83ef252c3a66e81316a42a12245af2c",
    "top_tier/sei_fault_gold_v1.json": "142d14d089afbad0f49fd4243b5dda252c96017456d392d9c7a3e63e2e5fd45a",
    "top_tier/P15_ATTESTATION_COMPOSITION_PROTOCOL_V2.md": "fe04e31e9883549c64ce0e6bd578d201a8e9a2d726b87fdfed9bcf90dbaa5505",
    "experiments/trust-domain-law-v1/sweep_trust_domain_law.py": "6803e76eab02d1238493e8b218aa09b94ba51e5c72453f068b51f2109457d1e6",
    "experiments/cross-site-replay-v1/reference_p15_attestation_composition_v2.json": "99b905fbf383933d011460a4554682a2cf1279f2b06bc830bdfa6e643fd6f767",
    "experiments/trust-domain-law-v1/RESULT_V1.json": None,  # compared by object, hash recorded
}
STRIP = ("observed_environment", "receipt_sha256")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_json_stdout(script: Path, cwd: Path) -> dict:
    proc = subprocess.run([sys.executable, str(script)], cwd=cwd, capture_output=True, timeout=3600)
    if proc.returncode != 0:
        raise RuntimeError(f"{script.name} exit {proc.returncode}: {proc.stderr[-300:]!r}")
    # last JSON document on stdout (runners print one indented JSON receipt)
    text = proc.stdout.decode()
    start = text.find("{")
    return json.loads(text[start:])


def project(receipt: dict) -> dict:
    return {k: v for k, v in receipt.items() if k not in STRIP}


def diff_keys(a: dict, b: dict) -> list[str]:
    keys = sorted(set(a) | set(b))
    return [k for k in keys if a.get(k) != b.get(k)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-commit", required=True)
    args = ap.parse_args()
    root = args.paper_dir.resolve()

    binding_failures = []
    for rel, want in FROZEN.items():
        p = root / rel
        if not p.is_file():
            binding_failures.append(f"MISSING {rel}")
        elif want and sha256_file(p) != want:
            binding_failures.append(f"DRIFT {rel}")
    env = {
        "utc": utc_now(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "source_commit": args.source_commit,
        "driver_sha256": sha256_file(Path(__file__)),
    }
    try:
        import cryptography  # noqa: F401

        env["cryptography"] = cryptography.__version__
    except Exception:
        binding_failures.append("MISSING cryptography")

    result: dict = {"schema": "ORION.ORION25.CrossSiteReplay.Result.v1", "environment": env}
    if binding_failures:
        result["run_terminal"] = "CANNOT_CHECK__BINDING_DRIFT"
        result["binding_failures"] = binding_failures
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        print("run_terminal=CANNOT_CHECK__BINDING_DRIFT")
        return 3

    # A. attestation composition V2
    ref = json.loads((root / "experiments/cross-site-replay-v1/reference_p15_attestation_composition_v2.json").read_text())
    local = run_json_stdout(root / "top_tier/run_attestation_composition_v2.py", root / "top_tier")
    a_diff = diff_keys(project(ref), project(local))
    result["attestation_v2"] = {
        "reference_environment": ref.get("observed_environment"),
        "replay_environment_keys": {"python": env["python"], "cryptography": env.get("cryptography"), "machine": env["machine"]},
        "projection_equal": not a_diff,
        "diverging_keys": a_diff,
        "replay_terminal_field": local.get("terminal"),
    }

    # B. trust-domain-law sweep
    ref_tdl = json.loads((root / "experiments/trust-domain-law-v1/RESULT_V1.json").read_text())
    local_tdl = run_json_stdout(root / "experiments/trust-domain-law-v1/sweep_trust_domain_law.py", root / "experiments/trust-domain-law-v1")
    b_diff = diff_keys(ref_tdl, local_tdl)
    result["trust_domain_law"] = {
        "reference_sha256": sha256_file(root / "experiments/trust-domain-law-v1/RESULT_V1.json"),
        "object_equal": not b_diff,
        "diverging_keys": b_diff,
        "replay_terminal_field": local_tdl.get("terminal"),
    }

    # Planted control: one flipped byte in the workload receipts must change
    # the attestation endpoint through the SAME comparison path.
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "paper"
        shutil.copytree(root / "top_tier", tmp / "top_tier")
        target = tmp / "top_tier/p15_real_workflow_receipts_v1.json"
        raw = bytearray(target.read_bytes())
        idx = raw.find(b'"receipts"') + 30
        raw[idx] = raw[idx] ^ 0x01
        target.write_bytes(bytes(raw))
        try:
            mutated = run_json_stdout(tmp / "top_tier/run_attestation_composition_v2.py", tmp / "top_tier")
            control_fired = bool(diff_keys(project(ref), project(mutated)))
            control_status = "FIRED_VIA_DIVERGENCE" if control_fired else "DID_NOT_FIRE"
        except Exception as exc:
            control_fired = True
            control_status = f"FIRED_VIA_RUNNER_FAILURE: {str(exc)[:120]}"
    result["planted_control"] = {"status": control_status, "fired": control_fired}

    if not control_fired:
        result["run_terminal"] = "CANNOT_CHECK__CONTROL_FAILURE"
    elif result["attestation_v2"]["projection_equal"] and result["trust_domain_law"]["object_equal"]:
        result["run_terminal"] = "T1_CROSS_SITE_ENDPOINTS_IDENTICAL"
    else:
        result["run_terminal"] = "T2_ENDPOINT_DIVERGENCE"
    result["custody_boundary"] = (
        "Second site under the same programme custody: portability evidence only; "
        "not independent replication, not a second custodian; scientific_authority_delta NONE."
    )
    result["finished_utc"] = utc_now()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(f"run_terminal={result['run_terminal']} -> {args.out}")
    return 0 if result["run_terminal"].startswith("T1") else 2


if __name__ == "__main__":
    raise SystemExit(main())
