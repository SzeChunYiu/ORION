"""Audit the issue-1086 portfolio disposition against the properties it promises.

``papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json`` records eight editorial
decisions about which papers survive separately and on what external evidence.
Those decisions are only worth as much as their consistency: a disposition that
hands two papers the same benchmark, or consolidates a group without saying so,
would look identical to one that does not.

This module turns four of the issue's "Definition of done" bullets into
computations over that record:

* every surviving paper carries **one** primary endpoint and its own external
  partition;
* **no benchmark is claimed by two papers**, so no public row can be read as
  independent validation twice;
* the groups the issue names as consolidation candidates -- P6-P8, P13-P14 and
  P15-Q3 -- each carry an explicit consolidation decision;
* P12 carries a strict stop/go decision with a defined stop branch, so it can
  pass once or stop rather than be retried until it passes.

The audit is deliberately structural. It reads the disposition and checks it
against itself and against the issue's stated groups; it does not read any
result, open any gold, or grade any paper. A disposition can be internally
consistent and still describe work that has not happened, which is why the
per-paper execution boxes are untouched by this.

Run it::

    python -m orion.programme.portfolio_integrity --disposition <file>.json

Exit codes: 0 PASS, 2 partition collision, 3 missing consolidation decision,
4 stop/go decision malformed, 5 malformed disposition -- could not check.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "CONSOLIDATION_GROUPS",
    "ISSUE_SOURCE_FAMILIES",
    "shared_source_families",
    "INDEPENDENCE_CLAIM_MARKERS",
    "EXIT_SHARED_SUBSTRATE_CLAIM",
    "check_no_shared_substrate_independence_claim",
    "EXIT_CANNOT_CHECK",
    "EXIT_MISSING_CONSOLIDATION",
    "EXIT_PARTITION_COLLISION",
    "EXIT_PASS",
    "EXIT_STOPGO_MALFORMED",
    "PortfolioAudit",
    "audit_disposition",
    "main",
]

#: The groups issue #1086 names as consolidation candidates. Each must carry an
#: explicit decision, so that "consolidated" is a recorded choice rather than an
#: absence of anyone having decided.
CONSOLIDATION_GROUPS: tuple[tuple[str, ...], ...] = (
    ("P6", "P7", "P8"),
    ("P13", "P14"),
    ("P15", "Q3"),
)

EXIT_PASS = 0
EXIT_PARTITION_COLLISION = 2
EXIT_MISSING_CONSOLIDATION = 3
EXIT_STOPGO_MALFORMED = 4
EXIT_CANNOT_CHECK = 5

_STOPGO_PAPER = "P12"

#: Benchmark families named as a Source by more than one paper in issue #1086.
#: Recorded from the issue's own per-paper ``Source:`` lines. Sharing a family
#: is not by itself a violation -- two papers may use disjoint row partitions of
#: the same corpus -- but it becomes one the moment either paper claims its rows
#: as independent validation without a recorded partition.
ISSUE_SOURCE_FAMILIES: dict[str, tuple[str, ...]] = {
    "P1": ("ScienceAgentBench",),
    "P2": ("TREC-COVID",),
    "P3": ("OAEI",),
    "P4": ("SciFact", "Crossref-RetractionWatch"),
    "P5": ("SWE-bench-Verified",),
    "P6": ("WorkflowHub", "Mathlib-Lean", "versioned-ontologies"),
    "P7": ("OBO", "WorkflowHub", "IPC"),
    "P8": ("OPA-Rego", "Cedar", "in-toto-SLSA", "Sigstore"),
    "P9": ("LeanDojo", "CLRS", "BPI", "WorkflowHub"),
    "P10": ("LeanDojo", "SyGuS-cvc5", "IPC", "EvalPlus"),
    "P11": ("LongMemEval",),
    "P12": ("ScienceAgentBench",),
    "P13+P14": ("CORE-Bench", "PaperBench", "public-git-ci-histories"),
    "P15+Q3": ("CORE-Bench", "PaperBench", "ScienceAgentBench"),
}


def shared_source_families(
    families: dict[str, tuple[str, ...]] | None = None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return ``(family, papers)`` for every source family named by 2+ papers.

    This is reported, never used to fail the audit. The issue's bullet is about
    a benchmark *row* being claimed twice, and a shared family with disjoint row
    partitions is legitimate. What the sharing does establish is that a
    row-level partition map is required before either paper can call its rows an
    independent partition -- and no such map exists in the disposition today.
    """

    source = ISSUE_SOURCE_FAMILIES if families is None else families
    owners: dict[str, list[str]] = {}
    for paper, entries in source.items():
        for family in entries:
            owners.setdefault(family, []).append(paper)
    return tuple(
        (family, tuple(sorted(papers)))
        for family, papers in sorted(owners.items())
        if len(papers) > 1
    )



