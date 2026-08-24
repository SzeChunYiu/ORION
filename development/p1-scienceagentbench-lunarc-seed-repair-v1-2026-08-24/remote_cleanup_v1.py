#!/usr/bin/env python3
"""Remove only the frozen remote seed-repair root and emit a receipt."""

import json
import pathlib
import shutil
import subprocess
import time


ROOT = pathlib.Path(
    "/projects/hep/fs10/scratch/scyiu/orion_p1_sab_seed_repair_v1_20260824"
)


def main():
    if str(ROOT) != "/projects/hep/fs10/scratch/scyiu/orion_p1_sab_seed_repair_v1_20260824":
        raise SystemExit("cleanup root identity mismatch")
    if not ROOT.is_dir():
        raise SystemExit("cleanup root absent before cleanup")
    files = [path for path in ROOT.rglob("*") if path.is_file() or path.is_symlink()]
    file_bytes = sum(path.lstat().st_size for path in files)
    du_bytes = int(
        subprocess.check_output(["du", "-sb", str(ROOT)], text=True).split()[0]
    )
    file_count = len(files)
    shutil.rmtree(ROOT)
    receipt = {
        "schema": "orion.p1.scienceagentbench.lunarc-direct-seed-remote-cleanup.v1",
        "status": "PASS_REMOTE_ROOT_REMOVED",
        "remote_root": str(ROOT),
        "files_removed": file_count,
        "file_bytes_removed": file_bytes,
        "du_bytes_before_cleanup": du_bytes,
        "cleanup_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root_exists_after_cleanup": ROOT.exists(),
        "scientific_authority_delta": "NONE",
    }
    if receipt["root_exists_after_cleanup"]:
        raise SystemExit("remote root still exists after cleanup")
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

