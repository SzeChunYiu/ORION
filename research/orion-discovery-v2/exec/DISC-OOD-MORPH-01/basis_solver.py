"""Registered-basis solver for DISC-OOD-MORPH-01.

AUTHORING ORDER MATTERS AND IS PART OF THE RESULT. This module was written
FIRST, before any world was authored, and its coverage predicate is derived
only from the text of section 3 of
KNOWLEDGE_WEB_NAVIGATION_PROOF_ECONOMY_AND_SELF_APPLICATION_V1.md
(vendored beside this file as SECTION_3_SOURCE.md, blob e5816b1d, verified
byte-identical to the branch copy).

If the generator's worlds and the solver's predicate were authored from one
shared table in the author's head, "recovery" would be true by construction and
no probe over solver-visible features could detect it. Deriving the predicate
from the spec's own words, before the worlds exist, is the control for that.

The solver is a LEXICAL EXPRESSIVENESS PROXY, not a semantic reasoner. It asks:
do the words of the move fall under the terms section 3 uses to enumerate each
space? This is a real limitation and is reported as one.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "SECTION_3_SOURCE.md"

STOP = {
    "the", "and", "or", "of", "in", "which", "can", "be", "a", "an", "is", "to",
    "it", "its", "itself", "whether", "may", "who", "what", "for", "on", "with",
    "as", "at", "by", "from", "that", "this", "these", "those", "space", "are",
    "worth", "own", "result", "candidates", "candidate", "not",
}


def _stem(w: str) -> str:
    """Light, INVERTIBLE-BY-AGREEMENT plural strip.

    DEFECT FOUND AND FIXED BEFORE ANY RUN: the first version stripped multi-char
    suffixes, so the spec's plural `counterexamples` stemmed to `counterexampl`
    while a move's singular `counterexample` stemmed to itself. The two never
    matched, and every proof/evidence term was silently dead. A solver whose
    coverage terms cannot fire would have manufactured "recovery" everywhere.
    The rule below maps singular and plural to the SAME form for every term
    section 3 actually uses, which is asserted in _assert_stem_agreement().
    """
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def _assert_stem_agreement() -> None:
    """Every coverage term must agree with its singular/plural counterpart."""
    for plural, singular in (("counterexamples", "counterexample"), ("laws", "law"),
                             ("models", "model"), ("mechanisms", "mechanism"),
                             ("measurements", "measurement"), ("objects", "object"),
                             ("variables", "variable"), ("proofs", "proof"),
                             ("constructions", "construction"), ("apparatus", "apparatus")):
        if _stem(plural) != _stem(singular):
            raise RuntimeError(f"stem disagreement: {plural} vs {singular}")


def load_spaces(source: Path = SOURCE) -> dict[str, dict]:
    _assert_stem_agreement()
    """Parse the six spaces and their enumerated coverage terms from section 3."""
    text = source.read_text(encoding="utf-8")
    s = text.index("# 3. Six coupled search spaces")
    e = text.index("# 4. Typed knowledge web")
    sec = text[s:e]
    # The enumerated list ends where the prose resumes. Without this bound the
    # sixth bullet absorbs the paragraphs that follow and acquires 62 coverage
    # terms instead of 6, which would bias every classification toward
    # authority_adoption. Caught by inspecting the parsed term counts.
    cut = sec.find("\nA move in one space")
    if cut == -1:
        raise RuntimeError("could not bound the enumerated list; refusing to guess")
    sec = sec[:cut]
    spaces: dict[str, dict] = {}
    # Each space is a numbered bullet: "N. **Name space** — <enumerated terms>"
    for m in re.finditer(r"^\s*(\d)\.\s+\*\*(.+?)\*\*\s+—\s+(.*?)(?=^\s*\d\.\s+\*\*|\Z)",
                         sec, re.S | re.M):
        idx, name, body = m.group(1), m.group(2), m.group(3)
        key = (name.lower().replace("/", "_").replace(" space", "")
               .replace(" ", "_").strip())
        definition = " ".join(body.split())
        terms = {_stem(w) for w in re.findall(r"[a-z]+", definition.lower())
                 if w not in STOP and len(w) > 2}
        spaces[key] = {"ordinal": int(idx), "name": name.strip(),
                       "definition_verbatim": definition, "coverage_terms": sorted(terms)}
    if len(spaces) != 6:
        raise RuntimeError(f"section 3 parse produced {len(spaces)} spaces, expected 6")
    return spaces


class BasisSolver:
    """Classifies a move into one of the six registered spaces, or abstains.

    threshold: minimum number of distinct spec coverage terms a move must share
    with a space before the solver will claim that space expresses it. It is
    CALIBRATED ON IN-BASIS WORLDS ONLY and frozen before any out-of-basis world
    is run -- a threshold tuned after seeing out-of-basis behaviour would make
    recovery a fitted result rather than a measured one.
    """

    def __init__(self, threshold: int, source: Path = SOURCE):
        self.spaces = load_spaces(source)
        self.threshold = threshold

    def _scores(self, move_text: str) -> dict[str, int]:
        toks = {_stem(w) for w in re.findall(r"[a-z]+", move_text.lower())}
        return {k: len(toks & set(v["coverage_terms"])) for k, v in self.spaces.items()}

    def classify(self, move_text: str) -> dict:
        """Abstaining mode: may return OPEN_MOVE_CLASS_REQUIRED."""
        sc = self._scores(move_text)
        best = max(sc, key=lambda k: (sc[k], -self.spaces[k]["ordinal"]))
        if sc[best] < self.threshold:
            return {"decision": "OPEN_MOVE_CLASS_REQUIRED", "space": None,
                    "score": sc[best], "scores": sc}
        return {"decision": "IN_BASIS", "space": best, "score": sc[best], "scores": sc}

    def classify_forced(self, move_text: str) -> dict:
        """Forced-choice mode: no abstain. Measures false certainty directly --
        what the basis returns when it is not permitted to say 'I cannot'."""
        sc = self._scores(move_text)
        best = max(sc, key=lambda k: (sc[k], -self.spaces[k]["ordinal"]))
        return {"decision": "IN_BASIS", "space": best, "score": sc[best], "scores": sc}
