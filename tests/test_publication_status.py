from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "research" / "publication" / "scoreboard.py"
STATUS_PATH = ROOT / "research" / "publication" / "publication_status.json"
SCHEMA_PATH = ROOT / "research" / "publication" / "publication_status.schema.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("publication_scoreboard", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_schema_is_json_schema():
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert payload["$id"] == "orion.publication-status.v1"
    assert payload["required"] == ["schema_version", "generated_from", "programme", "papers"]


def test_committed_scoreboard_matches_derived_artifacts():
    module = _load_module()
    payload = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    assert payload["schema_version"] == module.SCHEMA_VERSION
    errors = module.validate_scoreboard(payload, ROOT)
    assert errors == []
    assert payload["programme"]["issue"] == 97
    assert payload["programme"]["close_allowed"] is False
    assert payload["programme"]["status"] == "BLOCKED"


def test_p1_p2_and_p4_are_peer_review_ready_and_others_are_blocked():
    """P2 joined P1 and P4 when its terminal line stopped naming two terminals.

    This previously pinned P2 as BLOCKED. That was a true description of the
    scoreboard and a false description of the paper: P2's terminal line declared
    `PEER_REVIEW_READY` on a bounded claim while naming the excluded superiority
    claim as `CANNOT_CHECK` in the same sentence, and the parser resolves any
    `CANNOT_CHECK` on that line as the verdict. Its own fail-closed evidence gate
    reported `ok=True` with no blockers throughout.

    Splitting the verdict from its scope moved P2 to PEER_REVIEW_READY. Updating
    the expectation is therefore recording a fixed defect, not relaxing a bar --
    every corroborating condition below is still asserted for P2, and P3 and P5
    are still required to be blocked with a named reason.
    """

    module = _load_module()
    derived = module.derive_scoreboard(ROOT)
    by_id = {paper["paper_id"]: paper for paper in derived["papers"]}
    for paper_id in ("P1", "P2", "P4"):
        assert by_id[paper_id]["status"] == "PEER_REVIEW_READY", paper_id
        assert by_id[paper_id]["journal_readiness_terminal"] == "PEER_REVIEW_READY"
        assert by_id[paper_id]["attestation_paths"]
        assert by_id[paper_id]["claim_ledgers"]
        assert not by_id[paper_id]["missing_artifacts"], paper_id
    for paper_id in ("P3", "P5"):
        assert by_id[paper_id]["status"] == "BLOCKED", paper_id
        assert by_id[paper_id]["journal_readiness_terminal"] == "CANNOT_CHECK"
        assert by_id[paper_id]["missing_artifacts"]
    assert derived["programme"]["papers_peer_review_ready"] == ["P1", "P2", "P4"]
    # Still false: two papers remain blocked, so the programme does not close.
    assert derived["programme"]["close_allowed"] is False


def test_p2_readiness_rests_on_an_unambiguous_terminal_line():
    """Guard the mechanism, not just the outcome.

    If the scope caveat drifts back onto the terminal line, P2 silently returns to
    BLOCKED with twelve blockers and the test above starts failing for a reason
    that has nothing to do with P2's evidence. Naming the cause here means the
    failure message points at the sentence.
    """

    module = _load_module()
    readiness = (
        ROOT / "papers" / "paper-02-open-world-scientific-discovery" / "JOURNAL_READINESS.md"
    ).read_text(encoding="utf-8")
    assert module.terminal_line_is_ambiguous(readiness) is None, (
        "P2's terminal line names both PEER_REVIEW_READY and CANNOT_CHECK again; the "
        "scoreboard reads that one line and will resolve it fail-closed"
    )


def test_p1_readiness_is_artifact_backed_not_inferred_from_closed_issue():
    """#98's state is irrelevant; the successor bundle and attestation authorize P1."""
    module = _load_module()
    p1 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P1")
    assert p1["status"] == "PEER_REVIEW_READY"
    assert p1["protocol_status"] == "EXECUTION_FROZEN"
    assert p1["outcome_accessed"] is False
    assert p1["missing_artifacts"] == []
    assert p1["attestation_paths"] == [
        "papers/paper-01-recursive-epistemic-reconstruction/evidence/PEER_REVIEW_READY_BOUNDED_V2.md"
    ]


def test_p5_is_blocked_by_unbound_identities_and_unexecuted_claims():
    """P5 gained a claim ledger in #308; it is still blocked, for stronger reasons.

    This test previously asserted the ledger was *absent*. That premise expired
    when the ledger landed, and an expired premise is not evidence of anything --
    a paper acquiring its ledger is progress, not a regression. The blockers that
    actually survive are the unbound protocol identities and the ledger's own
    unexecuted external rows, so those are what is pinned here.
    """

    module = _load_module()
    p5 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P5")
    assert p5["status"] == "BLOCKED"
    assert p5["claim_ledgers"] == ["papers/paper-05-self-orion/evidence/CLAIM_LEDGER_V1.md"]
    assert p5["protocol_status"] == "DESIGN_FROZEN"
    assert p5["unbound_execution_bindings"]
    joined = "\n".join(p5["missing_artifacts"])
    assert "not PEER_REVIEW_READY" in joined
    assert "UNBOUND identities remain" in joined
    assert "EXTERNAL NOT EXECUTED" in joined


