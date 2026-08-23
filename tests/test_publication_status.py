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
    assert payload["programme"]["close_allowed"] is True
    assert payload["programme"]["status"] == "PEER_REVIEW_READY"


def test_p1_through_p5_are_peer_review_ready_on_scoped_artifact_gates():
    """All five publication packages may close while broader excluded claims stay unresolved.

    P3 is ready on its bounded mapping / P3-X identity-authority claim, not the
    unexecuted raw-text/downstream programme. P5 is ready on bounded
    non-self-promotion / authority separation, not on the unexecuted fresh-transfer
    superiority campaign. The scoreboard must represent scoped publication
    readiness without laundering either excluded claim into evidence.
    """

    module = _load_module()
    derived = module.derive_scoreboard(ROOT)
    by_id = {paper["paper_id"]: paper for paper in derived["papers"]}
    for paper_id in ("P1", "P2", "P3", "P4", "P5"):
        assert by_id[paper_id]["status"] == "PEER_REVIEW_READY", paper_id
        assert by_id[paper_id]["journal_readiness_terminal"] == "PEER_REVIEW_READY"
        assert by_id[paper_id]["attestation_paths"]
        assert by_id[paper_id]["claim_ledgers"]
        assert not by_id[paper_id]["missing_artifacts"], paper_id
    assert derived["programme"]["papers_peer_review_ready"] == ["P1", "P2", "P3", "P4", "P5"]
    assert derived["programme"]["close_allowed"] is True
    assert derived["programme"]["status"] == "PEER_REVIEW_READY"


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


def test_p5_scoped_readiness_preserves_unexecuted_performance_boundary():
    """P5's governance paper may be ready while its stronger performance claim stays open.

    This is the key scoped-publication case: the fail-closed paper-specific evidence
    gate corroborates the non-self-promotion claim, while the V1 development
    protocol may still record UNBOUND identities and the claim ledger may still
    record the separate external fresh-transfer campaign as CANNOT_CHECK. Those
    facts must remain visible rather than being erased to manufacture readiness.
    """

    module = _load_module()
    p5 = next(paper for paper in module.derive_scoreboard(ROOT)["papers"] if paper["paper_id"] == "P5")
    assert p5["status"] == "PEER_REVIEW_READY"
    assert p5["journal_readiness_terminal"] == "PEER_REVIEW_READY"
    assert p5["claim_ledgers"]
    assert p5["attestation_paths"]
    assert p5["unbound_execution_bindings"], "the separate fresh-transfer protocol boundary was silently erased"
    joined = "\n".join(p5["claim_ledger_cannot_check"])
    assert "CANNOT_CHECK" in joined or "EXTERNAL NOT EXECUTED" in joined
    assert p5["missing_artifacts"] == []


def test_forged_peer_review_ready_is_rejected(monkeypatch: pytest.MonkeyPatch):
    """Validation must still reject invented readiness even when all real papers are ready.

    A permanently blocked real paper is not needed as a test fixture. Instead we
    synthesize a derived tree state in which P5 is blocked and verify that a payload
    forged to retain PEER_REVIEW_READY is rejected. This keeps the test about the
    validation invariant rather than requiring the research programme to preserve
    an artificial loser forever.
    """

    module = _load_module()
    honest = module.derive_scoreboard(ROOT)
    forged = json.loads(json.dumps(honest))
    synthetic_derived = json.loads(json.dumps(honest))
    victim = next(paper for paper in synthetic_derived["papers"] if paper["paper_id"] == "P5")
    victim["status"] = "BLOCKED"
    victim["journal_readiness_terminal"] = "CANNOT_CHECK"
    victim["missing_artifacts"] = ["synthetic blocker for anti-forgery test"]
    synthetic_derived["programme"]["status"] = "BLOCKED"
    synthetic_derived["programme"]["close_allowed"] = False
    synthetic_derived["programme"]["papers_peer_review_ready"] = ["P1", "P2", "P3", "P4"]

    monkeypatch.setattr(module, "derive_scoreboard", lambda _root=None: synthetic_derived)
    errors = module.validate_scoreboard(forged, ROOT)
    assert any("P5" in error and "PEER_REVIEW_READY" in error for error in errors), (
        "validate_scoreboard accepted a forged PEER_REVIEW_READY when the derived tree was blocked"
    )


def test_close_allowed_matches_all_five_ready():
    module = _load_module()
    payload = module.derive_scoreboard(ROOT)
    assert payload["programme"]["close_allowed"] is True
    tampered = json.loads(json.dumps(payload))
    tampered["programme"]["close_allowed"] = False
    errors = module.validate_scoreboard(tampered, ROOT)
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
    """A terminal only a human can read is not a terminal this scoreboard has."""

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