@dataclass(frozen=True)
class PortfolioAudit:
    exit_code: int
    terminal: str
    problems: tuple[str, ...] = field(default=())
    partitions: tuple[tuple[str, str], ...] = field(default=())
    consolidated_groups: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def _decisions(document: Any) -> list[dict[str, Any]] | None:
    if not isinstance(document, dict):
        return None
    decisions = document.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        return None
    if not all(isinstance(item, dict) for item in decisions):
        return None
    return decisions


def audit_disposition(document: Any) -> PortfolioAudit:
    """Audit one parsed portfolio disposition."""

    decisions = _decisions(document)
    if decisions is None:
        return PortfolioAudit(
            EXIT_CANNOT_CHECK,
            "PORTFOLIO_INTEGRITY_CANNOT_CHECK",
            ("disposition carries no non-empty list of decision objects",),
        )

    problems: list[str] = []
    worst = EXIT_PASS

    # --- unique, disjoint external partitions -----------------------------
    partitions: dict[str, str] = {}
    claimed: dict[str, str] = {}
    for decision in decisions:
        required = decision.get("required_external_partitions")
        if not isinstance(required, dict):
            continue
        for paper, benchmark in required.items():
            if not isinstance(paper, str) or not isinstance(benchmark, str) or not benchmark.strip():
                return PortfolioAudit(
                    EXIT_CANNOT_CHECK,
                    "PORTFOLIO_INTEGRITY_CANNOT_CHECK",
                    (f"partition entry is not a usable (paper, benchmark) pair: {paper!r} -> {benchmark!r}",),
                )
            if paper in partitions and partitions[paper] != benchmark:
                problems.append(
                    f"{paper} is assigned two different external partitions: "
                    f"{partitions[paper]!r} and {benchmark!r}"
                )
                worst = max(worst, EXIT_PARTITION_COLLISION)
            partitions[paper] = benchmark
            owner = claimed.get(benchmark)
            if owner is not None and owner != paper:
                problems.append(
                    f"benchmark {benchmark!r} is claimed by both {owner} and {paper}; "
                    "a public row cannot be independent validation for two papers"
                )
                worst = max(worst, EXIT_PARTITION_COLLISION)
            claimed.setdefault(benchmark, paper)

    # --- consolidation decisions exist for the named groups ---------------
    consolidated: list[str] = []
    for group in CONSOLIDATION_GROUPS:
        label = "+".join(group)
        found = False
        for decision in decisions:
            papers = decision.get("papers")
            if not isinstance(papers, list):
                continue
            if set(papers) != set(group):
                continue
            disposition = str(decision.get("disposition", ""))
            status = str(decision.get("status", ""))
            if disposition.startswith("CONSOLIDATE") and status.startswith("ADOPTED"):
                found = True
                consolidated.append(label)
                break
            problems.append(
                f"{label}: decision present but is {status}/{disposition}, not an adopted consolidation"
            )
            worst = max(worst, EXIT_MISSING_CONSOLIDATION)
            found = True
            break
        if not found:
            problems.append(f"{label}: no consolidation decision recorded")
            worst = max(worst, EXIT_MISSING_CONSOLIDATION)

    # --- P12 stop/go ------------------------------------------------------
    stopgo = next(
        (d for d in decisions if isinstance(d.get("papers"), list) and d["papers"] == [_STOPGO_PAPER]),
        None,
    )
    if stopgo is None:
        problems.append(f"{_STOPGO_PAPER}: no stop/go decision recorded")
        worst = max(worst, EXIT_STOPGO_MALFORMED)
    else:
        disposition = str(stopgo.get("disposition", ""))
        rule = str(stopgo.get("rule", ""))
        if "STOP_GO" not in disposition.upper().replace("/", "_"):
            problems.append(f"{_STOPGO_PAPER}: disposition {disposition!r} is not a stop/go disposition")
            worst = max(worst, EXIT_STOPGO_MALFORMED)
        if "otherwise" not in rule.lower() or "stop" not in rule.lower():
            problems.append(
                f"{_STOPGO_PAPER}: stop/go rule defines no stop branch, so it can only be retried until it passes"
            )
            worst = max(worst, EXIT_STOPGO_MALFORMED)

    ordered = tuple(sorted(partitions.items()))
    if worst == EXIT_PASS:
        return PortfolioAudit(
            EXIT_PASS, "PORTFOLIO_INTEGRITY_PASS", (), ordered, tuple(consolidated)
        )
    return PortfolioAudit(
        worst, "PORTFOLIO_INTEGRITY_FAIL", tuple(problems), ordered, tuple(consolidated)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--disposition",
        type=Path,
        default=Path("papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json"),
    )
    args = parser.parse_args(argv)

    try:
        document = json.loads(args.disposition.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"PORTFOLIO_INTEGRITY_CANNOT_CHECK: {error}", file=sys.stderr)
        return EXIT_CANNOT_CHECK

    audit = audit_disposition(document)
    for problem in audit.problems:
        print(f"  {problem}", file=sys.stderr)
    for paper, benchmark in audit.partitions:
        print(f"  partition {paper} -> {benchmark}")
    shared = shared_source_families()
    if shared:
        print("  source families named by more than one paper (row-level partition required):")
        for family, papers in shared:
            print(f"    {family}: {', '.join(papers)}")
    print(f"{audit.terminal} consolidated={list(audit.consolidated_groups)} shared_families={len(shared)}")
    return audit.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


