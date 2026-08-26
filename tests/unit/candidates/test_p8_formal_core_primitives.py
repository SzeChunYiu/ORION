"""P8's authorization rule may not rest on primitives the theory never defines.

`FORMAL_CORE_V2.md` states Definition 10 clause 2 and all three terminals of Definition 11
in terms of a *blocker*, and never defines one. That is the gap `FORMAL_CORE_V2_1.md`
closes, and this module is the regression guard: it fails on the pre-V2.1 tree and would
fail again if a future core reintroduced an undefined primitive into the authorization rule.

The numbering test matters as much as the coverage test. V2 runs two independent counters
(Definitions to 17, Theorems/Propositions to 9), so an addendum that restarts either one
silently produces two Definition 16s and makes every cross-reference ambiguous.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT = ROOT / "papers" / "orion-18-epistemic-authority-autonomous-science" / "manuscript"
V2 = MANUSCRIPT / "FORMAL_CORE_V2.md"
V2_1 = MANUSCRIPT / "FORMAL_CORE_V2_1.md"

HEADER_RE = re.compile(r"^### (Definition|Theorem|Proposition|Corollary|Lemma) ([\d.]+)(?: — (.+))?$", re.M)

# Every primitive Definition 10 and Definition 11 read. Each must be defined somewhere in
# the core. `blocker` is the one V2 omitted.
AUTHORIZATION_PRIMITIVES = (
    "effect request",
    "obligation",
    "blocker",
    "authority context",
    "support family",
    "revocation",
    "protected root",
    "coercion",
)

# Quantities Definition 10 must be shown *not* to read. Naming them is what makes the
# non-substitution result statable at all.
SEPARATED_QUANTITIES = ("confidence", "expected utility")


def _read(path: Path) -> str:
    """A missing core is a finding, not a crash.

    Erroring out of a fixture buries the diagnosis under twelve identical tracebacks; the
    useful output is "blocker has no definition", which needs the assertions to run.
    """

    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _headers(path: Path) -> list[tuple[str, str, str]]:
    return [(kind, number, (title or "").strip()) for kind, number, title in HEADER_RE.findall(_read(path))]


@pytest.fixture(scope="module")
def all_headers() -> list[tuple[str, str, str]]:
    return _headers(V2) + _headers(V2_1)


def test_both_core_files_exist() -> None:
    assert V2.is_file()
    assert V2_1.is_file(), "V2.1 closes the primitives V2 leaves implicit"


@pytest.mark.parametrize("primitive", AUTHORIZATION_PRIMITIVES)
def test_every_authorization_primitive_has_a_definition(primitive: str, all_headers: list[tuple[str, str, str]]) -> None:
    titles = [title.lower() for kind, _, title in all_headers if kind == "Definition"]
    assert any(primitive in title for title in titles), (
        f"{primitive!r} is used by the authorization rule but has no `### Definition` header"
    )


@pytest.mark.parametrize("quantity", SEPARATED_QUANTITIES)
def test_confidence_and_utility_are_named_and_separated(quantity: str) -> None:
    text = _read(V2_1).lower()
    assert quantity in text, f"{quantity!r} is never named, so it cannot be shown not to grant authority"


def test_definition_numbers_are_unique_across_both_files(all_headers: list[tuple[str, str, str]]) -> None:
    numbers = [number for kind, number, _ in all_headers if kind == "Definition"]
    duplicates = sorted({n for n in numbers if numbers.count(n) > 1}, key=float)
    assert not duplicates, f"duplicate Definition numbers across V2 and V2.1: {duplicates}"


def test_theorem_and_proposition_numbers_share_one_sequence(all_headers: list[tuple[str, str, str]]) -> None:
    """V2 numbers Theorems and Propositions from a single counter; V2.1 must continue it."""

    numbers = [number for kind, number, _ in all_headers if kind in {"Theorem", "Proposition"}]
    duplicates = sorted({n for n in numbers if numbers.count(n) > 1}, key=float)
    assert not duplicates, f"duplicate Theorem/Proposition numbers across V2 and V2.1: {duplicates}"
    assert sorted(int(n) for n in numbers) == list(range(1, len(numbers) + 1)), (
        "the shared Theorem/Proposition sequence has a gap or restart"
    )


def test_corollaries_hang_off_an_existing_result(all_headers: list[tuple[str, str, str]]) -> None:
    parents = {number for kind, number, _ in all_headers if kind in {"Theorem", "Proposition"}}
    for kind, number, _ in all_headers:
        if kind == "Corollary":
            assert number.split(".")[0] in parents, f"Corollary {number} has no parent result"


def test_v2_1_declares_supersession_and_its_one_correction() -> None:
    text = _read(V2_1)
    assert "**Supersedes:** `FORMAL_CORE_V2.md`" in text
    assert "CLOSED_V2_1" in text
    # The correction has to be labelled as a correction, not folded in as an addition.
    assert "Correction to V2" in text


def test_v2_1_does_not_move_the_two_cannot_check_terminals() -> None:
    """Closing internal primitives is not evidence about novelty or a baseline."""

    text = _read(V2_1)
    assert "P8_NOVELTY = CANNOT_CHECK_UNTIL_LITERATURE_CLOSURE" in text
    assert "P8_SEPARATE_PAPER = CANNOT_CHECK_UNTIL_STRONG_BASELINE_DISCRIMINATOR" in text


def test_the_primitive_check_is_not_vacuous(all_headers: list[tuple[str, str, str]]) -> None:
    """No alarm, and no free pass.

    A term with no definition anywhere must be reported missing. Without this the coverage
    test above would pass on any file that happened to contain the word.
    """

    titles = [title.lower() for kind, _, title in all_headers if kind == "Definition"]
    assert not any("expected utility" in title for title in titles)
    assert any("blocker" in title for title in titles)
    assert len(titles) >= 20, f"only {len(titles)} definitions parsed; the header regex has drifted"
