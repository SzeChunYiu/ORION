from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HELDOUT = ROOT / "heldout"


def _load_parts(prefix: str) -> list[object]:
    rows: list[object] = []
    paths = sorted(HELDOUT.glob(f"{prefix}_PART_*.json"))
    if not paths:
        raise RuntimeError(f"no {prefix} parts found")
    for path in paths:
        value = json.loads(path.read_text())
        if not isinstance(value, list):
            raise TypeError(f"{path} is not a JSON list")
        rows.extend(value)
    return rows


def main() -> None:
    cases = _load_parts("CASES")
    dispositions = _load_parts("DISPOSITIONS")

    spec = importlib.util.spec_from_file_location("p1_u_r3_frozen_evaluator", ROOT / "evaluate.py")
    assert spec and spec.loader
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)

    result = evaluator.evaluate(cases, dispositions)
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out = ROOT / "RESULT_V1.json"
    out.write_text(output)
    print(output, end="")


if __name__ == "__main__":
    main()