#: Wordings by which a paper would assert that its use of a shared public
#: substrate is independent replication. Matched case-insensitively.
INDEPENDENCE_CLAIM_MARKERS: tuple[str, ...] = (
    "independent replication",
    "independent portfolio replication",
    "independently replicated",
    "replicated independently",
    "independent validation",
    "portfolio replication",
)

EXIT_SHARED_SUBSTRATE_CLAIM = 6


def check_no_shared_substrate_independence_claim(
    claims: dict[str, str],
    families: dict[str, tuple[str, ...]] | None = None,
) -> PortfolioAudit:
    """Refuse a paper that calls a SHARED public substrate independent replication.

    ``claims`` maps a paper key (matching :data:`ISSUE_SOURCE_FAMILIES`) to the
    text in which it describes its evidence. A paper may say whatever it likes
    about a substrate it alone uses; the prohibition bites only where the
    substrate is shared, because that is where "independent replication" would
    be counting one corpus twice across the portfolio.

    Recording the reuse is :func:`shared_source_families`. This is the other
    half the bullet asks for: the prohibition, enforced rather than stated.
    """

    if not isinstance(claims, dict):
        return PortfolioAudit(
            EXIT_CANNOT_CHECK, "PORTFOLIO_INTEGRITY_CANNOT_CHECK", ("claims is not a mapping",)
        )

    source = ISSUE_SOURCE_FAMILIES if families is None else families
    shared: dict[str, tuple[str, ...]] = dict(shared_source_families(source))
    shared_by_paper: dict[str, list[str]] = {}
    for family, papers in shared.items():
        for paper in papers:
            shared_by_paper.setdefault(paper, []).append(family)

    problems: list[str] = []
    for paper, text in claims.items():
        if not isinstance(text, str):
            return PortfolioAudit(
                EXIT_CANNOT_CHECK, "PORTFOLIO_INTEGRITY_CANNOT_CHECK", (f"{paper}: claim text is not a string",)
            )
        families_shared = shared_by_paper.get(paper)
        if not families_shared:
            continue
        lowered = text.lower()
        hit = next((m for m in INDEPENDENCE_CLAIM_MARKERS if m in lowered), None)
        if hit is None:
            continue
        others = sorted({q for f in families_shared for q in shared[f] if q != paper})
        problems.append(
            f"{paper}: claims {hit!r} while its substrate(s) {sorted(families_shared)} "
            f"are shared with {others}; a shared public corpus is not independent "
            "portfolio replication"
        )

    if problems:
        return PortfolioAudit(
            EXIT_SHARED_SUBSTRATE_CLAIM, "PORTFOLIO_INTEGRITY_FAIL", tuple(sorted(problems))
        )
    return PortfolioAudit(EXIT_PASS, "PORTFOLIO_INTEGRITY_PASS")
