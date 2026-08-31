# ORION-20 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `PROSPECTIVE_PROTOCOL_FROZEN__NO_RESULT_EXISTS__EXECUTION_NOT_AUTHORIZED`

This addendum is part of the frozen ORION-20 paper-content packet. What it freezes
is a **protocol, not a result**, and it is written so that no reader can mistake one
for the other.

## What is actually frozen

The active terminal is `P10_PROSPECTIVE_PROTOCOL_ONLY`, the lifecycle state is
`PROSPECTIVE_PROTOCOL_FROZEN_INPUTS_ABSENT`, and `active_empirical_claim` is
**null**. `scientific_result_state` is `NO_P10_PROTECTED_RESULT`, and
`promotion_allowed` is `false`.

All six hypotheses are recorded `PROSPECTIVE_NOT_EXECUTED`:

| | hypothesis | promotion evidence it would require |
|---|---|---|
| H1 | verified problem-solving superiority | native verifier-backed comparison against the strongest donor-complete baseline |
| H2 | search-efficiency superiority | matched total-resource search analysis on independent tasks |
| H3 | obstruction-diagnosis validity | reachable false-escalation controls and blinded gold obstruction labels |
| H4 | outside-closure method-language expansion | independently witnessed OCME case, minimal edit, old-closure exclusion, held-out transfer |
| H5 | low false expansion | known-method controls with familywise error control |
| H6 | cross-domain transfer | protected reproduction across multiple independently sampled domains |

The value frozen here is the prospective design itself: hypotheses, claim ladder and
promotion requirements committed **before** any outcome exists. That ordering is the
scientific content of this artifact, and it is worth preserving exactly because
nothing has been run against it.

Alongside it the paper carries **formal** content rather than empirical content: a
closure formalism, a definition of certified expansion with a macro-rejection lemma,
a minimality definition, and an exact measurement contract. The package status
records this under terminal
`ORION_20_BOUNDED_OCME_SCIENCE_FROZEN__NATIVE_PROMOTION_PENDING` with
`journal_authority: false`. That formal content is frozen here — but see F-1 below,
because the set of theorems the paper actually claims is not yet well defined, and
this freeze must not be read as settling it.

## Frozen boundary

`execution_authorized` is `false`, and the blocker is named:
`P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT`. The protocol cannot be executed
because the frozen donor and evaluator inputs it requires do not exist yet. That is
a missing input, not a failed run, and the distinction is the whole point of the
record.

**Four states are explicitly forbidden**, and this freeze licenses none of them:
`P10_SUPERIORITY_SUPPORTED`; `METHOD_SPACE_EXPANSION_SUPPORTED`;
`FAIL_AS_HYPOTHESIS_OUTCOME`; and `CANNOT_CHECK_AS_HYPOTHESIS_OUTCOME`.

That last pair deserves emphasis, because it is the failure mode this paper is most
exposed to. An unexecuted hypothesis must **not** be recorded as `CANNOT_CHECK`, and
must not be recorded as a failure. `PROSPECTIVE_NOT_EXECUTED` is neither of those. A
protocol that was never run has produced no evidence in any direction, and
converting silence into a three-valued outcome would manufacture a result the
programme does not have.

The predecessor material carries `LOCAL_REPRODUCIBLE_CORE_ONLY` authority, is for
implementation and reproduction input only, and explicitly **does not discharge**
any of H1 through H6.

Promotion requires all six of: a prospectively frozen P10 protocol; native
verifier-backed execution; strong donor-complete comparators; an independently
witnessed OCME case; protected cross-domain replication; and external review
custody. `scientific_authority_delta` remains `NONE`.

## Two open findings the freeze records rather than settles

**F-1 (major) — the paper's theorem corpora do not agree.** `THEOREM_PROOF_AUDIT_V1.md`
records two incompatible theorem schemes, five entries against six, with different
titles, different content and **no mapping recorded anywhere**. Specifically: A-T1
asserts *decidability* while its nearest counterpart proves *unreachability* — a
different proposition, with no decision procedure, finiteness hypothesis or
termination argument supplied; A-T2 has **no counterpart and no proof anywhere**;
A-T3's necessity half is unproved; A-T4 uses a strength preorder that is **never
defined** against a counterpart stated by set inclusion; and A-T5's conservativity
conjunct is never proved.

So while the formal content above is frozen, **the set of theorems this paper claims
is not currently well defined**, and no reader should treat the formalism as settled
until F-1 is resolved.

**Canonical manuscript source is open.** There is not exactly one: four surfaces
inside the paper directory carry manuscript-level content, and
`successor/P10_U_MANUSCRIPT.tex` differs from the concatenated section files by
**331 lines**. The LaTeX build target was treated as canonical for the audit pass,
but no decision is recorded.

Venue choice depends on both. The status document is explicit that it cannot be made
responsibly until the canonical source and F-1 are resolved, because the claimed
theorem set is not yet determinate.

The paper-level `SHA256SUMS` does currently verify **50 of 50** entries when checked
from the repository root; the "46 of 50" note in the status document describes the
state mid-pass, not the committed tree.

## What would unblock it

Exactly one thing, and it is concrete rather than a judgement call: assembling the
full frozen donor and evaluator inputs the protocol names. Once those exist the
protocol is executable as written, and its terminals are already predeclared, so
execution cannot be steered by its own outcome. Until then this paper is a frozen
design and must be cited as one.

## Frozen content surface

The content packet consists of `P10_ACTIVE_CLAIM_AUTHORITY_V1.json`,
`CLAIM_EVIDENCE_LEDGER.md`, the manuscript with its primary-hypotheses and
claim-ladder sections bound by digest in that authority record,
`THEOREM_PROOF_AUDIT_V1.md`, `MANUSCRIPT_SCOPE_AUDIT_V1.md`,
`JOURNAL_PACKAGE_STATUS_V1.md`, `BOUND_RETURN_AFTER_PROMOTION_20260828.md`, and this
addendum. ORION-20's claim is a prospective design for obstruction-certified
method-language expansion; it owns no empirical result, and this freeze does not
give it one.
