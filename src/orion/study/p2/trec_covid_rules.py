"""NIST's TREC-COVID evaluation rules, as refusals rather than prose.

TREC-COVID ran in five rounds over a corpus that changed underneath it. Three
NIST rules follow from that, and all three are easy to violate by accident while
producing numbers that look entirely reasonable:

**Residual collection.** Every round was evaluated residually: a run could not
contain documents already judged in earlier rounds. A system that returns a
previously-judged document is not scored generously, it is out of protocol. The
cumulative qrels define what "already judged" means for each round.

**Chronological qrels.** Round X's chronological file holds a judgment for every
(topic, docid) pair where the topic was used in Round X, the docid was valid in
Round X, and the pair was judged in *any* round. So a Round-5 qrels row can carry
a judgment made in Round 1.

**Rejudgment.** Documents that changed materially -- a new title, an abstract or
a PDF appearing -- were re-judged, so the same (topic, docid) pair can carry
different judgments in different rounds. Picking the wrong one silently changes
the answer.

The rule with the sharpest edge is the one about comparison. NIST states that a
merged Round 1+2 qrels can be built, but that scores computed from it may not be
compared against Round 1 or Round 2 run scores. Cross-round comparison is only
valid on a common topic subset. A pipeline that trains on early rounds and
evaluates the full topic set against late qrels produces a number that means
nothing, and nothing about the number looks wrong.

This module turns those into computations that fail closed, so a P2 run cannot
quietly be out of protocol.

Exit codes: 0 PASS, 2 residual violation, 3 invalid cross-round comparison,
4 rejudgment ambiguity resolved without a rule, 5 malformed input.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

__all__ = [
    "EXIT_CANNOT_CHECK",
    "EXIT_CROSS_ROUND",
    "EXIT_PASS",
    "EXIT_REJUDGMENT",
    "EXIT_RESIDUAL",
    "Judgment",
    "RuleVerdict",
    "check_cross_round_comparison",
    "check_residual_run",
    "resolve_rejudged",
    "main",
]

EXIT_PASS = 0
EXIT_RESIDUAL = 2
EXIT_CROSS_ROUND = 3
EXIT_REJUDGMENT = 4
EXIT_CANNOT_CHECK = 5


@dataclass(frozen=True)
class Judgment:
    """One qrels row. ``round_id`` is NIST's judgment round, e.g. '4.5'."""

    topic: str
    round_id: str
    docid: str
    label: int


@dataclass(frozen=True)
class RuleVerdict:
    exit_code: int
    terminal: str
    problems: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def _round_key(round_id: str) -> float:
    """NIST rounds are 0.5-stepped strings; order them numerically, not lexically."""

    try:
        return float(round_id)
    except (TypeError, ValueError) as error:  # pragma: no cover - guarded by callers
        raise ValueError(f"unorderable judgment round {round_id!r}") from error


def check_residual_run(
    run: Mapping[str, Sequence[str]],
    previously_judged: Mapping[str, Iterable[str]],
) -> RuleVerdict:
    """A residual run must not return any document already judged for that topic.

    ``run`` maps topic -> ranked docids. ``previously_judged`` maps topic -> the
    documents judged in earlier rounds, i.e. the cumulative qrels.
    """

    if not isinstance(run, Mapping) or not isinstance(previously_judged, Mapping):
        return RuleVerdict(EXIT_CANNOT_CHECK, "TREC_RESIDUAL_CANNOT_CHECK", ("run or judged set is not a mapping",))
    if not run:
        return RuleVerdict(EXIT_CANNOT_CHECK, "TREC_RESIDUAL_CANNOT_CHECK", ("run is empty",))

    seen = {topic: set(docs) for topic, docs in previously_judged.items()}
    problems: list[str] = []
    for topic, docids in run.items():
        if not isinstance(docids, Sequence) or isinstance(docids, (str, bytes)):
            return RuleVerdict(
                EXIT_CANNOT_CHECK, "TREC_RESIDUAL_CANNOT_CHECK", (f"topic {topic}: run is not a sequence of docids",)
            )
        already = seen.get(topic, set())
        offenders = [d for d in docids if d in already]
        if offenders:
            problems.append(
                f"topic {topic}: {len(offenders)} previously judged document(s) returned "
                f"(first: {offenders[0]}); a residual run may not contain them"
            )
        duplicates = len(docids) - len(set(docids))
        if duplicates:
            problems.append(f"topic {topic}: {duplicates} duplicate docid(s) in the ranking")

    if problems:
        return RuleVerdict(EXIT_RESIDUAL, "TREC_RESIDUAL_FAIL", tuple(problems))
    return RuleVerdict(EXIT_PASS, "TREC_RESIDUAL_PASS")


