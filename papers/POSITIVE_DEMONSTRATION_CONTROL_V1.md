# The positive-demonstration control

**Status:** programme methodology note · **Date:** 2026-08-29
**Scope:** experiment and control design. `scientific_authority_delta: NONE` — this note creates,
upgrades and retracts nothing. It names a practice already present in four ORION packets and states
it so the next round is designed with it rather than rediscovering it.

---

## The rule

> **For every claimed separation, write a control that requires the *disfavoured* arm to exhibit the
> failure you attribute to it — at least once, on the same instrument the real comparison uses.
> If that demonstration never arrives, the terminal is `CANNOT_CHECK`, never `PASS`.**

A control that only asks *"did the favoured arm do well?"* cannot distinguish **the mechanism works**
from **the comparison was true by construction**. Both produce a clean table.

## The failure it prevents

A comparison can be a tautology and still pass every check that looks only at outcomes. If ground
truth is defined so the disfavoured arm *cannot* exhibit the failure being attributed to it, then
"our rule has 0 violations, theirs has N" measures the definition, not the world — and no amount of
re-running finds it, because every run agrees.

This is not hypothetical. It was caught once, by exactly this control, and would otherwise have
shipped.

## The instance that named it — ORION-23, control V2

ORION-23's transport law claims the three-valued rule is the unique rule with both zero unsoundness
and zero waste. Waste is attributed to the pessimistic collapse. **Control V2 demanded a positive
demonstration: the pessimistic collapse must over-revoke at least once.**

It never did. The run returned **`T4_CANNOT_CHECK`** rather than a pass.

The cause was in the authors' own instrument. Ground truth had been defined as *"reuse is sound iff
no premise is `CONTRADICTED` or `UNKNOWN`"*, which makes `UNKNOWN` **definitionally** unsound to
reuse. Under that definition revoking on `UNKNOWN` is always correct, the pessimistic rule is
optimal, and the waste claim (P5) is **false by construction rather than by evidence**.

The frozen wording of P3 already excluded that reading — *"unnecessary revocation"* is only
meaningful if the premise **might in fact have been satisfied** — so the claim had always required a
hidden actual value behind `UNKNOWN`. The checker simply had not modelled one.

**The repair was to the instrument, not the claims.** Each `UNKNOWN` premise now carries a hidden
actual value, enumerated both ways, invisible to every rule. No claim, margin, terminal or control
was changed. In the packet's own words: had V2 not been written to demand a *positive*
demonstration, *"this would have shipped as a passing result built on a tautology."*

## It already generalises — four more instances

| packet | control | what it forces |
|---|---|---|
| **ORION-25** C1 | Where the theorem predicts forgery, forgery must actually succeed — **260/260** | *"or the attack is inert and every negative cell is meaningless"* |
| **ORION-25** C4 | Collapsing assignments must be present in the sweep — **5** | *"without them T2 would be untested and the sweep vacuous"* |
| **ORION-22** Y1 | A planted sub-floor must be caught by the same comparison the claim uses — **36/36** | the detector demonstrably fires |
| **ORION-16** (graph-quality law) | Planted unsound cases must be caught by the same predicate the real search uses — **310,002/310,002**; and zero-weighting cases must *not* alarm — **32,760/32,760** | *"no unsound over-approximation found" is distinguishable from "the predicate cannot fire"* |

The last row carries both halves: the predicate must fire where it should **and stay silent where it
should not**. A detector that always fires is as uninformative as one that never can.

## The counterpart — check against a record you did not just compute

**ORION-22's Y2.** The zero set was cross-checked against the **already-committed** aliasing record
rather than an intersection recomputed inside the same packet — *"recomputing the intersection myself
and finding agreement would have been circular; it would have tested this packet against itself."*

A positive-demonstration control proves the instrument *can* register the failure. An
anti-circularity control proves it is not being asked to confirm its own arithmetic. Separations of
consequence want both.

## Where it was missing — ORION-02, R23 and R24

Both rounds compared a geometric arm against a **matched no-geometry lexical control** reaching the
same 44/44 coverage, and reported the comparison as **bare counts with no test**. No control demanded
a positive demonstration that the lexical arm *should* do worse, and none asked whether the gap
survived between-dataset variation.

In **R23** the per-dataset data were published, so the gap could be tested afterwards. It resolved to
**not significant, p = 0.092** — the separation the counts appeared to show was not there.

