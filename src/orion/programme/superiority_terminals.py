"""The frozen P1-P10 ``Done when`` registry (issues #649-#656, #662, #663).

Each :class:`~orion.programme.superiority.TerminalGate` transcribes one bullet
from one issue's ``Done when`` list verbatim into ``statement`` and types it into
a :class:`~orion.programme.superiority.TerminalKind`. Nothing is paraphrased and
nothing is merged: the count of gates for a paper equals the count of bullets in
its issue, so a reader can diff this file against the issue and see a drift.

Transcription rules
-------------------
- The statement is the bullet as written, minus its checkbox.
- A bullet asking for a *win* is ``PROTECTED_SUPERIORITY``; a bullet asking for a
  ceiling *to hold* is ``HARM_GUARD``. "Reduce false closure without excessive
  recomputation" is a guard even though it mentions a reduction, because what it
  forbids is the cost blow-up.
- Two bullets carry an explicit narrower disjunct in the issue text
  (``P9-U-T2``, ``P10-U-T1``) and set ``bounded_terminal_admissible``.
- Amendments to an issue's ``Done when`` list are amendments to this file. A
  comment on an issue that adds an obligation --- #649's P11/P12/P13 falsifier
  amendment is the live example --- is *not* a ``Done when`` bullet and is not
  transcribed here; it constrains how ``P1-U-T1`` may be run, and that constraint
  belongs in the campaign packet, not in the terminal list.

This module is data. It performs no adjudication and reads no evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from orion.programme.superiority import TerminalGate, TerminalKind

P1_U_ISSUE = 649
P2_U_ISSUE = 650
P3_U_ISSUE = 651
P4_U_ISSUE = 652
P5_U_ISSUE = 653
P6_U_ISSUE = 654
P7_U_ISSUE = 655
P8_U_ISSUE = 656
P9_U_ISSUE = 662
P10_U_ISSUE = 663


P1_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P1-U-T1",
        paper_id="P1",
        issue_number=P1_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="Protected superiority survives strongest donor-complete comparator.",
    ),
    TerminalGate(
        gate_id="P1-U-T2",
        paper_id="P1",
        issue_number=P1_U_ISSUE,
        kind=TerminalKind.REPLICATION,
        statement="Positive effect replicates across domains and independent implementation.",
    ),
    TerminalGate(
        gate_id="P1-U-T3",
        paper_id="P1",
        issue_number=P1_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="No-regression/no-unnecessary-reformulation guard passes.",
    ),
    TerminalGate(
        gate_id="P1-U-T4",
        paper_id="P1",
        issue_number=P1_U_ISSUE,
        kind=TerminalKind.SCOPE_EXPANSION,
        statement=(
            "Claim is wider than the current registered families because new "
            "heterogeneous naturalistic tasks support it."
        ),
    ),
    TerminalGate(
        gate_id="P1-U-T5",
        paper_id="P1",
        issue_number=P1_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement=(
            "Failure regimes are converted into explicit successor mechanics/theorems "
            "rather than hidden."
        ),
    ),
)


P2_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P2-U-T1",
        paper_id="P2",
        issue_number=P2_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Statistically supported superiority on decision-relevant recall or final "
            "scientific utility."
        ),
    ),
    TerminalGate(
        gate_id="P2-U-T2",
        paper_id="P2",
        issue_number=P2_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="Simultaneous non-inferiority/superiority on false closure.",
    ),
    TerminalGate(
        gate_id="P2-U-T3",
        paper_id="P2",
        issue_number=P2_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="Benefit holds under matched budgets and strong donor-complete baselines.",
    ),
    TerminalGate(
        gate_id="P2-U-T4",
        paper_id="P2",
        issue_number=P2_U_ISSUE,
        kind=TerminalKind.REPLICATION,
        statement="Cross-domain replication.",
    ),
    TerminalGate(
        gate_id="P2-U-T5",
        paper_id="P2",
        issue_number=P2_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement=(
            "A negative/tied family has generated and validated at least one stronger "
            "successor search mechanic."
        ),
    ),
)


P3_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P3-U-T1",
        paper_id="P3",
        issue_number=P3_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Significant reduction in false scientific merges versus strongest real competitor."
        ),
    ),
    TerminalGate(
        gate_id="P3-U-T2",
        paper_id="P3",
        issue_number=P3_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="No unacceptable false-split/plurality penalty.",
    ),
    TerminalGate(
        gate_id="P3-U-T3",
        paper_id="P3",
        issue_number=P3_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="Downstream scientific synthesis/QA benefit demonstrated.",
    ),
    TerminalGate(
        gate_id="P3-U-T4",
        paper_id="P3",
        issue_number=P3_U_ISSUE,
        kind=TerminalKind.REPLICATION,
        statement="Cross-domain and independent-expert replication.",
    ),
    TerminalGate(
        gate_id="P3-U-T5",
        paper_id="P3",
        issue_number=P3_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement=(
            "At least one new identity mechanic/coordinate is discovered from failure and "
            "prospectively validated."
        ),
    ),
)


P4_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P4-U-T1",
        paper_id="P4",
        issue_number=P4_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Strong superiority on false scientific promotion under matched clean coverage."
        ),
    ),
    TerminalGate(
        gate_id="P4-U-T2",
        paper_id="P4",
        issue_number=P4_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement=(
            "Identifiability audit shows the benchmark measures the intended competence."
        ),
    ),
    TerminalGate(
        gate_id="P4-U-T3",
        paper_id="P4",
        issue_number=P4_U_ISSUE,
        kind=TerminalKind.REPLICATION,
        statement=(
            "Result survives multiple constructions/domains and independent implementation."
        ),
    ),
    TerminalGate(
        gate_id="P4-U-T4",
        paper_id="P4",
        issue_number=P4_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Strong donor-complete comparator still loses on the residual "
            "scientific-promotion relation."
        ),
    ),
    TerminalGate(
        gate_id="P4-U-T5",
        paper_id="P4",
        issue_number=P4_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement=(
            "At least one old null/saturated family yields a prospectively successful new "
            "evaluation mechanic."
        ),
    ),
)


P5_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P5-U-T1",
        paper_id="P5",
        issue_number=P5_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="Repeated fresh-task superiority over strongest self-evolving comparator.",
    ),
    TerminalGate(
        gate_id="P5-U-T2",
        paper_id="P5",
        issue_number=P5_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="Harmful-transfer/regression guard passes.",
    ),
    TerminalGate(
        gate_id="P5-U-T3",
        paper_id="P5",
        issue_number=P5_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="Improvement remains significant after matched budget/cost controls.",
    ),
    TerminalGate(
        gate_id="P5-U-T4",
        paper_id="P5",
        issue_number=P5_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement=(
            "At least one learned or invented mechanic—not hand-written by us—causes "
            "a replicated gain."
        ),
    ),
    TerminalGate(
        gate_id="P5-U-T5",
        paper_id="P5",
        issue_number=P5_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Later ORION generation is measurably better at producing future improvements "
            "(meta-improvement signal)."
        ),
    ),
)


P6_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P6-U-T1",
        paper_id="P6",
        issue_number=P6_U_ISSUE,
        kind=TerminalKind.FORMAL_GENERALIZATION,
        statement="General theorem proved from primitive semantics.",
    ),
    TerminalGate(
        gate_id="P6-U-T2",
        paper_id="P6",
        issue_number=P6_U_ISSUE,
        kind=TerminalKind.FORMAL_GENERALIZATION,
        statement="Existing finite result follows as corollary.",
    ),
    TerminalGate(
        gate_id="P6-U-T3",
        paper_id="P6",
        issue_number=P6_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Naturalistic multi-domain evaluation shows large cost reduction with no "
            "validity loss."
        ),
    ),
    TerminalGate(
        gate_id="P6-U-T4",
        paper_id="P6",
        issue_number=P6_U_ISSUE,
        kind=TerminalKind.INDEPENDENT_REVIEW,
        statement="Independent proof/checker review.",
    ),
    TerminalGate(
        gate_id="P6-U-T5",
        paper_id="P6",
        issue_number=P6_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement=(
            "At least one discovered counterexample causes a principled framework extension "
            "rather than an ad hoc exception."
        ),
    ),
)


P7_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P7-U-T1",
        paper_id="P7",
        issue_number=P7_U_ISSUE,
        kind=TerminalKind.FORMAL_GENERALIZATION,
        statement="General compositional calculus/checker exists.",
    ),
    TerminalGate(
        gate_id="P7-U-T2",
        paper_id="P7",
        issue_number=P7_U_ISSUE,
        kind=TerminalKind.FORMAL_GENERALIZATION,
        statement="Current P7 results are corollaries/instances.",
    ),
    TerminalGate(
        gate_id="P7-U-T3",
        paper_id="P7",
        issue_number=P7_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Prospective prediction of real pipeline closure failures beats strong comparators."
        ),
    ),
    TerminalGate(
        gate_id="P7-U-T4",
        paper_id="P7",
        issue_number=P7_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="Significant reduction in false closure without excessive recomputation.",
    ),
    TerminalGate(
        gate_id="P7-U-T5",
        paper_id="P7",
        issue_number=P7_U_ISSUE,
        kind=TerminalKind.INDEPENDENT_REVIEW,
        statement="Independent formal/empirical reproduction.",
    ),
)


P8_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P8-U-T1",
        paper_id="P8",
        issue_number=P8_U_ISSUE,
        kind=TerminalKind.FORMAL_GENERALIZATION,
        statement="General composition/revocation theorem proved and mechanized.",
    ),
    TerminalGate(
        gate_id="P8-U-T2",
        paper_id="P8",
        issue_number=P8_U_ISSUE,
        kind=TerminalKind.FORMAL_GENERALIZATION,
        statement="Current P8 exhaustive result follows as an instance.",
    ),
    TerminalGate(
        gate_id="P8-U-T3",
        paper_id="P8",
        issue_number=P8_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "Prospective naturalistic evaluation shows failures generic "
            "authorization/provenance systems miss."
        ),
    ),
    TerminalGate(
        gate_id="P8-U-T4",
        paper_id="P8",
        issue_number=P8_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="Strong empirical utility without excessive blocking.",
    ),
    TerminalGate(
        gate_id="P8-U-T5",
        paper_id="P8",
        issue_number=P8_U_ISSUE,
        kind=TerminalKind.INDEPENDENT_REVIEW,
        statement="Independent formal and systems reproduction.",
    ),
)


P9_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P9-U-T1",
        paper_id="P9",
        issue_number=P9_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="direct LLM result survives all frozen hostile gates",
    ),
    TerminalGate(
        gate_id="P9-U-T2",
        paper_id="P9",
        issue_number=P9_U_ISSUE,
        kind=TerminalKind.REPLICATION,
        statement="second-family replication or explicit family-bounded terminal",
        bounded_terminal_admissible=True,
    ),
    TerminalGate(
        gate_id="P9-U-T3",
        paper_id="P9",
        issue_number=P9_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="scale/compute crossing is on-grid and prospectively defined",
    ),
    TerminalGate(
        gate_id="P9-U-T4",
        paper_id="P9",
        issue_number=P9_U_ISSUE,
        kind=TerminalKind.HARM_GUARD,
        statement="representation-length and format-prior attacks fail",
    ),
    TerminalGate(
        gate_id="P9-U-T5",
        paper_id="P9",
        issue_number=P9_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="domain-block uncertainty is positive",
    ),
    TerminalGate(
        gate_id="P9-U-T6",
        paper_id="P9",
        issue_number=P9_U_ISSUE,
        kind=TerminalKind.SCOPE_DISCIPLINE,
        statement=(
            "claim is phrased as the strongest earned bounded law, not a universal statement"
        ),
    ),
)


P10_U_GATES: tuple[TerminalGate, ...] = (
    TerminalGate(
        gate_id="P10-U-T1",
        paper_id="P10",
        issue_number=P10_U_ISSUE,
        kind=TerminalKind.REPLICATION,
        statement="native-state/search result is independently reproduced or retained as a negative",
        bounded_terminal_admissible=True,
    ),
    TerminalGate(
        gate_id="P10-U-T2",
        paper_id="P10",
        issue_number=P10_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement="real verified problem-solving gain beyond representation-only metrics",
    ),
    TerminalGate(
        gate_id="P10-U-T3",
        paper_id="P10",
        issue_number=P10_U_ISSUE,
        kind=TerminalKind.SUCCESSOR_MECHANIC,
        statement="at least one closed-world method-expansion result with low false escalation",
    ),
    TerminalGate(
        gate_id="P10-U-T4",
        paper_id="P10",
        issue_number=P10_U_ISSUE,
        kind=TerminalKind.PROTECTED_SUPERIORITY,
        statement=(
            "at least one real-domain candidate only if external correctness/novelty "
            "review survives"
        ),
    ),
    TerminalGate(
        gate_id="P10-U-T5",
        paper_id="P10",
        issue_number=P10_U_ISSUE,
        kind=TerminalKind.SCOPE_DISCIPLINE,
        statement="P10 paper claim remains bounded to what is actually earned.",
    ),
)


PAPER_GATES: dict[str, tuple[TerminalGate, ...]] = {
    "P1": P1_U_GATES,
    "P2": P2_U_GATES,
    "P3": P3_U_GATES,
    "P4": P4_U_GATES,
    "P5": P5_U_GATES,
    "P6": P6_U_GATES,
    "P7": P7_U_GATES,
    "P8": P8_U_GATES,
    "P9": P9_U_GATES,
    "P10": P10_U_GATES,
}

PAPER_ISSUES: dict[str, int] = {
    "P1": P1_U_ISSUE,
    "P2": P2_U_ISSUE,
    "P3": P3_U_ISSUE,
    "P4": P4_U_ISSUE,
    "P5": P5_U_ISSUE,
    "P6": P6_U_ISSUE,
    "P7": P7_U_ISSUE,
    "P8": P8_U_ISSUE,
    "P9": P9_U_ISSUE,
    "P10": P10_U_ISSUE,
}

ALL_GATES: tuple[TerminalGate, ...] = tuple(
    gate for paper_id in PAPER_GATES for gate in PAPER_GATES[paper_id]
)

ALL_GATE_IDS: tuple[str, ...] = tuple(gate.gate_id for gate in ALL_GATES)


@dataclass(frozen=True)
class PaperDirectories:
    """Which directory currently carries a paper's identity, and what preceded it.

    ``papers/PAPER_ALIASES.md`` is the repository's "single place for historical
    ORION paper-directory aliases", and it covers only P1-P5.

    Every paper now carries exactly one directory. The two that used to sit beside
    P9 and P10 were never papers and now carry the ``paper-xx-`` prefix --- see
    :data:`VACATED_PAPER_NUMBERS`.

    Paths follow the 2026-08-21 refactor that lifted P6-P10 out of
    ``papers/candidates/`` into ``papers/`` alongside the flagship five. So for P6-P10 there
    was nowhere recording succession, and two retired candidates sat beside two
    active ones under the same numbers, distinguishable only by opening each
    README. This is that record for the ten papers this module adjudicates.

    ``retired`` directories are **kept**, not deleted, and the reason is recorded
    per entry. The P1-P5 precedent in ``PAPER_ALIASES.md`` removed retired paths
    only because "They contained no independent manuscript content"; that test
    fails for both P9's and P10's predecessors, which hold results that live tests
    and other papers cite.
    """

    paper_id: str
    active: str
    retired: tuple[tuple[str, str], ...] = ()
    """``(directory, why it is retained)`` pairs."""


PAPER_DIRECTORIES: tuple[PaperDirectories, ...] = (
    PaperDirectories("P1", "papers/paper-01-recursive-epistemic-reconstruction"),
    PaperDirectories("P2", "papers/paper-02-open-world-scientific-discovery"),
    PaperDirectories(
        "P3",
        "papers/paper-03-global-knowledge-portrait",
        (("papers/paper-02-global-knowledge-portrait", "historical planning redirect to P3"),),
    ),
    PaperDirectories(
        "P4",
        "papers/paper-04-verified-scientific-discovery",
        (("papers/paper-03-verified-discovery", "historical planning redirect to P4"),),
    ),
    PaperDirectories(
        "P5",
        "papers/paper-05-self-orion",
        (("papers/paper-04-self-orion", "historical planning redirect to P5"),),
    ),
    PaperDirectories(
        "P6",
        "papers/paper-06-formal-epistemic-structures-and-mechanics",
        ((
            "papers/candidates/paper-06-formal-epistemic-structures-and-mechanics",
            "preserved pre-refactor candidate snapshot; the root-level package is active",
        ),),
    ),
    PaperDirectories(
        "P7",
        "papers/paper-07-epistemic-navigation-open-worlds",
        ((
            "papers/candidates/paper-07-epistemic-navigation-open-worlds",
            "preserved pre-refactor candidate snapshot; the root-level package is active",
        ),),
    ),
    PaperDirectories(
        "P8",
        "papers/paper-08-epistemic-authority-autonomous-science",
        ((
            "papers/candidates/paper-08-epistemic-authority-autonomous-science",
            "preserved pre-refactor candidate snapshot; the root-level package is active",
        ),),
    ),
    PaperDirectories(
        "P9",
        "papers/paper-09-structured-epistemic-learning",
        (
            (
                "papers/candidates/paper-09-structured-epistemic-learning",
                "preserved pre-refactor candidate snapshot; the root-level package is active",
            ),
            (
                "papers/candidates/paper-09-executable-research-core",
                "historical candidate later vacated into paper-xx-executable-research-core",
            ),
        ),
    ),
    PaperDirectories(
        "P10",
        "papers/paper-10-structured-problem-solving",
        (
            (
                "papers/candidates/paper-10-structured-problem-solving",
                "preserved successor-manuscript snapshot; the root-level package is active",
            ),
            (
                "papers/candidates/paper-10-content-bound-math-evaluation",
                "historical candidate later vacated into paper-xx-content-bound-math-evaluation",
            ),
        ),
    ),
)


#: Former paper candidates whose number has been vacated.
#:
#: Both were routed into other papers by a dated terminal decision, so neither was
#: available for renumbering into P11-P14: re-absorbing them would contradict a
#: recorded terminal *and* move them away from the papers that own their subjects.
#: ``content-bound-math-evaluation`` is not even dormant --- its ``FOLLOW_UPS.md``
#: carries active reopen triggers, and trigger 5 routes any surviving positive
#: through P4 and P8.
#:
#: The ``paper-xx-`` prefix is deliberate: it vacates the number while preserving
#: that these were paper candidates, and it does not match ``_PAPER_DIR_PATTERN``,
#: so the identity checks correctly stop treating them as paper identities.
VACATED_PAPER_NUMBERS: tuple[tuple[str, str, str], ...] = (
    (
        "papers/paper-xx-executable-research-core",
        "was P9",
        "MERGED INTO P8/PROGRAMME; no standalone manuscript. Its contribution is "
        "LearningMachine in the shared orion-learning-machine lane, and the live "
        "P9 manuscript does not cite it.",
    ),
    (
        "papers/paper-xx-content-bound-math-evaluation",
        "was P10",
        "TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME, decided 2026-08-18. Reopen "
        "triggers remain active; a surviving positive routes through P4 and P8.",
    ),
)

#: Paper identities registered but **not adjudicated** by this module: #670's
#: P11-P14, plus P15 which has no issue yet. Originally just the P11-P14 set whose
#: directories arrive with PR #715 (which targets ``papers/candidates/``; after
#: the 2026-08-21 refactor they are expected directly under ``papers/``, and
#: both spellings are registered so the merge order does not matter). They are *registered but not adjudicated*: this
#: module holds no ``Done when`` gates for them, because #670 is a programme issue
#: rather than a per-paper superiority terminal.
#:
#: They are listed here for one concrete reason. ``HC-SUP-STALE-PAPER-IDENTITY``
#: fails on a paper-numbered directory the registry has never heard of, so without
#: this the check would red PR #715 the moment it merged --- a check for identity
#: rot blocking a legitimate new identity. Registering the four names ahead of the
#: directories is the fix, and it is also the honest record: #670 assigned these
#: numbers before any directory existed.
FUTURE_PAPER_DIRECTORIES: dict[str, str] = {
    "P11": "papers/paper-11-state-as-computation",
    "P12": "papers/paper-12-adaptive-state-reasoning",
    "P13": "papers/paper-13-responsibility-carrying-state",
    "P14": "papers/paper-14-orion-rse",
    # No issue yet. Opened as a systems paper introducing the ORION research
    # harness and the ORION-Q dual harness; registered here so the identity
    # checks do not read a deliberately-opened folder as identity rot.
    "P15": "papers/paper-15-orion-research-harness",
}

#: Pre-refactor manuscript snapshots retained after the root-level P11-P14
#: packages became canonical. Recording these as historical locations resolves
#: the otherwise ambiguous same-slug split without deleting provenance.
FUTURE_RETIRED_PAPER_DIRECTORIES: dict[str, tuple[tuple[str, str], ...]] = {
    paper_id: ((
        directory.replace("papers/", "papers/candidates/", 1),
        "preserved pre-refactor manuscript snapshot; the root-level package is active",
    ),)
    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items()
    if paper_id in {"P11", "P12", "P13", "P14"}
}

#: Directories under ``papers/`` that are **not** paper identities.
#:
#: ``orion-learning-machine/`` is the shared code, experiments and committed
#: results that two paper directories cite. It sits beside a row of ``paper-NN-*``
#: directories and carried no README for a long time, which made it read as a
#: fourteenth paper. It is recorded here so that "is this a paper?" has a
#: machine-checkable answer, and so nothing tries to register it as one.
#:
#: The subtlety worth keeping: its own ``REPRODUCE.md`` names
#: ``paper-xx-executable-research-core`` and ``paper-xx-content-bound-math-evaluation``
#: --- the two *retired predecessors*, not the active P9 and P10. That is exactly
#: why both predecessors are retained rather than deleted.
SHARED_LANES: dict[str, str] = {
    "papers/orion-learning-machine": (
        "Shared P9/P10 reproduction lane: framework, experiments and committed "
        "results cited by paper-xx-executable-research-core and "
        "paper-xx-content-bound-math-evaluation. Authority is "
        "LOCAL_REPRODUCIBLE_CORE_ONLY. Not a publication identity."
    ),
}


#: Research tracks whose **standalone paper numbering was retired** by #670, and
#: the identity that absorbed each.
#:
#: This is the answer to "which of these became papers and which were absorbed?".
#: #670's rule is that absorption happens by *retiring a number*, never by
#: renumbering an existing paper:
#:
#:     Research decomposition is fine-grained; publication synthesis is
#:     coarse-grained. A research atom does not automatically receive a paper
#:     number.
#:
#: The issues stay open as falsifiable research tracks; only the publication
#: identity was withdrawn. P1-P10 numbering is explicitly preserved by the same
#: issue ("P1-U-P8-U remain #649-#656").
RETIRED_PAPER_NUMBERING: tuple[tuple[int, str, str], ...] = (
    (664, "accessibility work and representation-computation accounting", "P11"),
    (667, "state optionality: compile, cache, recover or materialize", "P11"),
    (668, "responsibility-carrying state interface and certified reuse", "P13"),
)

PAPER_DIRECTORIES_BY_ID: dict[str, PaperDirectories] = {
    entry.paper_id: entry for entry in PAPER_DIRECTORIES
}

REGISTERED_PAPER_DIRECTORIES: frozenset[str] = frozenset(
    [entry.active for entry in PAPER_DIRECTORIES]
    + [directory for entry in PAPER_DIRECTORIES for directory, _ in entry.retired]
    + list(FUTURE_PAPER_DIRECTORIES.values())
    + [
        directory
        for entries in FUTURE_RETIRED_PAPER_DIRECTORIES.values()
        for directory, _ in entries
    ]
    # PR #715 was authored against the pre-refactor layout. Registering the
    # ``candidates/`` spelling too means whichever order the two land in, a
    # legitimate new identity never reads as identity rot.
    + [
        directory.replace("papers/", "papers/candidates/", 1)
        for directory in FUTURE_PAPER_DIRECTORIES.values()
    ]
)


def validate_registry() -> tuple[str, ...]:
    """Return deduplicated structural errors in the registry. Empty means intact.

    Called from the tests rather than at import time, matching
    ``orion.programme.catalogue.validate_catalogue``: an import-time raise in a
    data module makes every unrelated test in the package fail with one traceback.
    """

    errors: list[str] = []

    seen: set[str] = set()
    for gate in ALL_GATES:
        if gate.gate_id in seen:
            errors.append(f"duplicate gate id {gate.gate_id}")
        seen.add(gate.gate_id)

    for paper_id, gates in PAPER_GATES.items():
        if paper_id not in PAPER_ISSUES:
            errors.append(f"paper {paper_id} has gates but no registered issue")
            continue
        expected_issue = PAPER_ISSUES[paper_id]
        for gate in gates:
            if gate.paper_id != paper_id:
                errors.append(f"gate {gate.gate_id} is filed under paper {paper_id}")
            if gate.issue_number != expected_issue:
                errors.append(
                    f"gate {gate.gate_id} cites issue #{gate.issue_number}, "
                    f"but paper {paper_id} is issue #{expected_issue}"
                )

    for paper_id in PAPER_ISSUES:
        if paper_id not in PAPER_GATES:
            errors.append(f"paper {paper_id} has an issue but no gates")

    for paper_id in PAPER_GATES:
        if paper_id not in PAPER_DIRECTORIES_BY_ID:
            errors.append(f"paper {paper_id} has gates but no registered directory")
    seen_directories: set[str] = set()
    for entry in PAPER_DIRECTORIES:
        for directory in (entry.active, *(item for item, _ in entry.retired)):
            if directory in seen_directories:
                errors.append(f"directory {directory} is registered to more than one paper")
            seen_directories.add(directory)
    for paper_id, directory in FUTURE_PAPER_DIRECTORIES.items():
        if paper_id in PAPER_DIRECTORIES_BY_ID:
            errors.append(f"paper {paper_id} is registered as both current and future")
        if directory in seen_directories:
            errors.append(f"directory {directory} is registered to more than one paper")
        seen_directories.add(directory)
    for lane in SHARED_LANES:
        if lane in seen_directories:
            errors.append(f"shared lane {lane} is also registered as a paper identity")
    for issue, _, absorbed_into in RETIRED_PAPER_NUMBERING:
        if absorbed_into not in FUTURE_PAPER_DIRECTORIES and absorbed_into not in PAPER_GATES:
            errors.append(f"issue #{issue} is absorbed into unregistered identity {absorbed_into}")

    return tuple(dict.fromkeys(errors))


__all__ = [
    "ALL_GATES",
    "ALL_GATE_IDS",
    "FUTURE_PAPER_DIRECTORIES",
    "FUTURE_RETIRED_PAPER_DIRECTORIES",
    "PAPER_DIRECTORIES",
    "PAPER_DIRECTORIES_BY_ID",
    "PAPER_GATES",
    "PAPER_ISSUES",
    "REGISTERED_PAPER_DIRECTORIES",
    "RETIRED_PAPER_NUMBERING",
    "SHARED_LANES",
    "VACATED_PAPER_NUMBERS",
    "PaperDirectories",
    "P1_U_GATES",
    "P2_U_GATES",
    "P3_U_GATES",
    "P4_U_GATES",
    "P5_U_GATES",
    "P6_U_GATES",
    "P7_U_GATES",
    "P8_U_GATES",
    "P9_U_GATES",
    "P10_U_GATES",
    "validate_registry",
]
