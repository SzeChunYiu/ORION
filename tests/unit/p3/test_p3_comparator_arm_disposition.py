"""The comparator-arm disposition must bind to real receipts, on the real tree.

These tests run against the committed disposition and the committed evidence,
not a fixture. A checker validated only on fixtures passes while whole classes
of defect go unseen, so every mutation below is applied to the real document
and every digest is verified against the real file.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from orion.study.p3.comparator_arm_disposition import (
    DISPOSITIONS,
    EXIT_CANNOT_CHECK,
    EXIT_EVIDENCE,
    EXIT_OVERCLAIM,
    EXIT_PASS,
    EXIT_SCHEMA,
    EXIT_UNCONDITIONED,
    check_disposition,
)

PACKET = Path("development/p3-comparator-arm-disposition-v22-2026-08-24")
DISPOSITION = PACKET / "COMPARATOR_ARM_DISPOSITION_V22.json"


def _root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / DISPOSITION).is_file():
            return parent
    pytest.skip("repository root with the disposition packet not found")


@pytest.fixture(scope="module")
def root() -> Path:
    return _root()


@pytest.fixture(scope="module")
def document(root: Path) -> dict:
    return json.loads((root / DISPOSITION).read_text(encoding="utf-8"))


def test_the_committed_disposition_passes_against_the_real_tree(root, document):
    """The no-alarm case. A checker that cries wolf on its first real run gets switched off."""

    verdict = check_disposition(document, root)
    assert verdict.exit_code == EXIT_PASS, verdict.problems
    assert verdict.arms_checked == 2


def test_both_required_arms_are_present(document):
    assert {arm["arm"] for arm in document["arms"]} == {"AML", "LogMap"}


def test_aml_is_scored_and_logmap_is_cannot_check(document):
    verdicts = {arm["arm"]: arm["disposition"] for arm in document["arms"]}
    assert verdicts == {"AML": "SCORED", "LogMap": "CANNOT_CHECK"}
    assert set(verdicts.values()) <= DISPOSITIONS


def test_a_tampered_scored_digest_is_caught(root, document):
    mutated = copy.deepcopy(document)
    mutated["arms"][0]["evidence"][0]["sha256"] = "0" * 64
    assert check_disposition(mutated, root).exit_code == EXIT_EVIDENCE


def test_missing_evidence_is_caught(root, document):
    mutated = copy.deepcopy(document)
    mutated["arms"][0]["evidence"][0]["path"] = "development/does-not-exist/missing.rdf"
    assert check_disposition(mutated, root).exit_code == EXIT_EVIDENCE


def test_a_tampered_blocking_digest_is_caught(root, document):
    mutated = copy.deepcopy(document)
    mutated["arms"][1]["blocking_conditions"][0]["evidence_sha256"] = "f" * 64
    assert check_disposition(mutated, root).exit_code == EXIT_EVIDENCE


def test_cannot_check_without_promotion_conditions_is_refused(root, document):
    """CANNOT_CHECK with no way forward is a dead end dressed as a verdict."""

    mutated = copy.deepcopy(document)
    del mutated["arms"][1]["promotion_conditions"]
    verdict = check_disposition(mutated, root)
    assert verdict.exit_code == EXIT_UNCONDITIONED
    assert any("promotion_conditions" in problem for problem in verdict.problems)


def test_cannot_check_without_blocking_conditions_is_refused(root, document):
    mutated = copy.deepcopy(document)
    del mutated["arms"][1]["blocking_conditions"]
    assert check_disposition(mutated, root).exit_code == EXIT_UNCONDITIONED


@pytest.mark.parametrize(
    "phrase",
    ["LogMap is unavailable here.", "The arm cannot be run.", "It failed to produce output."],
)
def test_the_unavailability_overclaim_is_refused(root, document, phrase):
    """LogMap runs -- V11 bound a 90/90 closure and exited zero. Saying otherwise is false."""

    mutated = copy.deepcopy(document)
    mutated["arms"][1]["what_is_true_instead"] = phrase
    assert check_disposition(mutated, root).exit_code == EXIT_OVERCLAIM


def test_quoting_an_overclaim_in_order_to_disclaim_it_is_allowed(root, document):
    """`explicitly_not_claimed` exists to name the overclaims; scanning it would punish honesty."""

    assert "LogMap is unavailable" in document["arms"][1]["explicitly_not_claimed"]
    assert check_disposition(document, root).exit_code == EXIT_PASS


def test_an_unknown_disposition_is_refused(root, document):
    mutated = copy.deepcopy(document)
    mutated["arms"][0]["disposition"] = "PROBABLY_FINE"
    assert check_disposition(mutated, root).exit_code == EXIT_SCHEMA


def test_cannot_check_may_not_also_claim_it_was_scored(root, document):
    mutated = copy.deepcopy(document)
    mutated["arms"][1]["scored_against_reference"] = True
    assert check_disposition(mutated, root).exit_code == EXIT_SCHEMA


def test_scored_must_actually_say_it_was_scored(root, document):
    mutated = copy.deepcopy(document)
    mutated["arms"][0]["scored_against_reference"] = False
    assert check_disposition(mutated, root).exit_code == EXIT_SCHEMA


@pytest.mark.parametrize("bad", [None, "doc", 7, [], {}, {"arms": []}])
def test_malformed_documents_cannot_be_checked_and_never_pass(root, bad):
    verdict = check_disposition(bad, root)
    assert verdict.exit_code == EXIT_CANNOT_CHECK
    assert not verdict.passed


def test_the_artifact_creates_no_result(document):
    """This is a disposition, not a campaign. It must say so in machine-readable form."""

    assert document["results_exist"] is False
    assert document["campaign_executed"] is False
    assert document["outcome_accessed"] is False


def test_the_open_boxes_are_named_as_out_of_scope(document):
    """Nobody should later read this file as covering the whole P3 section."""

    out = document["out_of_scope_boxes"]
    assert any("MELT" in key for key in out)
    assert any("natural ontology-pair" in key for key in out)
    assert all("NOT addressed" in value for value in out.values())


def test_the_logmap_wrapper_measurement_is_stated_exactly(document):
    logmap = next(arm for arm in document["arms"] if arm["arm"] == "LogMap")
    wrapper = next(c for c in logmap["blocking_conditions"] if c["id"] == "LM-B3")
    assert wrapper["measured"] == {"rows_total": 16, "rows_with_optional_wrapper": 16}


def test_the_optional_wrapper_measurement_is_true_of_the_real_logmap_output(root, document):
    """Re-measure the claim against the committed artifact rather than trusting the number.

    The recorded 16/16 is what makes LM-B3 a real interface defect rather than
    an assertion, so it is re-derived here from the file the blocking
    condition cites.
    """

    logmap = next(arm for arm in document["arms"] if arm["arm"] == "LogMap")
    wrapper = next(c for c in logmap["blocking_conditions"] if c["id"] == "LM-B3")
    tsv = root / wrapper["evidence_path"]
    rows = [line for line in tsv.read_text(encoding="utf-8").splitlines() if line.strip()]
    wrapped = [line for line in rows if "Optional.of(" in line]
    assert len(rows) == wrapper["measured"]["rows_total"]
    assert len(wrapped) == wrapper["measured"]["rows_with_optional_wrapper"]
    assert len(wrapped) == len(rows), "the defect is total, not partial"
