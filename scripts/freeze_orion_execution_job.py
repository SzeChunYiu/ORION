#!/usr/bin/env python3
"""Freeze one outcome-unopened ORION execution protocol."""

import argparse
import json
from pathlib import Path

from orion.discovery.execution_takeover import freeze_protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with args.draft.open(encoding="utf-8") as handle:
        draft = json.load(handle)
    frozen = freeze_protocol(draft)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(frozen, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(
        "ORION_EXECUTION_PROTOCOL_FROZEN "
        f"job={frozen['job_id']} sha256={frozen['protocol_sha256']}"
    )


if __name__ == "__main__":
    main()

