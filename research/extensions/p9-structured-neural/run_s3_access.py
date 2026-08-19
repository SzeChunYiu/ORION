from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.study.p9.s3_runtime import run_s3_access_attribution


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--subject-sha", required=True)
    args = parser.parse_args()

    result = run_s3_access_attribution(subject_sha=args.subject_sha)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": result["terminal"],
        "result_digest": result["result_digest"],
        "f1_accuracy": result["f1_serialized_generic_binding"]["test"]["accuracy"],
        "f1_double_corruption_accuracy": result["f1_serialized_generic_binding"]["test"]["double_corruption_accuracy"],
        "f1_unresolved_accuracy": result["f1_serialized_generic_binding"]["test"]["unresolved_accuracy"],
        "f2_accuracy": result["f2_serialized_exact_generic_comparator"]["accuracy"],
        "historical_serialized_accuracy": result["historical_controls"]["TYPED_SERIALIZED_BAG"]["test"]["accuracy"],
        "historical_typed_relational_accuracy": result["historical_controls"]["TYPED_RELATIONAL"]["test"]["accuracy"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
