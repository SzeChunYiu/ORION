#!/usr/bin/env python3
"""Fail closed on unearned P9/P10 claims in P1--P8 manuscripts.

This is a programme-boundary guard, not a novelty or empirical evaluator.  It
only rejects a sentence that both names the future P9/P10 direction and uses
assertive result language.  Explicitly bounded language (``CANNOT_CHECK``,
future-work statements, or an explicit non-claim) remains permitted.

Exit codes: 0 clean, 1 boundary violations, 2 harness/IO errors.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATHS = (
    ROOT / "papers" / "paper-01-recursive-epistemic-reconstruction" / "manuscript",
    ROOT / "papers" / "paper-02-open-world-scientific-discovery" / "manuscript",
    ROOT / "papers" / "paper-03-global-knowledge-portrait" / "manuscript",
    ROOT / "papers" / "paper-04-verified-scientific-discovery" / "manuscript",
    ROOT / "papers" / "paper-05-self-orion" / "manuscript",
    ROOT / "papers" / "candidates" / "paper-06-formal-epistemic-structures-and-mechanics" / "submission",
    ROOT / "papers" / "candidates" / "paper-07-epistemic-navigation-open-worlds" / "submission",
    ROOT / "papers" / "candidates" / "paper-08-epistemic-authority-autonomous-science" / "submission",
)

_DIRECTION_RE = re.compile(
    r"\b(?:P9|P10|paper\s+(?:9|10))\b|"
    r"\b(?:structural\s+learning|learned\s+scientific\s+method|"
    r"method\s+invention|invented\s+method(?:s)?)\b",
    re.IGNORECASE,
)
_ASSERTION_RE = re.compile(
    r"\b(?:we|our\s+(?:method|model|system|results?))\s+"
    r"(?:show|demonstrat|establish|achiev|improv|outperform|invent|learn|"
    r"discover|find|produce|generate|validat|confirm|attain|yield)",
    re.IGNORECASE,
)
_RESULT_RE = re.compile(
    r"\b(?:achiev(?:es|ed|ing)?|demonstrat(?:es|ed|ing)?|"
    r"outperform(?:s|ed|ing)?|improv(?:es|ed|ing)?|"
    r"empirical(?:ly)?|performance|accuracy|benchmark|results?|"
    r"invent(?:s|ed|ing)?|discover(?:s|ed|ing)?|generat(?:es|ed|ing)?)\b",
    re.IGNORECASE,
)
_BOUNDARY_RE = re.compile(
    r"\b(?:CANNOT_CHECK|cannot\s+check|do\s+not\s+claim|does\s+not\s+claim|"
    r"not\s+(?:yet\s+)?(?:claim(?:ed)?|established|demonstrated|evaluated)|"
    r"future\s+work|planned|prospective|will\s+(?:evaluate|test|measure)|"
    r"requires?\s+(?:future|independent|prospective|empirical)\s+(?:evaluation|"
    r"experiments?|evidence)|before\s+(?:any\s+)?experiments?)\b",
    re.IGNORECASE,
)


class HarnessError(RuntimeError):
    pass


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HarnessError(f"cannot read {path}: {exc}") from exc


def _sentences(text: str) -> list[str]:
    # This guard is deliberately conservative: source-level punctuation is
    # enough to identify a reviewable sentence, while avoiding a LaTeX parser.
    text = re.sub(r"%[^\n]*", " ", text)
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _files(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if not path.exists():
            raise HarnessError(f"scan path does not exist: {path}")
        if path.is_file():
            found.append(path)
        else:
            found.extend(item for item in path.rglob("*") if item.suffix.lower() in {".tex", ".md"})
    return sorted(set(found))


def violations(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in _files(paths):
        for line_no, sentence in enumerate(_sentences(_read(path)), 1):
            if not _DIRECTION_RE.search(sentence):
                continue
            if _BOUNDARY_RE.search(sentence):
                continue
            # Requiring both direction and result vocabulary avoids treating a
            # neutral bridge heading or a historical protocol reference as a
            # result claim.  First-person/result-subject language is stronger
            # still, and catches the usual overclaim shape.
            if _ASSERTION_RE.search(sentence) or _RESULT_RE.search(sentence):
                findings.append(
                    f"P9_P10_OVERCLAIM: {path}:{line_no}: {sentence}"
                )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", type=Path, dest="paths")
    args = parser.parse_args(argv)
    try:
        findings = violations(args.paths or list(DEFAULT_PATHS))
    except HarnessError as exc:
        print(f"P9/P10 CLAIM-BOUNDARY HARNESS ERROR: {exc}", file=sys.stderr)
        print("could not check the boundary; this is not a pass", file=sys.stderr)
        return 2
    if findings:
        for finding in findings:
            print(f"VIOLATION {finding}", file=sys.stderr)
        print(f"{len(findings)} P9/P10 claim-boundary violation(s).", file=sys.stderr)
        return 1
    print("P9/P10 claim boundary clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