In **R24** the control **beat** the treatment outright — **14 violations against the geometric arm's
20** — and the comparison **cannot be tested at all**. Its emitter computes
`violation_strict` per dataset and then consumes it only as `sum(...)`; the per-dataset `rows`
mapping is never serialised. That is an **emission gap, not a measurement gap** — the quantity a
paired test needs existed at run time and was dropped at write time, and it is not recoverable after
the fact.

Two lessons, and the second is cheap: a control matching the treatment's coverage with *fewer*
violations is **the control beating the treatment**, and bare counts cannot separate that from noise;
and **per-item values must be emitted, not just aggregates**, or the check becomes impossible rather
than merely undone.

## Scope — where a positive-demonstration control does *not* apply

This rule governs **claimed separations between arms**. It does not convert into a demand for
statistical tests everywhere:

- For an **exhaustive enumeration** — every status assignment, every role-by-compromise cell — there
  is no sampling, so no test is owed. The analogous control is **non-degeneracy**: does the enumerated
  space actually contain instances where the distinction could show? ORION-25's C4 is exactly that
  form, and it is the right control there.
- For a **pre-registered gate**, failing the gate is a legitimate verdict without a test. What is
  still owed is a **detectable-effect statement**: what capability the gate would reject, and with
  what error. Without it, "the capability is absent" cannot be separated from "the gate cannot see it
  at this n" — readings with opposite implications.

Demanding a paired test of an exhaustive enumeration is a category error, and a checker that fires
there is crying wolf on its first real run — which is how checkers get switched off.

## Reading rule — an honest negative and an omission look identical

The controls above are about *designing* an experiment. This one is about *reading* an
artifact, and it is the cheapest item here.

**A table that declines to report and a table that was never wired both appear as a table
with no numbers in it.** Nothing in a file listing, a diff stat, or a grep for empty cells
separates them. The only thing that does is the header comment stating *why* — and you
have to open the file to see it.

That distinction decided a real call. ORION-15's seven empty manuscript tables were
flagged as an instrumentation omission — "high value and cheap to wire". They are honest
`CANNOT_CHECK` declarations with stated reasons and an explicit refusal to impute. P5-T2's
own header reads: *"no matched baseline/ablation arms, round identities, or campaign-level
outcomes. Numbers are not imputed from the 21/24 diagnostic accuracy."*

**Wiring numbers into them would have manufactured evidence where the paper had correctly
declined to.** The lead was plausible, specific, and wrong, and it was checked rather than
executed.

So: before treating an empty or absent artifact as a gap, open it and look for a stated
reason. An absence with a recorded justification is a finding. An absence without one is a
gap. They are the same shape on disk and opposite in meaning, and the programme's whole
`CANNOT_CHECK` discipline depends on not confusing them — the same rule as
`"pooled_significance_test": "NOT_COMPUTED_BY_PROTOCOL"`, which makes an omission
auditable rather than silent.

## Checklist

1. Name the failure the disfavoured arm is supposed to exhibit.
2. Write a control that **requires** it to exhibit that failure at least once, on the instrument the
   real comparison uses.
3. Write the paired no-alarm control: the detector must stay silent where nothing is wrong.
4. Prefer checking against an already-committed record over a value recomputed here.
5. If the demanded demonstration does not arrive, terminal `CANNOT_CHECK` — **never** `PASS`.
   "Could not check" must never read as "checked and fine."
6. Emit per-item values alongside aggregates, always.
7. If the quantity is a sample estimate, test it. If it is an enumeration, show non-degeneracy
   instead. If it is a gate, state the detectable effect.

## Provenance

`papers/orion-23-responsibility-carrying-state/transport-law-v1/CLAIM_DISPOSITION.md` (control V2 and
the instrument repair); `papers/orion-25-orion-research-harness/experiments/trust-domain-law-v1/CLAIM_DISPOSITION.md`
(C1–C4); `papers/orion-22-adaptive-state-reasoning/experiments/observation-regret-law-v1/CLAIM_DISPOSITION.md`
(Y1, Y2); `papers/orion-16-formal-epistemic-structures-and-mechanics/revalidation/graph-quality-law-v1/CLAIM_DISPOSITION.md`
(planted-unsound and zero-weighting controls); ORION-02 R23/R24 rounds for the counterexample.
