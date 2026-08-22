# P1–P10 superiority terminals — frozen ledger and adjudication rule (2026-08-21)

**Lane:** `claude/papers-1-10-issues-uqrj2o`.
**Status:** additive audit object. This document closes no issue, promotes no
claim, and reopens none. It makes an existing adjudication machine-checkable.

**Machine-checkable form:**

- registry: `src/orion/programme/superiority_terminals.py`
- adjudication: `src/orion/programme/superiority.py`
- battery: `src/orion/programme/checks_superiority.py`
- ledger: `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`
- report: `make p1-p10-superiority-report`

## Why this object exists

Each of issues #649–#656, #662 and #663 ends in a `Done when` list. Those lists
are the terminals of ten open programmes, and they are clear. What has repeatedly
gone wrong is not the terminals but what arrives in their place:

> Status correction — 2026-08-20 after P1–P10 TeX refinement merge. The
> manuscript/refinement programme is complete, but this issue's scientific
> terminal is **NOT YET EARNED**. […] No manuscript-completion status is allowed
> to substitute for this issue's superiority terminal.
> — [#649](https://github.com/SzeChunYiu/ORION/issues/649#issuecomment-5356565517)

That correction was made by a human reading prose. The same substitution has more
than one shape, and the other shapes are harder to see:

| Substitution | What arrives | What was asked for |
| --- | --- | --- |
| manuscript for outcome | a merged/refined manuscript | a protected outcome |
| mechanism for transfer | a `BOUNDED_EXACT` `P<n>-X` terminal | a naturalistic protected outcome |
| `CANNOT_CHECK` for result | an honestly preserved campaign that never scored | a scored campaign |
| straw comparator | a win over a weaker baseline | a win over a donor-complete comparator |
| compensatory scoring | a headline win | a win **and** every guard holding |
| thin replication | a second run in the same domain | disjoint domains, independent implementation |
| predecessor reuse | a citation of the superseded result | the superseding result |

Each row is now a check that fails closed, so the substitution is caught by
running something rather than by remembering to look.

## Adjudication rule

Three-valued and non-compensatory, matching `orion.programme.hostile`:

- `PASS` / `FAIL` / `CANNOT_CHECK`, and `CANNOT_CHECK` blocks exactly as `FAIL`
  does. An unrecorded precondition is never a pass.
- A paper terminal is `EARNED` only when **every** gate passes. A superiority win
  does not buy off a failed guard.
- `CANNOT_CHECK` is deliberately not spelled `NOT_EARNED`. Ten programmes whose
  terminals have not been attempted have not been refuted either, and the report
  says so rather than reporting a negative nobody earned.

### Terminal kinds

| Kind | Discharged only by |
| --- | --- |
| `PROTECTED_SUPERIORITY` | `PROSPECTIVE_PROTECTED` |
| `HARM_GUARD` | `BOUNDED_PROTECTED` or `PROSPECTIVE_PROTECTED` |
| `REPLICATION` | `PROSPECTIVE_PROTECTED`, ≥2 distinct domains, independent implementation |
| `FORMAL_GENERALIZATION` | `MECHANIZED_THEOREM` |
| `INDEPENDENT_REVIEW` | `MECHANIZED_THEOREM` or `PROSPECTIVE_PROTECTED`, reviewed independently |
| `SUCCESSOR_MECHANIC` | `PROSPECTIVE_PROTECTED` |
| `SCOPE_DISCIPLINE` | advertised claim ≤ what the strongest grade licenses |
| `SCOPE_EXPANSION` | advertised claim reaches `GENERAL_PROSPECTIVE`, and is licensed there |

`INDEPENDENT_REVIEW` is separate from `REPLICATION` because the two ask
different questions. Replication asks whether an *effect* survives a disjoint
domain and a second implementation; an independent proof or checker review asks
whether a *formal artifact* holds up under outside scrutiny, and has no domains
to be disjoint across. Typing #654's, #655's and #656's review bullets as
`REPLICATION` made them unpassable via their own documented unblock path — caught
by review on PR #739, and now guarded by a test asserting every gate is reachable
by the strongest evidence its own type admits.

`SCOPE_EXPANSION` exists for exactly one bullet. #649's fourth `Done when` asks
for the claim to be *wider* than the registered families; typing it as discipline
would let a correctly-narrow claim pass a terminal demanding a wider one.

### Evidence grades

`ABSENT` · `CANNOT_CHECK` · `MANUSCRIPT_COMPLETION` · `MECHANISM_NON_VACUITY` ·
`MECHANIZED_THEOREM` · `BOUNDED_PROTECTED` · `PROSPECTIVE_PROTECTED`

The grades are ordered for one purpose only — deciding how wide a claim a paper
may advertise. Discharge is a *relation*, not a threshold: a `MECHANIZED_THEOREM`
discharges a formal terminal and no empirical one, and a `MECHANISM_NON_VACUITY`
result discharges neither however strong it is.

### Predecessors count, and discharge nothing

Every one of these ten programmes stands on a predecessor. The ledger names them
with their own terminal strings, and they do two things: they license the paper's
*current bounded claim*, and they discharge no `P<n>-U` gate. Pointing a gate's
`artifact_refs` at one fails `HC-SUP-PREDECESSOR-REUSE` regardless of the grade
the entry claims for itself — a grade is an assertion, a path is a fact.

## Frozen state at 2026-08-21

Regenerate with `make p1-p10-superiority-report`. Exit code `3` is the expected
result and is distinct from both a pass and a build failure.

| Paper | Issue | Terminal | Strongest grade | Gates passing |
| --- | --- | --- | --- | --- |
| P1 | #649 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P2 | #650 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P3 | #651 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P4 | #652 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P5 | #653 | `CANNOT_CHECK` | `BOUNDED_PROTECTED` | 0/5 |
| P6 | #654 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P7 | #655 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P8 | #656 | `CANNOT_CHECK` | `MECHANISM_NON_VACUITY` | 0/5 |
| P9 | #662 | `CANNOT_CHECK` | `BOUNDED_PROTECTED` | 1/6 |
| P10 | #663 | `CANNOT_CHECK` | `BOUNDED_PROTECTED` | 1/5 |

**2 of 51 gates pass.** Both are scope gates — `P9-U-T6` and `P10-U-T5` — and
they pass because those two papers do keep their advertised claims inside what
they earned. Nothing else is discharged, and the thirteen-check battery is clean:
no substitution is currently being made anywhere in the ledger.

The full battery is clean *and* the report still blocks. That combination is the
object working as intended: "nobody is cheating" and "nothing is established" are
different facts, and neither implies the other.

## Why `CANNOT_CHECK` is not one status

The first version of this ledger reported all ten programmes as `CANNOT_CHECK`
and stopped there. That word was covering at least three unrelated situations —
a one-file defect, an evaluation arena nobody has built, and a theorem nobody has
proved — which is the same collapse the three-valued outcome exists to prevent
one level up.

Every blocked terminal now carries a **responsibility class**, taken from P1's
own frozen taxonomy in
`development/p1-u-gpt-r2-naturalistic/DEVELOPMENT_PACKET.md`, plus what would
unblock it and how near that is. `HC-SUP-UNCLASSIFIED-BLOCKER` fails on a blocked
gate with no recorded cause, so the ledger cannot quietly go back to one word.

Forty-five of the fifty-one registered terminals are blocked, and all forty-five
are classified. Six are discharged: `P9-U-T6` and `P10-U-T5` on scope discipline,
and `P6-U-T1`, `P6-U-T2`, `P7-U-T1` and `P8-U-T1` on mechanized theorems, which is
what a `FORMAL_GENERALIZATION` terminal admits. Those four had been blocked on
blocker text asking for evaluator custody; custody is a precondition of an
empirical campaign, and requiring it of a proof blocks every provable gate on a
category error. The queue, nearest first:

| Actionability | Terminals | Meaning |
| --- | --- | --- |
| `BLOCKED_ON_UPSTREAM` | 5 | another lane's in-flight work, nameable by PR |
| `BLOCKED_ON_CAMPAIGN` | 20 | arena and comparator exist; no protected run scored |
| `BLOCKED_ON_NEW_ARENA` | 14 | the evaluation object itself does not exist yet |
| `BLOCKED_ON_PROOF` | 6 | needs a mechanized theorem from primitive semantics |

By responsibility class: `MEASUREMENT_OR_EVALUATOR` 19, `SEARCH_OR_EVIDENCE` 18,
`OBJECTIVE_OR_MODEL_CLASS` 4, `IMPLEMENTATION_OR_ENVIRONMENT` 3,
`REPRESENTATION_OR_INTERFACE` 1.

These counts are pinned against the generated report by
`test_ledger_document_counts_match_the_report`, because a hand-written table
beside a generated one drifts on the first regeneration.

Nothing is `ACTIONABLE_NOW`, and that is a real finding rather than a formality:
after the P1 implementation defect below, the nearest work is other lanes'
in-flight PRs, and everything past that needs a campaign, an arena or a proof.

## P1: the defect is solved, and the result is not yet attributable

This section was written when the P1 diagnosis was "an implementation defect stops
the campaign producing rows". Cross-agent verification has since moved it, and the
new position is better news and a harder problem.

**The digest defect was the only thing between R6 and a scored primary.** With the
repair installed, the frozen 2020 primary runs to completion: 48/48 rows bound,
zero leakage rows, terminal `P1_R6_PRIMARY_PASS_PENDING_2019_REPLICATION`. Run
unpatched, the same inputs give 48/48 invalid rows *with every other check already
green underneath*. So P1 was never short of evidence — it was one representation
mismatch away from a result, and that mismatch had survived four campaign rounds
because a predicate answering `False` at a type boundary is indistinguishable from
a check that ran and failed. Full record in
`research/failures/2026-08-digest-representation-boundary-mixup/`; the two SHA-256
representations are now named apart in `src/orion/core/digests.py`, which raises on
a crossed boundary instead of returning `False`.

**But the scored result cannot support a P1-U claim yet.** `ORION_NATIVE_BASE`
returns `UNRESOLVED` on 48/48 episodes: the solver never reaches `DIAGNOSE`, so the
ablation arm #723 added *precisely* to show the gain comes from the ARD addition
rather than from runtime wrapping is inert, and all six families "differ from BASE"
trivially. Two frozen guards also do not test what they are named — class
noninferiority files both pair members under `adverse_class`, so the control class
is never evaluated, and domain noninferiority has 26 strata of 1–2 episodes, making
the −0.10 margin a hard zero-loss rule.

That is why `P1-U-T1` is now `MEASUREMENT_OR_EVALUATOR`, not
`IMPLEMENTATION_OR_ENVIRONMENT`. The blocker moved one layer up, from *can the
campaign run* to *does the campaign measure what it claims*. Details and
reproductions:
`research/claim_expansion/p1/claude_r6_verification/CROSS_AGENT_VERIFICATION_2026-08-21.md`.

Nothing from that verification is recorded as evidence against a P1-U gate. It is an
observation about another lane's in-flight work; counting it would be the post-hoc
promotion `HC-SUP-POST-HOC-FREEZE` exists to refuse.

### What each paper's terminal is currently waiting on

- **P1 #649** — see above. A scored 2020 primary now exists; what it lacks is
  attribution (inert ablation arm) and replication (the 2019 evaluator cannot run).
- **P2 #650** — a naturalistic open-world arena. `P2-X` scored exact acquisition
  contracts, which is a different object from deep-research recall.
- **P3 #651** — raw heterogeneous literature with double annotation. The `P3-X`
  terminal explicitly does not authorize it.
- **P4 #652** — an identifiability-audited construction-balanced benchmark. The
  old H3 slice was non-identifying, which is why the issue asks for a new one.
- **P5 #653** — everything downstream of a matched baseline. The `21/24`
  attribution record's own `baseline_pressure` layer is `CANNOT_CHECK`.
- **P6 #654** / **P7 #655** / **P8 #656** — `FORMAL_GENERALIZATION` gates need a
  mechanized theorem from primitive semantics. The existing checkers are
  exhaustive finite enumeration, which is what the issues ask to *stop* being the
  primary authority.
- **P9 #662** — the direct open-weight scaling run and its second family. The
  scope gate already passes.
- **P10 #663** — native-state extraction and verified solve benefit. The scope
  gate already passes; the successor `.tex` is a manuscript and is listed as a
  predecessor precisely so it cannot be counted.

## Paper identity — resolved 2026-08-21

When this ledger was first written, `papers/` held two `paper-09-*` and two
`paper-10-*` directories where P1–P8 held one each. That is now resolved, and the
resolution is worth recording because the first diagnosis was wrong.

They were never second versions of P9 and P10. They were a **benchmark package**
and a **benchmark corpus** wearing paper numbers — different *layers* of the same
research stack, not competing *lineages*. The live P9 manuscript does not cite
`executable-research-core` at all.

Both were already routed elsewhere by dated terminal decisions — into P8 and
P4/P8 respectively — so neither was available for renumbering into P11–P14 either:
re-absorbing them would contradict a recorded terminal and move them away from the
papers that own their subjects. Both now carry the `paper-xx-` prefix, which
vacates the number without deleting content that live tests and other papers cite.
See `VACATED_PAPER_NUMBERS` and `papers/PAPER_ALIASES.md`.

`papers/` now holds exactly one directory per paper, `paper-01` through
`paper-15`, plus `orion-learning-machine/` (the shared P9/P10 lane, not a paper,
recorded in `SHARED_LANES`) and the two vacated candidates.

Three checks hold that shape: `HC-SUP-STALE-PAPER-IDENTITY` on any paper-numbered
directory nobody registered, `HC-SUP-SPLIT-PAPER-IDENTITY` on one identity holding
content in two locations, and `validate_registry` on a directory registered to two
papers.

## Boundary

This object is an audit instrument. It:

- **does not** grant closure — `grants_issue_closure` is hardwired `false` in the
  report payload, mirroring `HostileCheckReport.grants_phase4_closure`;
- **does not** amend any issue's `Done when` list. Amending an issue amends
  `superiority_terminals.py`; a comment adding an obligation (#649's
  P11/P12/P13 falsifier amendment) constrains how a gate may be *run* and belongs
  in the campaign packet;
- **does not** re-score, reopen or reinterpret any predecessor result. Every
  terminal string in the ledger is quoted from the artifact that declared it;
- **is not** a substitute for any campaign. A clean battery says no substitution
  is being made. It says nothing about whether the science is done.
