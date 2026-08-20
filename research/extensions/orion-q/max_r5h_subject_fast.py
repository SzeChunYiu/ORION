#!/usr/bin/env python3
"""Parallel subject runner for frozen MAX-R5H semantics."""
from __future__ import annotations

import json
import sys

import max_r5h_mixed_cardinality_development as b
import max_r5h_mixed_cardinality_development_fast as accel


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in b.SUBJECTS:
        raise SystemExit("usage: max_r5h_subject_fast.py H4|N2")
    b.prune = accel.fast_prune
    b.combine_frontiers = accel.fast_combine_frontiers
    name = sys.argv[1]
    result = b.run_subject(name, b.SUBJECTS[name])
    out = {
        "schema": "ORIONQ.MAXR5H.SubjectFast.v1",
        "authority": "DEVELOPMENT_ONLY__FROZEN_R5H_SEMANTICS",
        "subject": name,
        "result": result,
    }
    print("ORIONQ_MAX_R5H_SUBJECT=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
