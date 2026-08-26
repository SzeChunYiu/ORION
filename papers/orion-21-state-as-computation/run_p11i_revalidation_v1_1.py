"""Fresh-process P11I revalidation without mutating its original result."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from orion.study.p11.wide_panel_revalidation import (
    PRECONDITION_FAILED,
    build_revalidation_receipt,
    canonical_text,
)

HERE = Path(__file__).resolve().parent
FROZEN_RUNNER = HERE / "run_p11i_wide_high_width_replication_v1.py"
OUT = HERE / "P11I_REVALIDATION_RECEIPT_V1_1.json"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="p11i-revalidation-") as directory:
        outputs = [Path(directory) / "a.json", Path(directory) / "b.json"]
        runs = [
            subprocess.run(
                [sys.executable, str(FROZEN_RUNNER), "--once", str(output)],
                cwd=HERE.parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            for output in outputs
        ]
        if not all(run.returncode == 0 for run in runs):
            raise RuntimeError("P11I frozen replay worker failed")
        raw = [output.read_bytes() for output in outputs]
        identical = raw[0] == raw[1]
        digest = sha256(raw[0]).hexdigest()
        receipt = build_revalidation_receipt(
            json.loads(raw[0]), replay_sha256=digest, byte_identical=identical
        )
        OUT.write_text(canonical_text(receipt), encoding="utf-8")
        print(json.dumps(receipt["adjudication"], indent=2, sort_keys=True))
        if receipt["adjudication"]["terminal"] == PRECONDITION_FAILED:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