def test_forged_peer_review_ready_is_rejected():
    """Claiming readiness in the JSON must not survive validation against the tree.

    The subject is derived from whichever papers are actually blocked rather than
    hardcoded. It used to name P2, which stopped being a forgery the moment P2
    became genuinely ready -- the test then asserted that a true statement ought to
    be rejected, and failed for a reason unrelated to forgery. Deriving the subject
    keeps this about forgery instead of about which paper happens to be blocked.
    """

    module = _load_module()
    payload = module.derive_scoreboard(ROOT)
    blocked = [paper for paper in payload["papers"] if paper["status"] == "BLOCKED"]
    assert blocked, "no blocked paper left to forge; this test needs a new subject"
    victim = blocked[0]
    paper_id = victim["paper_id"]
    victim["status"] = "PEER_REVIEW_READY"
    victim["missing_artifacts"] = []
    payload["programme"]["status"] = "BLOCKED"
    payload["programme"]["close_allowed"] = False
    errors = module.validate_scoreboard(payload, ROOT)
    assert any(paper_id in error and "PEER_REVIEW_READY" in error for error in errors), (
        f"validate_scoreboard accepted a forged PEER_REVIEW_READY for {paper_id}"
    )


def test_close_allowed_requires_all_five_ready():
    module = _load_module()
    payload = module.derive_scoreboard(ROOT)
    payload["programme"]["close_allowed"] = True
    errors = module.validate_scoreboard(payload, ROOT)
    assert any("close_allowed" in error for error in errors)


def test_terminal_parser_distinguishes_ready_from_cannot_check():
    module = _load_module()
    ready = "**Terminal:** `ORION-P4 = PEER_REVIEW_READY`\n"
    blocked = "**Current terminal:** `CANNOT_CHECK` for external superiority / not peer-review ready.\n"
    negated = "**Current terminal:** `CANNOT_CHECK`; **not** `PEER_REVIEW_READY`.\n"
    assert module.parse_journal_readiness_terminal(ready) == "PEER_REVIEW_READY"
    assert module.parse_journal_readiness_terminal(blocked) == "CANNOT_CHECK"
    assert module.parse_journal_readiness_terminal(negated) == "CANNOT_CHECK"


def test_a_narrowed_terminal_is_never_scored_as_peer_review_ready():
    """`PEER_REVIEW_READY_NARROWED` is a weaker terminal, not the full one.

    A substring test reads it as `PEER_REVIEW_READY`, and it fails in the
    inflating direction: nothing downstream re-derives the terminal, so a paper
    that deliberately narrowed its claim would be scored as ready to submit.
    """

    module = _load_module()
    narrowed = "**Terminal:** `ORION-P2 = PEER_REVIEW_READY_NARROWED`\n"
    assert module.parse_journal_readiness_terminal(narrowed) != "PEER_REVIEW_READY"
    assert module.readme_records_peer_review_ready(
        "**Status:** `PEER_REVIEW_READY_NARROWED`\n"
    ) is False
    # No-alarm control: the exact full terminal is still recognized, so this
    # guard cannot pass by refusing every terminal it is shown.
    assert module.readme_records_peer_review_ready("**Status:** `PEER_REVIEW_READY`\n") is True

    # The third consumer of this token. Its anchor was reasoned to be safe --
    # `PEER_REVIEW_READY_NARROWED` cannot reach the trailing `.**` -- but a
    # reasoned-safe guard in the same family as two that were not is worth
    # asserting rather than inferring, since the failure would be silent and in
    # the inflating direction.
    narrowed_declaration = "**`ORION-P2 = PEER_REVIEW_READY_NARROWED`.**"
    assert module.journal_readiness_declares_complete(narrowed_declaration, "P2") is False
    assert (
        module.journal_readiness_declares_complete("**`ORION-P2 = PEER_REVIEW_READY`.**", "P2")
        is True
    )


def test_every_paper_declares_a_machine_scorable_terminal():
    """A terminal only a human can read is not a terminal this scoreboard has.

    Paper 2's `**Scientific terminal:**` / `**Publication terminal:**` pair was
    invisible to `TERMINAL_LINE`, so the scoreboard reported it as having no
    scorable terminal and the committed snapshot silently disagreed with the
    derived one. Pin the declaration form for every paper rather than only
    repairing the one that drifted.
    """

    module = _load_module()
    for spec in module.PAPER_SPECS:
        path = ROOT / spec["root"] / "JOURNAL_READINESS.md"
        terminal = module.parse_journal_readiness_terminal(
            path.read_text(encoding="utf-8")
        )
        assert terminal in {"PEER_REVIEW_READY", "CANNOT_CHECK"}, spec["paper_id"]


def test_cli_check_accepts_committed_snapshot(capsys: pytest.CaptureFixture[str]):
    module = _load_module()
    # The committed file must already match; --check is the CI gate.
    errors = module.validate_scoreboard(
        json.loads(STATUS_PATH.read_text(encoding="utf-8")),
        ROOT,
    )
    assert errors == []
    assert capsys.readouterr().out == ""
