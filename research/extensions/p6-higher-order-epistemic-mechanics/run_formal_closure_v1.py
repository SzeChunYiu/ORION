from __future__ import annotations

import json

from orion.transfer.v2.higher_order_formal_closure import (
    build_formal_closure_report,
    formal_parent_dispositions,
    run_finite_formal_closure_checks,
)


def main() -> int:
    finite = run_finite_formal_closure_checks()
    closure = build_formal_closure_report()
    payload = {
        "version": "HigherOrderFormalClosureReplay.v1",
        "finite": {**finite.unsigned(), "digest": finite.digest},
        "closure": {**closure.unsigned(), "digest": closure.digest},
        "parents": [item.unsigned() for item in formal_parent_dispositions()],
        "terminal_is_authorized_by_runner": False,
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    if not finite.all_checks_passed:
        return 2
    if closure.recommendation.value != "FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
