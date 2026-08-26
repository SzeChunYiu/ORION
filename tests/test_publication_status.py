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
    # The verdict is derived, not pinned here. Pinning it is what let the
    # committed file assert close_allowed=true and all five ready while the
    # checker computed BLOCKED -- the file's own validator rejected it, and the
    # test that should have caught that was asserting the stale answer instead.
    derived = module.derive_scoreboard(ROOT)
    assert payload["programme"] == derived["programme"]


def test_scoped_readiness_reflects_the_artifacts_not_the_ambition():
    """Two of five are ready on scoped gates; three are blocked, and honestly so.

    This asserted all five until the repository corrected itself past it. P1 and
    P5 declare CANNOT_CHECK in their current readiness records -- P5's frozen
    96-case panel returned NO_TERMINAL_UNDER_FROZEN_RULES. P4 now version-separates
    its current CANNOT_CHECK lifecycle from the immutable protected-V2 readiness
    archive. The papers were honest; the committed scoreboard and this test were
    the stale pair.

    P3 is ready on its bounded mapping / P3-X identity-authority claim, not the
    unexecuted raw-text/downstream programme. Scoped readiness must not launder
    an excluded claim into evidence, and neither must it launder an unready
    paper into a ready one.
    """

    module = _load_module()
    derived = module.derive_scoreboard(ROOT)
    by_id = {paper["paper_id"]: paper for paper in derived["papers"]}

    for paper_id in ("P2", "P3"):
        assert by_id[paper_id]["status"] == "PEER_REVIEW_READY", paper_id
        assert by_id[paper_id]["journal_readiness_terminal"] == "PEER_REVIEW_READY"
        assert by_id[paper_id]["attestation_paths"], paper_id
        assert by_id[paper_id]["claim_ledgers"], paper_id
        assert not by_id[paper_id]["missing_artifacts"], paper_id

    for paper_id in ("P1", "P4", "P5"):
        assert by_id[paper_id]["status"] == "BLOCKED", paper_id
        assert by_id[paper_id]["journal_readiness_terminal"] == "CANNOT_CHECK", paper_id
        assert by_id[paper_id]["missing_artifacts"], (
            f"{paper_id} is blocked; the artifacts it lacks must be named, or the "
            "block is unactionable"
        )

    assert by_id["P4"]["journal_readiness"].endswith("CURRENT_JOURNAL_READINESS_V1.md")
    assert derived["programme"]["papers_peer_review_ready"] == ["P2", "P3"]
    assert derived["programme"]["close_allowed"] is False
    assert derived["programme"]["status"] == "BLOCKED"


def test_p2_readiness_rests_on_an_unambiguous_terminal_line():
    """Guard the mechanism, not just the outcome.

    P2's readiness is read from one line. If a scope caveat drifts back onto
    that line so it names both PEER_REVIEW_READY and CANNOT_CHECK, the parser
    resolves fail-closed and P2 silently returns BLOCKED -- and every downstream
    test starts failing for a reason that has nothing to do with P2's evidence.
    Naming the cause here means the failure message points at the sentence.

    Previously called module.terminal_line_is_ambiguous, which does not exist;
    the test raised AttributeError rather than checking anything, so the drift it
    guards against would not have been caught.
    """
    module = _load_module()
    readiness = (
        ROOT / "papers" / "paper-02-open-world-scientific-discovery" / "JOURNAL_READINESS.md"
    ).read_text(encoding="utf-8")
    terminal = module.parse_journal_readiness_terminal(readiness)
    assert terminal == "PEER_REVIEW_READY", (
        "P2's terminal line no longer resolves to PEER_REVIEW_READY "
        f"(got {terminal!r}); the scoreboard reads one line and resolves it "
        "fail-closed, so a scope caveat on that line blocks the paper"
    )


def test_p1_block_is_artifact_backed_not_inferred_from_a_closed_issue():
    """#98's state is irrelevant in both directions.

    This test used to assert P1 ready on a successor bundle and attestation. P1
    now declares CANNOT_CHECK in its own JOURNAL_READINESS and the artifacts the
    scoreboard requires are absent, so it is blocked -- and the block must rest
    on those missing artifacts, not on an issue being open, exactly as the
    readiness claim had to rest on artifacts rather than on an issue being
    closed. The principle is unchanged; the answer moved.
    """
    module = _load_module()
    p1 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P1")
    assert p1["status"] == "BLOCKED"
    assert p1["journal_readiness_terminal"] == "CANNOT_CHECK"
    assert p1["missing_artifacts"], "a block with no named missing artifact is unactionable"
    assert p1["outcome_accessed"] is False


