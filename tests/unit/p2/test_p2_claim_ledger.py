"""Operative P2 claim-ledger tests after the post-P2-X manuscript promotion.

The original test module is preserved byte-for-byte as
``_p2_claim_ledger_tests_v1.py``. All of its tests/fixtures remain exported;
two stale fixtures are refreshed without weakening their invariants:

* the unledgered-conclusion insertion anchor follows the current bounded
  ``CANNOT_CHECK`` conclusion sentence;
* the unsupported-strength mutation targets the current live ``NONE_YET`` claim
  rather than an externally supported claim whose support class later changed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


_V1_PATH = Path(__file__).with_name("_p2_claim_ledger_tests_v1.py")
_SPEC = importlib.util.spec_from_file_location("_p2_claim_ledger_tests_v1", _V1_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot load preserved P2 claim-ledger tests")
_V1 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_V1)

_REPLACED_TEST_NAMES = {
    "test_new_unledgered_conclusion_claim_is_caught",
    "test_unsupported_claim_may_not_be_downgraded_to_descriptive",
}
_PRESERVED_TEST_NAMES = {
    name for name in dir(_V1) if name.startswith("test_") and name not in _REPLACED_TEST_NAMES
}

for _name in dir(_V1):
    if _name.startswith("__") or _name in _REPLACED_TEST_NAMES:
        continue
    _value = getattr(_V1, _name)
    globals()[_name] = _value
    if _name.startswith("test_") or hasattr(_value, "_pytestfixturefunction"):
        try:
            _value.__module__ = __name__
        except (AttributeError, TypeError):
            pass


def test_preserved_v1_suite_export_is_complete() -> None:
    exported = {name for name in globals() if name.startswith("test_")}
    assert _PRESERVED_TEST_NAMES <= exported


def test_unsupported_claim_may_not_be_downgraded_to_descriptive(paper: Path) -> None:
    """A live NONE_YET claim must stay CANNOT_CHECK, not become DESCRIPTIVE."""
    ledger = load_ledger(paper)
    target = claim(ledger, "P2-R41")
    assert target["support_type"] == "NONE_YET"
    assert target["strength"] == "CANNOT_CHECK"
    target["strength"] = "DESCRIPTIVE"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "OVERSTATED_STRENGTH" in messages(proc)


def test_new_unledgered_conclusion_claim_is_caught(paper: Path) -> None:
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    marker = "Deployed multi-provider/retrieval-engine generality remains \\texttt{CANNOT\\_CHECK}.\n"
    assert marker in source
    main.write_text(
        source.replace(
            marker,
            marker + "\nThe system achieves a recall of 0.93 on the open web.\n",
            1,
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "UNLEDGERED_CLAIM" in messages(proc)
