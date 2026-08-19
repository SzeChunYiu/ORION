from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.study.p9.s3_rotation_experiment import run_s3_domain_rotations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--subject-sha", required=True)
    args = parser.parse_args()
    result = run_s3_domain_rotations(subject_sha=args.subject_sha)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    compact = {"terminal": result["terminal"], "result_digest": result["result_digest"], "rotations": {}}
    for name, row in result["rotations"].items():
        compact["rotations"][name] = {
            "F1": row["f1_serialized_generic_binding"]["test"]["accuracy"],
            "F1_double": row["f1_serialized_generic_binding"]["test"]["double_corruption_accuracy"],
            "F1_unresolved": row["f1_serialized_generic_binding"]["test"]["unresolved_accuracy"],
            "F2": row["f2_serialized_exact_generic_comparator"]["accuracy"],
            "F3": row["same_run_dense_controls"]["TYPED_RELATIONAL"]["test"]["accuracy"],
            "F0_dense": row["same_run_dense_controls"]["TYPED_SERIALIZED_BAG"]["test"]["accuracy"],
        }
    print(json.dumps(compact, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
