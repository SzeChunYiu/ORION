from __future__ import annotations

import json
import sys
from research.claim_expansion.p3.generate_p3_x_dev_cases import generate


def main() -> int:
    cases = generate(n_variants=10, authority="PROTECTED_V1")
    json.dump({
        "authority":"PROTECTED_V1",
        "case_count":len(cases),
        "cases":cases,
    }, sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
