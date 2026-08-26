"""A scoped terminal declaration must not fail silently.

P2 declared, on one line:

    `ORION-P2 = PEER_REVIEW_READY` on the bounded methods / critical system-design
    claim as of 2026-08-18. ... external ORION-vs-baseline superiority remains
    `CANNOT_CHECK` and is not part of the ready claim.

That is correct and careful prose. It is also unresolvable for a parser that
returns one terminal, and `parse_journal_readiness_terminal` resolves it
fail-closed: any `CANNOT_CHECK` on the terminal line wins. So P2 scored
`CANNOT_CHECK` with twelve blockers while its own fail-closed evidence gate,
`orion.publication.peer_review_ready.evaluate_paper`, reported `ok=True` with
none — and nothing in the output connected the two.

The fail-closed resolution is right and stays. What was wrong is that it was
silent: "the declaration could not be resolved" and "the paper declared itself
not ready" are different states, and only the first is fixed by editing a
sentence.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCOREBOARD = ROOT / "research" / "publication" / "scoreboard.py"
P2_READINESS = (
    ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "JOURNAL_READINESS.md"
)


def _scoreboard():
    spec = importlib.util.spec_from_file_location("scoreboard_under_test", SCOREBOARD)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registering before exec_module: a @dataclass in the module resolves its own
    # module by name during class creation and raises AttributeError otherwise.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _readiness(terminal: str) -> str:
    return f"# heading\n\n**Current terminal:** {terminal}\n"


def test_a_scoped_declaration_is_still_resolved_fail_closed() -> None:
    """Behaviour must not change: naming both terminals still scores CANNOT_CHECK."""

    scoreboard = _scoreboard()
    both = _readiness(
        "`ORION-P2 = PEER_REVIEW_READY` on the bounded claim; external superiority "
        "remains `CANNOT_CHECK` and is not part of the ready claim."
    )
    assert scoreboard.parse_journal_readiness_terminal(both) == "CANNOT_CHECK"


def test_the_ambiguity_is_reported_rather_than_only_absorbed() -> None:
    """The part that was missing: say so, so the author can fix the line."""

    scoreboard = _scoreboard()
    both = _readiness(
        "`ORION-P2 = PEER_REVIEW_READY` on the bounded claim; external superiority "
        "remains `CANNOT_CHECK` and is not part of the ready claim."
    )
    flagged = scoreboard.terminal_line_is_ambiguous(both)
    assert flagged, "a terminal line naming both terminals must be reported"
    assert "PEER_REVIEW_READY" in flagged and "CANNOT_CHECK" in flagged


def test_unambiguous_lines_are_not_flagged() -> None:
    """Non-vacuity, and the direction that would make the signal useless.

    A detector that flagged every blocked paper would be noise, and the warning
    would be ignored exactly when it mattered. A plain refusal is not ambiguous.
    """

    scoreboard = _scoreboard()
    for terminal in (
        "`ORION-P2 = PEER_REVIEW_READY` on the bounded methods claim as of 2026-08-18.",
        "not PEER_REVIEW_READY. Blocked on the external trial.",
        "`CANNOT_CHECK`.",
        "`PEER_REVIEW_READY_NARROWED` pending the mechanical checks.",
    ):
        assert scoreboard.terminal_line_is_ambiguous(_readiness(terminal)) is None, (
            f"false positive on an unambiguous line: {terminal}"
        )


def test_p2_on_disk_declares_one_terminal() -> None:
    """Guard the specific file, so the scoped caveat cannot drift back onto the line."""

    scoreboard = _scoreboard()
    text = P2_READINESS.read_text(encoding="utf-8")
    assert scoreboard.terminal_line_is_ambiguous(text) is None, (
        "P2's terminal line names both terminals again; move the scope caveat onto "
        "its own line"
    )
    assert scoreboard.parse_journal_readiness_terminal(text) == "PEER_REVIEW_READY"
    # The exclusion must remain visible to a reader. Removing the ambiguity by
    # deleting the caveat would pass the checks above and would be dishonest.
    assert "CANNOT_CHECK" in text, "the excluded superiority claim is no longer recorded"
    # Matched loosely on purpose: the caveat is bolded in the file ("is **not**
    # part of the ready claim"), and an assertion that breaks on emphasis would be
    # a test about markdown rather than about the exclusion surviving.
    assert "part of the ready claim" in text
