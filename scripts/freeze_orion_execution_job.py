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
    parser.add_argument("--expected-source-git-sha")
    args = parser.parse_args()

    with args.draft.open(encoding="utf-8") as handle:
        draft = json.load(handle)
    if draft.get("execution_class") == "SCIENTIFIC_STUDY" and not args.expected_source_git_sha:
        parser.error("scientific protocol freeze requires --expected-source-git-sha")
    frozen = freeze_protocol(
        draft,
        expected_source_git_sha=args.expected_source_git_sha,
    )
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(frozen, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(
        "ORION_EXECUTION_PROTOCOL_FROZEN "
        f"job={frozen['job_id']} sha256={frozen['protocol_sha256']}"
    )


if __name__ == "__main__":
    main()
