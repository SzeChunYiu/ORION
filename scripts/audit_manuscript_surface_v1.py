"""Surface audit for manuscript prose: repeated sentences and conflicting numbers.

Two defect classes that survive every check the programme already runs, because
both are locally well-formed. Neither breaks a build, a binding or a test.

**Repeated sentences.** An edit adds a revised sentence without deleting the one
it revises, so the manuscript says the same thing twice. Found in ORION-22 §1 and
§9 (similarities 0.74 and 0.91).

**Conflicting numbers.** The same noun takes two different values in one
document. Found in ORION-18's abstract, which described "39,936 exact authority
states" three lines above "3,072 distinct exact authority states … 39,936
evaluations", having itself written that the distinction matters.

Both were found by hand first and only then automated, which is the reason this
file exists rather than a scan built from the definitions. Two earlier splitters
reported the ORION-22 file *clean*:

- a paragraph-level comparison, because the duplication is inside one paragraph;
- a line-by-line sentence split, because markdown emphasis (``…spent.**``) hides
  the sentence boundary and the source is hard-wrapped, so one sentence spans two
  lines.

So this audit joins paragraphs before splitting, strips emphasis first, and —
most importantly — **carries a control**. ``--self-test`` builds a document with a
known duplicate and a known number conflict and requires the audit to find both.
A scan that reports "clean" without being able to demonstrate it can still fire
is worth nothing; that verdict was believed twice here before the control existed.

Legitimate repetition exists and is carried in a baseline rather than suppressed
by loosening the threshold: restating a technical axiom two sections later is
correct writing, and rewording it to satisfy a similarity cutoff makes the paper
worse.

Exit codes
----------
0   no finding outside the baseline
2   a new repeated sentence or number conflict, or a stale baseline entry
3   CANNOT_CHECK -- the audit could not run, which is not the same as clean
"""

from __future__ import annotations

import argparse
import difflib
import itertools
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "papers" / "MANUSCRIPT_SURFACE_BASELINE_V1.json"

SIMILARITY = 0.70
MIN_SENTENCE = 80

EMPHASIS = re.compile(r"\*\*|\*|`|_")
FENCED = re.compile(r"```.*?```", re.S)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
STOPWORDS = {"the","and","for","with","that","this","are","was","were","its","per","its","over","than","from","into","under","each"}
NUMBERED = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d{2,6})\s+((?:[a-z][\w-]*\s+){0,3}[a-z][\w-]*)")


class CannotCheck(Exception):
    """The audit could not run. Distinct from a clean result."""


def sentences(text: str) -> list[str]:
    """Substantive sentences, robust to hard wrapping and markdown emphasis."""
    text = FENCED.sub("", text)
    text = EMPHASIS.sub("", text)
    out: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        block = " ".join(block.split())  # undo hard wrapping
        if block.startswith(("#", "|", ">")):
            continue
        for sentence in SENTENCE_SPLIT.split(block):
            sentence = sentence.strip().lstrip("-* ")
            if len(sentence) >= MIN_SENTENCE:
                out.append(sentence)
    return out


def repeated_sentences(text: str) -> list[dict]:
    found = []
    items = sentences(text)
    for a, b in itertools.combinations(range(len(items)), 2):
        ratio = difflib.SequenceMatcher(None, items[a], items[b]).ratio()
        if ratio >= SIMILARITY:
            found.append({"kind": "repeated_sentence", "similarity": round(ratio, 3),
                          "a": items[a][:200], "b": items[b][:200]})
    return found


