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
| `SUCCESSOR_MECHANIC` | `PROSPECTIVE_PROTECTED` |
| `SCOPE_DISCIPLINE` | advertised claim ≤ what the strongest grade licenses |
| `SCOPE_EXPANSION` | advertised claim reaches `GENERAL_PROSPECTIVE`, and is licensed there |

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
they earned. Nothing else is discharged, and the eleven-check battery is clean:
no substitution is currently being made anywhere in the ledger.

The full battery is clean *and* the report still blocks. That combination is the
object working as intended: "nobody is cheating" and "nothing is established" are
different facts, and neither implies the other.

### What each paper's terminal is currently waiting on

- **P1 #649** — every gate. The `P1-X` exact result is `A3_CANNOT_CHECK` on the
  axis the issue asks about, and R2/R3/R4 each terminated at acquisition.
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
