"""Revalidate P12B twice in the prospectively fixed locked environment."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from orion.study.p12.equal_action_successor_v1_1 import (
    NOT_SUPPORTED,
    adjudicate,
    build_core,
    canonical_text,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1_1.json"


def _worker(path: Path) -> None:
    path.write_text(canonical_text(build_core()), encoding="utf-8")


def _supervise(path: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="p12b-v1-1-replay-") as directory:
        outputs = [Path(directory) / "a.json", Path(directory) / "b.json"]
        runs = [
            subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "--worker", str(output)],
                cwd=HERE.parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            for output in outputs
        ]
        if not all(run.returncode == 0 for run in runs):
            raise RuntimeError("P12B V1.1 protected worker failed")
        raw = [output.read_bytes() for output in outputs]
        digests = [sha256(item).hexdigest() for item in raw]
        byte_identical = raw[0] == raw[1]
        result = adjudicate(json.loads(raw[0]), byte_identical_replay=byte_identical)
        result["replay"] = {
            "fresh_python_subprocesses": 2,
            "byte_identical": byte_identical,
            "first_core_sha256": digests[0],
            "second_core_sha256": digests[1],
        }
        path.write_text(canonical_text(result), encoding="utf-8")
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.worker:
        _worker(args.worker)
        return
    result = _supervise(args.out)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "summary": result["summary"],
                "gates": result["gates"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result["terminal"] == NOT_SUPPORTED:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

