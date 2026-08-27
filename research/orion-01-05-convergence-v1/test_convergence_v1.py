from __future__ import annotations

from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from verify_convergence_v1 import validate_changed_paths, verify  # noqa: E402


def test_complete_convergence_subject() -> None:
    verify(ROOT, check_diff=False)


def test_changed_path_policy_rejects_destructive_and_extra_paths() -> None:
    with pytest.raises(AssertionError, match="destructive"):
        validate_changed_paths([("D", "papers/README.md")], {"papers/README.md"})
    with pytest.raises(AssertionError, match="mismatch"):
        validate_changed_paths(
            [("A", "research/orion-01-05-convergence-v1/extra.txt")],
            {"research/orion-01-05-convergence-v1/expected.txt"},
        )
    with pytest.raises(AssertionError, match="outside strict"):
        validate_changed_paths([("A", "src/extra.py")], {"src/extra.py"})


def test_changed_path_policy_allows_only_readme_modification_plus_additions() -> None:
    records = [("M", "papers/README.md"), ("A", "research/orion-01-05-convergence-v1/new.json")]
    validate_changed_paths(records, {path for _, path in records})
