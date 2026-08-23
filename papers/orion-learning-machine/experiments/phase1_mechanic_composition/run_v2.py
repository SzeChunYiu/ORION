#!/usr/bin/env python3
"""Corrected Phase-1 reporting wrapper.

The delivered V1 runner writes ``false_commit=0.0`` for every policy without a
commit event or a prospective false-commit definition.  That value is not a
measurement.  V2 preserves the delivered experiment and random stream exactly,
but replaces the constant with an explicit ``NOT_MEASURED`` status before any
result is printed.

The V1 source and artifact remain immutable under the delivery manifest so the
defect and its repair retain separate identities.
"""

from __future__ import annotations

import run_v1 as delivered


def evaluate(split, models, threshold, n=360, probe=True):
    """Run the delivered evaluator and remove its unsupported numeric field."""

    out, tasks = delivered.evaluate(split, models, threshold, n=n, probe=probe)
    for policy, metrics in out.items():
        legacy = metrics.pop("false_commit")
        if legacy != 0.0:
            raise AssertionError(
                f"delivered false_commit constant changed for {policy}: {legacy!r}"
            )
        metrics["false_commit_status"] = "NOT_MEASURED"
    return out, tasks


def _render_metric(name: str, value: object) -> str:
    if name == "false_commit_status":
        if value != "NOT_MEASURED":
            raise AssertionError(f"unexpected false-commit status: {value!r}")
        return f"{name}={value}"
    if not isinstance(value, (int, float)):
        raise TypeError(f"unexpected metric value for {name}: {value!r}")
    return f"{name}={value:.3f}"


def main() -> None:
    train = delivered.make_training(700, probe=True)
    models = delivered.fit_models(train)
    threshold = 0.50
    print("frozen threshold", threshold)
    for split in ["iid", "scale", "length", "mixed"]:
        out, _ = evaluate(split, models, threshold, n=80, probe=True)
        print("\n==", split, "==")
        for policy, metrics in out.items():
            print(policy, " ".join(_render_metric(name, value) for name, value in metrics.items()))


if __name__ == "__main__":
    main()
