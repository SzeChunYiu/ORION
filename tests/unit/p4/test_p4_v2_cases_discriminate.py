"""The proposed V2 insufficient-evidence cases, and the freeze they must not disturb.

V1's three `INSUFFICIENT_EVIDENCE` cases state their verdict, which is the simplest
available explanation for `correct_cannot_check_rate` sitting at 1.0 for all eleven
panel systems. V1 is frozen and stays exactly as it is: the V2 campaign already ran
against it, and editing a manifest that recorded results would rewrite the record
rather than improve it.

So the repair lives in a new file, marked `PROPOSED_NOT_EXECUTED`, and these tests
hold it to the bar V1 failed:

- no case may state its own verdict;
- the repaired cases must keep V1's evidential facts, since the fix is subtraction,
  not rewriting;
- the new cases must be hard in the way that matters -- evidence that survives
  surface checks and fails on scope -- because repairing the leak alone leaves
  cases whose thin evidence is itself a giveaway.

Nothing here claims a result. No campaign has been run against these cases, and a
proposal that quietly acquired a measured outcome would be the same category error
as a leaking case.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P4 = ROOT / "papers" / "orion-14-verified-scientific-discovery"
CHECKER = P4 / "protocol" / "check_verdict_leak_v1.py"
V1 = P4 / "protocol" / "ATTACK_MANIFEST_V1.jsonl"
V2 = P4 / "protocol" / "INSUFFICIENT_EVIDENCE_CASES_V2_PROPOSED.jsonl"

#: Surface cues a citation-matching system can act on without judging scope.
SURFACE_CUES = ("n=5", "no peer review", "preprint", "no confidence intervals")


def _checker():
    spec = importlib.util.spec_from_file_location("verdict_leak_v2", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_no_proposed_case_states_its_verdict() -> None:
    checker = _checker()
    for case in _rows(V2):
        assert checker.leaks_in(case) == [], (
            f"{case['case_id']} states its verdict; it would be scored by reading"
        )


def test_the_repaired_cases_kept_v1_evidence_and_only_dropped_the_verdict() -> None:
    """Subtraction, verified against V1 rather than asserted.

    A repair that rewrote the evidence would change what the case tests. Each
    repaired case must still be a prefix of its V1 original.
    """

    v1 = {
        c["candidate_visible"]["claim_text"]: c["candidate_visible"]["evidence_text"]
        for c in _rows(V1)
        if c["attack_family"] == "INSUFFICIENT_EVIDENCE"
    }
    repaired = [c for c in _rows(V2) if c["origin"] == "repaired_from_v1"]
    assert len(repaired) == 3, f"expected 3 repaired cases, got {len(repaired)}"

    for case in repaired:
        claim = case["candidate_visible"]["claim_text"]
        assert claim in v1, f"{case['case_id']} claim does not match any V1 case"
        original, kept = v1[claim], case["candidate_visible"]["evidence_text"]
        assert original.startswith(kept.rstrip()), (
            f"{case['case_id']} rewrote the evidence rather than trimming it; the repair "
            f"must preserve what V1 asked the system to weigh"
        )
        assert len(kept) < len(original), f"{case['case_id']} dropped nothing"


def test_the_new_cases_are_hard_in_the_way_that_matters() -> None:
    """Repairing the leak is not enough on its own.

    A case whose evidence is visibly thin can still be answered from surface cues.
    The discriminating cases must present evidence that passes a quality screen --
    peer review, intervals, significance tests or quantitative evaluation -- and fail
    on scope instead. The screen is a disjunction on purpose: requiring the words
    "peer reviewed" would have forced a false statement about a real publication into
    a gold case, since one of these cites a venue that is not peer reviewed.
    """

    new = [c for c in _rows(V2) if c["origin"] == "new_discriminating"]
    assert len(new) == 3, f"expected 3 discriminating cases, got {len(new)}"

    for case in new:
        evidence = case["candidate_visible"]["evidence_text"].lower()
        assert not any(cue in evidence for cue in SURFACE_CUES), (
            f"{case['case_id']} leans on a surface cue {SURFACE_CUES}; a system could "
            f"answer it without reasoning about scope"
        )
        # The requirement is that the evidence survives a quality screen, not that it
        # carries one particular label. Case 006 cites Bricken et al., which is not a
        # peer-reviewed venue; asserting that it were would put a false statement about
        # a real publication into a gold case to satisfy a test.
        quality_signals = (
            "peer-reviewed",
            "peer reviewed",
            "confidence interval",
            "statistically significant",
            "quantitative",
            "interpretability evaluation",
        )
        assert any(signal in evidence for signal in quality_signals), (
            f"{case['case_id']}: the evidence presents no quality signal at all, so it can "
            f"be declined on surface grounds and does not isolate scope reasoning"
        )
        assert case["insufficiency_subtype"].startswith("scope_mismatch"), (
            f"{case['case_id']} is not a scope mismatch; that is the mechanism these cases "
            f"exist to isolate"
        )
        assert case["expected_authority_terminal"] == "CANNOT_CHECK"


def test_nothing_here_claims_a_result() -> None:
    """A proposal must not acquire an outcome by sitting in the repository."""

    for case in _rows(V2):
        assert case["status"] == "PROPOSED_NOT_EXECUTED", (
            f"{case['case_id']} is no longer marked as unexecuted. If a campaign has run "
            f"these cases, the result belongs in an evidence artifact with its own "
            f"protocol identity, not in the case file."
        )
        assert "measured" not in case and "observed_terminal" not in case


def test_v1_is_untouched() -> None:
    """The frozen manifest keeps its defect on the record.

    The V2 campaign ran against V1. Editing it now would rewrite what was measured,
    and the leak is evidence about the published result -- it should stay visible.
    """

    checker = _checker()
    leaking = [c["case_id"] for c in _rows(V1) if checker.leaks_in(c)]
    assert sorted(leaking) == [
        "P4-INSUFFICIENT_EVIDENCE-001",
        "P4-INSUFFICIENT_EVIDENCE-002",
        "P4-INSUFFICIENT_EVIDENCE-003",
    ], (
        f"V1's leaking cases changed to {sorted(leaking)}. V1 is frozen and was the subject "
        f"of the published campaign; repairs belong in the V2 proposal file."
    )
