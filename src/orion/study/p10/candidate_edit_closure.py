"""Machine-check a candidate edit against P10's frozen method-language closure.

P10's central risk is *method-language escalation*: a controller that solves a
case by quietly widening its own vocabulary and then reports the result as if it
had stayed inside the method it was evaluated on. The paper calls the honest
version of that an outside-closure method expansion (OCME), and it is only
admissible when it is declared and independently witnessed. The dishonest
version is a false closure -- an edit that uses a token the frozen grammar does
not contain while claiming to be inside it.

Nothing here decides whether an expansion is *justified*. That is H4's job and it
needs external witnesses. This decides the prior question, which is mechanical:
**is this edit expressible in the frozen grammar at all, and does its own
declaration match the answer?**

The grammar is read from the live enums in :mod:`orion.study.p10.a0_control`
rather than restated, so the check cannot drift from the vocabulary it is
supposed to be checking. If someone adds a `ProposalKind`, this module starts
accepting it in the same commit -- which is correct, because at that point the
grammar genuinely did change and the freeze digest changes with it.

Exit codes: 0 PASS, 2 false closure (out-of-grammar token claimed in-closure),
3 undeclared expansion, 4 declared expansion that names no new token,
5 malformed -- could not check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orion.study.p10.a0_control import ControllerArm, ProposalKind, Responsibility

__all__ = [
    "EXIT_CANNOT_CHECK",
    "EXIT_EXPANSION_UNNAMED",
    "EXIT_FALSE_CLOSURE",
    "EXIT_PASS",
    "EXIT_UNDECLARED_EXPANSION",
    "IN_CLOSURE",
    "OUTSIDE_CLOSURE",
    "ClosureVerdict",
    "check_candidate_edit",
    "frozen_grammar",
    "grammar_digest",
    "main",
]

IN_CLOSURE = "IN_CLOSURE"
OUTSIDE_CLOSURE = "OUTSIDE_CLOSURE"

EXIT_PASS = 0
EXIT_FALSE_CLOSURE = 2
EXIT_UNDECLARED_EXPANSION = 3
EXIT_EXPANSION_UNNAMED = 4
EXIT_CANNOT_CHECK = 5


def frozen_grammar() -> dict[str, tuple[str, ...]]:
    """The frozen vocabulary, read from the live enums, never restated."""

    return {
        "responsibility": tuple(sorted(m.value for m in Responsibility)),
        "proposal_kind": tuple(sorted(m.value for m in ProposalKind)),
        "controller_arm": tuple(sorted(m.value for m in ControllerArm)),
    }


def grammar_digest(grammar: dict[str, tuple[str, ...]] | None = None) -> str:
    """A digest over the vocabulary, so a silent widening is visible."""

    g = grammar or frozen_grammar()
    # Members are sorted, not just keys: a grammar is a set, so reordering an
    # enum declaration must not read as a grammar change.
    payload = json.dumps({k: sorted(v) for k, v in sorted(g.items())}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ClosureVerdict:
    exit_code: int
    terminal: str
    position: str | None = None
    out_of_grammar: tuple[tuple[str, str], ...] = field(default=())
    problems: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


_FIELD_TO_AXIS = {
    "responsibility": "responsibility",
    "proposal_kind": "proposal_kind",
    "kind": "proposal_kind",
    "controller_arm": "controller_arm",
    "arm": "controller_arm",
}


def check_candidate_edit(edit: Any, grammar: dict[str, tuple[str, ...]] | None = None) -> ClosureVerdict:
    """Decide whether one candidate edit is expressible in the frozen grammar.

    ``edit`` must declare ``declared_position`` (IN_CLOSURE or OUTSIDE_CLOSURE)
    and may carry any of the grammar-bearing fields. An edit that declares
    OUTSIDE_CLOSURE must also name the token it needs, because an expansion
    nobody can name cannot be witnessed.
    """

    g = grammar or frozen_grammar()
    if not isinstance(edit, dict):
        return ClosureVerdict(EXIT_CANNOT_CHECK, "P10_CLOSURE_CANNOT_CHECK", None, (), ("edit is not an object",))

    declared = edit.get("declared_position")
    if declared not in {IN_CLOSURE, OUTSIDE_CLOSURE}:
        return ClosureVerdict(
            EXIT_CANNOT_CHECK,
            "P10_CLOSURE_CANNOT_CHECK",
            None,
            (),
            (f"declared_position {declared!r} is neither {IN_CLOSURE} nor {OUTSIDE_CLOSURE}",),
        )

    offending: list[tuple[str, str]] = []
    for name, value in edit.items():
        axis = _FIELD_TO_AXIS.get(name)
        if axis is None or value is None:
            continue
        if not isinstance(value, str):
            return ClosureVerdict(
                EXIT_CANNOT_CHECK, "P10_CLOSURE_CANNOT_CHECK", None, (), (f"{name} is not a string",)
            )
        if value not in g[axis]:
            offending.append((axis, value))

    actual = OUTSIDE_CLOSURE if offending else IN_CLOSURE
    tokens = tuple(sorted(set(offending)))

    if actual == OUTSIDE_CLOSURE and declared == IN_CLOSURE:
        return ClosureVerdict(
            EXIT_FALSE_CLOSURE,
            "P10_FALSE_CLOSURE",
            actual,
            tokens,
            tuple(
                f"{axis} {value!r} is not in the frozen grammar, but the edit claims {IN_CLOSURE}"
                for axis, value in tokens
            ),
        )
    if actual == OUTSIDE_CLOSURE and declared == OUTSIDE_CLOSURE:
        named = edit.get("expansion_tokens")
        if not isinstance(named, list) or not named:
            return ClosureVerdict(
                EXIT_EXPANSION_UNNAMED,
                "P10_EXPANSION_UNNAMED",
                actual,
                tokens,
                ("an expansion that names no new token cannot be witnessed",),
            )
        missing = sorted({v for _, v in tokens} - set(map(str, named)))
        if missing:
            return ClosureVerdict(
                EXIT_EXPANSION_UNNAMED,
                "P10_EXPANSION_UNNAMED",
                actual,
                tokens,
                (f"expansion_tokens omits {missing}",),
            )
        return ClosureVerdict(EXIT_PASS, "P10_DECLARED_EXPANSION", actual, tokens)
    if actual == IN_CLOSURE and declared == OUTSIDE_CLOSURE:
        return ClosureVerdict(
            EXIT_UNDECLARED_EXPANSION,
            "P10_SPURIOUS_EXPANSION",
            actual,
            (),
            ("the edit declares an expansion but every token is already in the frozen grammar",),
        )
    return ClosureVerdict(EXIT_PASS, "P10_IN_CLOSURE", actual, ())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edits", type=Path, help="JSON list of candidate edits")
    args = parser.parse_args(argv)

    g = frozen_grammar()
    print(f"frozen grammar digest: {grammar_digest(g)}")
    for axis, members in g.items():
        print(f"  {axis}: {len(members)} -> {', '.join(members)}")
    if args.edits is None:
        return EXIT_PASS

    try:
        edits = json.loads(args.edits.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"P10_CLOSURE_CANNOT_CHECK: {error}", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    if not isinstance(edits, list):
        print("P10_CLOSURE_CANNOT_CHECK: edits is not a list", file=sys.stderr)
        return EXIT_CANNOT_CHECK

    worst = EXIT_PASS
    for index, edit in enumerate(edits):
        verdict = check_candidate_edit(edit, g)
        print(f"  edit[{index}]: {verdict.terminal} position={verdict.position}")
        for problem in verdict.problems:
            print(f"    {problem}", file=sys.stderr)
        worst = max(worst, verdict.exit_code)
    return worst


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