def check_cross_round_comparison(
    left_topics: Iterable[str],
    right_topics: Iterable[str],
    *,
    left_round: str,
    right_round: str,
    restricted_to_common_subset: bool,
) -> RuleVerdict:
    """Two rounds' scores are comparable only on the topics both rounds used.

    NIST is explicit that a merged qrels may be built but its scores may not be
    compared with either round's own run scores.
    """

    left = set(left_topics)
    right = set(right_topics)
    if not left or not right:
        return RuleVerdict(EXIT_CANNOT_CHECK, "TREC_CROSS_ROUND_CANNOT_CHECK", ("a topic set is empty",))

    common = left & right
    problems: list[str] = []
    if left != right and not restricted_to_common_subset:
        problems.append(
            f"round {left_round} used {len(left)} topics and round {right_round} used {len(right)}; "
            f"only {len(common)} are common. Comparing unrestricted scores across rounds is invalid — "
            "restrict to the common topic subset first"
        )
    if not common:
        problems.append(f"rounds {left_round} and {right_round} share no topics; no valid comparison exists")

    if problems:
        return RuleVerdict(EXIT_CROSS_ROUND, "TREC_CROSS_ROUND_FAIL", tuple(problems))
    return RuleVerdict(EXIT_PASS, "TREC_CROSS_ROUND_PASS")


def resolve_rejudged(
    judgments: Sequence[Judgment],
    *,
    target_round: str,
) -> tuple[dict[tuple[str, str], int], RuleVerdict]:
    """Resolve (topic, docid) pairs that carry more than one judgment.

    The rule is positional, not statistical: use the judgment made in the target
    round when one exists, otherwise the most recent judgment at or before it.
    A pair whose only judgments come from later rounds is not resolvable for this
    round, and is reported rather than guessed.
    """

    try:
        target = _round_key(target_round)
    except ValueError as error:
        return {}, RuleVerdict(EXIT_CANNOT_CHECK, "TREC_REJUDGMENT_CANNOT_CHECK", (str(error),))

    grouped: dict[tuple[str, str], list[Judgment]] = defaultdict(list)
    for item in judgments:
        if not isinstance(item, Judgment):
            return {}, RuleVerdict(EXIT_CANNOT_CHECK, "TREC_REJUDGMENT_CANNOT_CHECK", ("not a Judgment",))
        grouped[(item.topic, item.docid)].append(item)

    resolved: dict[tuple[str, str], int] = {}
    problems: list[str] = []
    for key, items in grouped.items():
        try:
            eligible = [i for i in items if _round_key(i.round_id) <= target]
        except ValueError as error:
            return {}, RuleVerdict(EXIT_CANNOT_CHECK, "TREC_REJUDGMENT_CANNOT_CHECK", (str(error),))
        if not eligible:
            problems.append(
                f"{key[0]}/{key[1]}: judged only after round {target_round}; not resolvable for this round"
            )
            continue
        chosen = max(eligible, key=lambda i: _round_key(i.round_id))
        resolved[key] = chosen.label
        distinct = {i.label for i in eligible}
        if len(distinct) > 1 and len(eligible) > 1:
            # Rejudged with a changed verdict. Resolving it is fine; doing so
            # silently is not, because the denominator moved.
            problems.append(
                f"{key[0]}/{key[1]}: rejudged across rounds {sorted(i.round_id for i in eligible)} "
                f"with labels {sorted(distinct)}; resolved to {chosen.label} from round {chosen.round_id}"
            )

    if problems:
        return resolved, RuleVerdict(EXIT_REJUDGMENT, "TREC_REJUDGMENT_REPORTED", tuple(problems))
    return resolved, RuleVerdict(EXIT_PASS, "TREC_REJUDGMENT_PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin", type=Path, default=Path("papers/paper-02-open-world-scientific-discovery/protocol/P2_TREC_COVID_ROUND5_SOURCE_PIN_V1.json"))
    args = parser.parse_args(argv)
    import json

    try:
        pin = json.loads(args.pin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"TREC_RULES_CANNOT_CHECK: {error}", file=sys.stderr)
        return EXIT_CANNOT_CHECK

    print(f"pinned release: {pin['document_collection']['release']}")
    for entry in pin["pinned_files"]:
        print(f"  {entry['file']:28s} {entry['sha256'][:16]}... {entry['bytes']} bytes")
    print("TREC_RULES_LOADED")
    return EXIT_PASS


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