def test_p5_block_preserves_the_unexecuted_performance_boundary():
    """P5 is blocked, and the boundary it always carried must survive that.

    The scoped-publication point this test was written for still holds: the
    separate external fresh-transfer campaign is CANNOT_CHECK and the V1
    development protocol may record UNBOUND identities, and neither may be
    erased to manufacture a verdict. What changed is the direction of the
    pressure. Erasing them once risked manufacturing readiness; now the risk is
    treating a blocked paper as having no bounded result at all. Both facts stay
    visible.
    """

    module = _load_module()
    p5 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P5")
    assert p5["status"] == "BLOCKED"
    assert p5["journal_readiness_terminal"] == "CANNOT_CHECK"
    assert p5["missing_artifacts"], "a block with no named missing artifact is unactionable"
    assert p5["claim_ledgers"], "the ledger must remain readable even while blocked"
    joined = "\n".join(p5["claim_ledger_cannot_check"])
    assert "CANNOT_CHECK" in joined or "EXTERNAL NOT EXECUTED" in joined, (
        "the separate fresh-transfer protocol boundary was silently erased"
    )


def test_forged_peer_review_ready_is_rejected(monkeypatch: pytest.MonkeyPatch):
    """Validation must still reject invented readiness even when all real papers are ready.

    A permanently blocked real paper is not needed as a test fixture. We
    synthesize a derived state in which a currently-*ready* paper is blocked, and
    verify that a payload forged to retain PEER_REVIEW_READY is rejected.

    The victim must be a paper that is ready for real. This test used to blocked
    P5, which was ready when it was written and is blocked now -- so the forgery
    became a no-op, the payload already agreed with the synthetic state, and the
    assertion passed on nothing. A forgery test whose forgery matches reality
    detects no forgery.
    """

    module = _load_module()
    honest = module.derive_scoreboard(ROOT)
    forged = json.loads(json.dumps(honest))
    synthetic_derived = json.loads(json.dumps(honest))
    ready_now = honest["programme"]["papers_peer_review_ready"]
    assert ready_now, "no paper is ready; this test needs a real ready paper to forge"
    victim_id = ready_now[0]
    victim = next(paper for paper in synthetic_derived["papers"] if paper["paper_id"] == victim_id)
    victim["status"] = "BLOCKED"
    victim["journal_readiness_terminal"] = "CANNOT_CHECK"
    victim["missing_artifacts"] = ["synthetic blocker for anti-forgery test"]
    synthetic_derived["programme"]["status"] = "BLOCKED"
    synthetic_derived["programme"]["close_allowed"] = False
    synthetic_derived["programme"]["papers_peer_review_ready"] = [
        pid for pid in ready_now if pid != victim_id
    ]

    monkeypatch.setattr(module, "derive_scoreboard", lambda _root=None: synthetic_derived)
    errors = module.validate_scoreboard(forged, ROOT)
    assert any(victim_id in error and "PEER_REVIEW_READY" in error for error in errors), (
        "validate_scoreboard accepted a forged PEER_REVIEW_READY when the derived tree was blocked"
    )


def test_close_allowed_tracks_readiness_in_both_directions():
    """close_allowed must follow the papers, and tampering with it must be caught.

    The invariant is two-sided and the original test only exercised one side of
    it, because when it was written every paper was ready. It asserted
    close_allowed is True and then flipped it to False. With P1 and P5 blocked
    the derived value is False, so that first assertion fails for a reason that
    has nothing to do with the invariant -- and the tamper it checked is now the
    honest value.

    So: assert close_allowed agrees with whether every paper is ready, whichever
    way that falls, and tamper it to its opposite.
    """
    module = _load_module()
    payload = module.derive_scoreboard(ROOT)
    all_ready = all(p["status"] == "PEER_REVIEW_READY" for p in payload["papers"])
    assert payload["programme"]["close_allowed"] is all_ready

    tampered = json.loads(json.dumps(payload))
    tampered["programme"]["close_allowed"] = not all_ready
    errors = module.validate_scoreboard(tampered, ROOT)
    assert any("close_allowed" in error for error in errors), (
        "close_allowed was flipped away from what the papers support and "
        "validation did not object"
    )


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
    """A terminal only a human can read is not a terminal this scoreboard has."""

    module = _load_module()
    for spec in module.PAPER_SPECS:
        path = ROOT / spec["root"] / spec.get("journal_readiness", "JOURNAL_READINESS.md")
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
