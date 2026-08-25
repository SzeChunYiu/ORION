#!/usr/bin/env python3
"""Bind a frozen ORION execution protocol to a SLURM script."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from orion.discovery.execution_takeover import (
    render_slurm_script,
    submission_key,
    validate_frozen_protocol,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("protocol", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--account", required=True)
    parser.add_argument("--partition", required=True)
    parser.add_argument("--stdout", required=True)
    parser.add_argument("--stderr", required=True)
    try:
        separator = sys.argv.index("--")
    except ValueError:
        parser.error("an argv command must follow --")
    args = parser.parse_args(sys.argv[1:separator])
    command = sys.argv[separator + 1 :]
    with args.protocol.open(encoding="utf-8") as handle:
        frozen = json.load(handle)
    validate_frozen_protocol(frozen)
    script = render_slurm_script(
        frozen,
        account=args.account,
        partition=args.partition,
        command=command,
        stdout_path=args.stdout,
        stderr_path=args.stderr,
    )
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(script)
    print(
        "ORION_SLURM_PACKAGE_BOUND "
        f"job={frozen['job_id']} submission_key={submission_key(frozen)} "
        f"script_sha256={hashlib.sha256(script.encode('utf-8')).hexdigest()}"
    )


if __name__ == "__main__":
    main()
