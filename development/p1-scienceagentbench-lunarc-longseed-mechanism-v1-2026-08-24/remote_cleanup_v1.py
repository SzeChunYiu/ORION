#!/usr/bin/env python3
"""Remove only the frozen remote long-seed mechanism root."""

import json
import pathlib
import shutil
import subprocess
import time


ROOT = pathlib.Path(
    "/projects/hep/fs10/scratch/scyiu/orion_p1_sab_longseed_mechanism_v1_20260824"
)


def main():
    expected = "/projects/hep/fs10/scratch/scyiu/orion_p1_sab_longseed_mechanism_v1_20260824"
    if str(ROOT) != expected or not ROOT.is_dir():
        raise SystemExit("cleanup root identity/precondition mismatch")
    files = [path for path in ROOT.rglob("*") if path.is_file() or path.is_symlink()]
    file_bytes = sum(path.lstat().st_size for path in files)
    du_bytes = int(
        subprocess.check_output(["du", "-sb", str(ROOT)], text=True).split()[0]
    )
    shutil.rmtree(ROOT)
    receipt = {
        "schema": "orion.p1.scienceagentbench.longseed-mechanism-cleanup.v1",
        "status": "PASS_REMOTE_ROOT_REMOVED",
        "remote_root": str(ROOT),
        "files_removed": len(files),
        "file_bytes_removed": file_bytes,
        "du_bytes_before_cleanup": du_bytes,
        "cleanup_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root_exists_after_cleanup": ROOT.exists(),
        "scientific_authority_delta": "NONE",
    }
    if receipt["root_exists_after_cleanup"]:
        raise SystemExit("remote root remains")
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
