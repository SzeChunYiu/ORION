"""A replication drawn from another year must be able to reach this evaluator.

`P1-U-T2` recorded that the 2019 replication "cannot run through this evaluator
at all": the primary year was the literal `2020` in two row checks, so every row
of any other corpus failed the year check, every source id missed the frozen
expectation, and the run came back as a frozen-corpus `CANNOT_CHECK` with zero
episodes scored and nothing raised. Two separate defects wearing one symptom.

The first is that the year was written in the checker instead of read from the
source set that declares it -- `FIXED_SOURCE_SET_V1.json` has carried
`primary_year` all along.

The second is the more interesting one. Being handed a corpus built from
different sources is not an undetermined measurement; it is a determinate fact
about the object presented, and the evaluator can state it. Reporting it as
`CANNOT_CHECK` says "I could not tell" about something it can tell perfectly
well, which is the same conflation the three-valued discipline exists to
prevent, pointed the other way.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVAL_PATH = ROOT / "research" / "claim_expansion" / "p1" / "gpt_r6" / "evaluate_native.py"
FIXED_PATH = (
    ROOT / "research" / "claim_expansion" / "p1" / "gpt_r5" / "FIXED_SOURCE_SET_V1.json"
)


def _load():
    spec = importlib.util.spec_from_file_location("p1_r6_year_probe", EVAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["p1_r6_year_probe"] = module
    spec.loader.exec_module(module)
    return module


def test_the_primary_year_comes_from_the_source_set() -> None:
    module = _load()
    declared = int(json.loads(FIXED_PATH.read_text(encoding="utf-8"))["primary_year"])
    assert module.PRIMARY_YEAR == declared
    assert "!= 2020" not in EVAL_PATH.read_text(encoding="utf-8"), (
        "the year is a property of the source set; writing it in the checker is "
        "what made another year unrunnable"
    )


def test_the_frozen_corpus_still_validates_and_still_says_which_year() -> None:
    module = _load()
    pairs, unresolved = module.CORPUS.build()
    data = module.validate_fixed_corpus(list(pairs), list(unresolved))
    assert data["complete"], data["errors"]
    assert data["source_set"] == "FROZEN"
    assert data["primary_year"] == module.PRIMARY_YEAR
    assert {row["source_year"] for row in pairs} == {module.PRIMARY_YEAR}


def test_a_different_corpus_is_refused_rather_than_reported_undetermined() -> None:
    module = _load()
    pairs, unresolved = module.CORPUS.build()

    other_year = module.PRIMARY_YEAR - 1

    def restamp(row: dict) -> dict:
        moved = dict(row)
        moved["source_id"] = f"doi:10.9999/replication-{other_year}-{row['source_id']}"
        moved["source_year"] = other_year
        return moved

    replication_pairs = [restamp(dict(row)) for row in pairs]
    replication_unres = [restamp(dict(row)) for row in unresolved]

    data = module.validate_fixed_corpus(replication_pairs, replication_unres)
    assert data["source_set"] == "DISJOINT", data["source_set"]
    assert not data["complete"]

    result = module.evaluate(replication_pairs, replication_unres)
    assert result["terminal"] == "P1_R6_REFUSED_NOT_THE_FROZEN_SOURCE_SET", result["terminal"]
    assert result["terminal"] != "P1_R6_CANNOT_CHECK_FIXED_CORPUS"


def test_an_incomplete_frozen_corpus_is_still_undetermined() -> None:
    """The refusal must not swallow the case it was carved out of.

    Dropping one source from the frozen set leaves the same corpus, short a row.
    That genuinely is a measurement that could not be taken, and it must keep
    reporting as one -- otherwise the new terminal has simply relabelled every
    failure as somebody else's object.
    """

    module = _load()
    pairs, unresolved = module.CORPUS.build()
    short = list(pairs)[:-1]

    data = module.validate_fixed_corpus(short, list(unresolved))
    assert data["source_set"] == "PARTIAL"
    assert not data["complete"]
    assert module.evaluate(short, list(unresolved))["terminal"] == (
        "P1_R6_CANNOT_CHECK_FIXED_CORPUS"
    )