def conflicting_numbers(text: str) -> list[dict]:
    """A noun phrase that takes more than one value in the same document."""
    text = EMPHASIS.sub("", text)
    flat = " ".join(text.split())
    by_noun: dict[str, set[str]] = {}
    for match in NUMBERED.finditer(flat):
        words = match.group(2).split()
        # Index every bigram in the captured phrase, not just its first or last
        # pair. A leading adjective ("3,072 *distinct exact* authority states")
        # or a trailing verb ("39,936 authority states *replayed* ...") shifts a
        # fixed-position key and the conflict goes unseen; the shared bigram does
        # not move.
        for i in range(len(words) - 1):
            key = f"{words[i]} {words[i + 1]}"
            if len(words[i]) < 3 or len(words[i + 1]) < 3:
                continue
            if key.split()[0] in STOPWORDS or key.split()[1] in STOPWORDS:
                continue
            by_noun.setdefault(key, set()).add(match.group(1))
    return [
        {"kind": "number_conflict", "noun": key, "values": sorted(values)}
        for key, values in sorted(by_noun.items())
        if len(values) > 1
    ]


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def fingerprint(finding: dict) -> str:
    if finding["kind"] == "repeated_sentence":
        return "repeated_sentence::" + finding["a"][:60]
    return f"number_conflict::{finding['noun']}::{','.join(finding['values'])}"


def audit(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CannotCheck(f"cannot read {path}: {exc}") from exc
    findings = repeated_sentences(text) + conflicting_numbers(text)
    for finding in findings:
        finding["path"] = path.as_posix()
    return findings


def self_test() -> None:
    """The control. A scan that cannot demonstrate it fires is not evidence."""
    probe = (
        "# Probe\n\n"
        "These results sharpen the motivation: adaptive inference is crowded and the\n"
        "novel discriminator must be where the resource can be spent.\n"
        "These results strengthen, rather than weaken, the motivation: adaptive "
        "inference is crowded and the novel discriminator must be where the resource "
        "can be spent.\n\n"
        "The model exhausts 39,936 authority states under the frozen protocol here.\n"
        "The model covers 3,072 authority states replayed thirteen times over.\n"
    )
    reps = repeated_sentences(probe)
    nums = conflicting_numbers(probe)
    if not reps:
        raise CannotCheck(
            "self-test: the audit cannot see a planted repeated sentence; a clean "
            "verdict from it would be meaningless"
        )
    if not nums:
        raise CannotCheck(
            "self-test: the audit cannot see a planted number conflict; a clean "
            "verdict from it would be meaningless"
        )


def load_baseline() -> dict:
    if not BASELINE.is_file():
        return {"entries": {}}
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise CannotCheck(f"baseline is malformed: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path,
                        help="manuscript files; defaults to the baseline's own targets")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--self-test-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        self_test()
        if args.self_test_only:
            print("SELF_TEST_PASSED: the audit fires on a planted duplicate and conflict")
            return 0
        baseline = load_baseline()
        targets = args.paths or [ROOT / p for p in baseline.get("targets", [])]
        # Accept relative paths from any cwd inside the repository.
        targets = [p if p.is_absolute() else (ROOT / p) for p in targets]
        targets = [p.resolve() for p in targets if p.is_file()]
        if not targets:
            raise CannotCheck("no manuscript targets resolved; nothing was audited")
        findings: list[dict] = []
        for path in targets:
            findings.extend(audit(path))
    except CannotCheck as exc:
        print(f"CANNOT_CHECK: {exc}", file=sys.stderr)
        return 3

    known = set(baseline.get("entries", {}))
    seen = {fingerprint(f) for f in findings}
    new = [f for f in findings if fingerprint(f) not in known]
    stale = sorted(known - seen)

    report = {
        "schema": "orion.manuscript-surface-audit.v1",
        "scientific_authority_delta": "NONE",
        "audited": [_rel(p) for p in targets],
        "findings": findings,
        "new": new,
        "stale_baseline_entries": stale,
    }
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")

    print(f"audited {len(targets)} manuscript(s); {len(findings)} finding(s), "
          f"{len(new)} outside the baseline, {len(stale)} stale baseline entr(ies)")
    for finding in new:
        print(f"  NEW {finding['kind']} in {finding['path']}: "
              f"{finding.get('noun') or finding.get('a','')[:90]}", file=sys.stderr)
    for entry in stale:
        print(f"  STALE baseline entry no longer reproduces: {entry}", file=sys.stderr)
    return 2 if (new or stale) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
