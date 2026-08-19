#!/usr/bin/env python3
"""Execute the prospectively frozen P9 S3 corrective attribution study."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from orion.study.p9.s3_result import run_s3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--subject-sha", default=os.environ.get("GITHUB_SHA"))
    args = parser.parse_args()

    result = run_s3(subject_sha=args.subject_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print("P9_S3_TERMINAL=" + str(result["terminal"]))
    print("P9_S3_RESULT_DIGEST=" + str(result["result_digest"]))
    print("P9_S3_DATASET_DIGEST=" + str(result["dataset_manifest_digest"]))
    print("P9_S3_F1_MODEL=" + str(result["selected_F1_model"]["config_id"]))
    print("P9_S3_F1_ACCURACY=" + str(result["F1_test"]["accuracy"]))
    print("P9_S3_F1_DOUBLE=" + str(result["F1_test"]["double_corruption_accuracy"]))
    print("P9_S3_F1_UNRESOLVED=" + str(result["F1_test"]["unresolved_accuracy"]))
    print("P9_S3_F2_ACCURACY=" + str(result["F2_test"]["accuracy"]))
    print("P9_S3_GAP_RECOVERED=" + str(result["gap_recovered"]))
    print("P9_S3_RESIDUAL_TO_TYPED=" + str(result["residual_to_typed_relational"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
