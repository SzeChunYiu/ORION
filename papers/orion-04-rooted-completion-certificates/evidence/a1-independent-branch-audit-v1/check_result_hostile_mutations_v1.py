#!/usr/bin/env python3
"""A1 hostile result mutations against the committed global result verifier.

This does not re-run the D4 search.  It copies the already committed verifier and
its bound inputs into a temporary shadow packet and proves that two forged-result
classes fail closed:

1. a forged top-level result digest; and
2. a semantically forged nonzero survivor whose stdout/hash/top-level digest are
   all made internally self-consistent, so rejection must come from the zero-
   survivor semantic check rather than from a checksum mismatch.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
SOURCE = PAPER / "evidence" / "global-obstruction-v1"
CHECKER = SOURCE / "independent_checker" / "check_result.py"
SOURCES = [
    "engine_high_u128.c",
    "engine_high_avx.c",
    "engine_rank3_u128.c",
    "engine_rank3_avx.c",
    "engine_c4rank2_u128.c",
    "engine_c4rank2_avx.c",
]


def canon(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def shadow_packet(root: Path) -> Path:
    packet = root / "global-obstruction-v1"
    (packet / "independent_checker").mkdir(parents=True)
    shutil.copy2(CHECKER, packet / "independent_checker" / "check_result.py")
    shutil.copy2(SOURCE / "RESULT.json", packet / "RESULT.json")
    shutil.copy2(SOURCE / "FULL_CUBE_COVER.json", packet / "FULL_CUBE_COVER.json")
    for name in SOURCES:
        shutil.copy2(SOURCE / name, packet / name)
    return packet


def run_checker(packet: Path) -> tuple[int, dict]:
    out = packet / "HOSTILE_GENERIC_RESULT.json"
    proc = subprocess.run(
        ["python", str(packet / "independent_checker" / "check_result.py"),
         "--output", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    result = json.loads(out.read_text(encoding="utf-8"))
    return proc.returncode, result


def forge_digest(packet: Path) -> None:
    path = packet / "RESULT.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    result["result_digest"] = "0" * 64
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def forge_nonzero_survivor_with_valid_digest(packet: Path) -> None:
    path = packet / "RESULT.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    key = result["runs"][0]["key"]
    changed = 0
    for row in result["runs"]:
        if row["key"] != key:
            continue
        row["solutions"] = 1
        row["stdout"] = row["stdout"].replace("solutions=0", "solutions=1")
        row["stdout_sha256"] = sha256(row["stdout"].encode())
        changed += 1
    assert changed == 2, f"expected the u128/avx pair for {key}, got {changed}"
    unsigned = dict(result)
    unsigned.pop("result_digest", None)
    result["result_digest"] = sha256(canon(unsigned))
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    observations: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix="orion04-a1-hostile-") as td:
        base = Path(td)

        packet = shadow_packet(base / "digest")
        forge_digest(packet)
        code, result = run_checker(packet)
        observations["forged_result_digest"] = {
            "returncode": code,
            "decision": result["decision"],
            "result_digest_check": result["checks"]["result_digest"],
            "rejected": code != 0 and result["decision"] == "REJECT_ORION04_GLOBAL_RESULT",
        }

        packet = shadow_packet(base / "semantic")
        forge_nonzero_survivor_with_valid_digest(packet)
        code, result = run_checker(packet)
        observations["forged_nonzero_survivor_with_valid_digest"] = {
            "returncode": code,
            "decision": result["decision"],
            "result_digest_check": result["checks"]["result_digest"],
            "all_zero_check": result["checks"]["all_zero"],
            "rejected_semantically": (
                code != 0
                and result["decision"] == "REJECT_ORION04_GLOBAL_RESULT"
                and result["checks"]["result_digest"] is True
                and result["checks"]["all_zero"] is False
            ),
        }

    ok = all(
        row.get("rejected", row.get("rejected_semantically", False))
        for row in observations.values()
    )
    print(json.dumps({"all_hostile_mutations_rejected": ok, "observations": observations},
                     indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
