# Adversarial analysis of ORION-18 Proposition 12 — the one surviving claim

**Status:** `SURVIVOR_DOWNGRADED__VENUE_MISMATCH_IDENTIFIED`
**Scientific authority delta:** `NONE`. This can only narrow what ORION-18 may claim.

`A6_DONOR_SUBTRACTION_V1.md` found nine of ten results inherited and marked exactly one
`SURVIVING_NEW_CONSEQUENCE`: Proposition 12, *permission is not a function of confidence
and expected utility*. It was the paper's answer to the review's charge that the theory
reduces to classical decision theory.

I attacked it. **It does not survive as a theorem.** It survives as something else, and
naming that correctly is what makes ORION-18 publishable rather than rejected.

## The claim and its proof

> **Proposition 12.** There is no well-defined map `f` with `Perm(e) = f(Conf, EU)`.

The proof constructs `e₁, e₂` with `Conf(e₁) = Conf(e₂)` and `EU(e₁) = EU(e₂)`, differing
only in that an obligation is discharged for one and undischarged for the other because
the evidence its judgment type names is unavailable. Definition 10 then gives
`Perm(e₁) = AUTHORIZED` and `Perm(e₂) = CANNOT_CHECK`. Same fibre of `(Conf, EU)`,
different image, so `f` is not well defined.

## Attack 1 — the proposition is close to a definitional tautology

Definition 10 defines `Perm` by clauses over obligations, blockers, grants, freshness and
binding. **None of those is `Conf` or `EU`.** So `Perm` is a function of a variable set
disjoint from `(Conf, EU)`, and exhibiting two effects that agree on `(Conf, EU)` while
differing on an input `Perm` actually reads is not a discovery — it is the definition,
restated.

The general form is: *a function of X is not a function of Y when X ⊄ Y.* That is true and
it is not a theorem.

For the proposition to carry weight it would need to be an **impossibility claim**: that no
rational reconstruction of `Perm` in terms of `(Conf, EU)` exists for any decision-theoretic
agent. It is not stated that way and it is not proved that way.

## Attack 2 — there is a donor after all, and it is elementary

Constrained optimisation separates the **feasible set** from the **objective function**.
Permission is a constraint; expected utility is an objective. *The feasible set is not
determined by the objective function* is structural to the whole framework, not a finding
within it.

Deontic logic supplies the same separation independently, and Hume's is/ought gap is the
informal ancestor of both.

So `A6_DONOR_SUBTRACTION_V1.md`'s provisional `SURVIVING_NEW_CONSEQUENCE` was too
generous. **Corrected verdict for Proposition 12 as stated: `DONOR`** — constraint/objective
separation.

## What genuinely survives, and it is not the proposition

**Corollary 12.1** is the real content:

> Raising `Conf` or `EU` cannot convert `CANNOT_CHECK` or `DENIED` into `AUTHORIZED`.

Read as mathematics this inherits Proposition 12's weakness. Read as an **architectural
guarantee about an implemented system**, it is a different and defensible object: *this
system is built so that confidence cannot purchase authorization, and here is the proof
over its actual definitions.*

That is a **verified design property**, not a theorem about agents in general. Its value is
that the non-amplification property is *checked* rather than asserted — which is exactly
what the paper's own machinery does, and what its hostile-mutation controls test.

## Consequence for venue, which is the actionable part

The review said ORION-18's theory sits too close to classical decision theory. It is right,
and the response is not to argue but to stop submitting it as decision theory.

- **As a decision-theory or AI-theory contribution:** Proposition 12 is constraint/objective
  separation and will be recognised as such by any reviewer who works in the area. Reject.
- **As a formal-methods / verification contribution:** "a specified authorization system in
  which confidence and utility provably cannot promote a terminal, with mechanised checks
  and hostile mutations that fail closed" is a legitimate, checkable, useful result.

`nature-writing`'s decision engine lists exactly this repair — *change target or article
type when the science is sound but the editorial objective is mismatched* — and ranks it
alongside adding evidence rather than beneath it.

## What this costs and what it buys

**Costs:** ORION-18 cannot claim a new theorem about permission. The donor tally becomes
`DONOR` 6, `SPECIALIZATION` 4, `SURVIVING_NEW_CONSEQUENCE` 0 at the theorem level.

**Buys:** a claim that survives contact with a reviewer. A verified non-amplification
property with mechanised checking is publishable where a restated separation result is not,
and the paper already contains the machinery the verification venue would ask for.

## Two candidates from the donor pass remain untested

Theorem 4's uniformity premise and Proposition 14's *mandatory* forward-only demotion were
flagged alongside Proposition 12. **They have not received this treatment.** Given that the
strongest of the three collapsed under an hour of adversarial reading, neither should be
quoted as novel until it has survived the same attack. My prior is now that Theorem 4 falls
to abstract-interpretation completeness; Proposition 14's obligation is the one I would bet
on, because obligation-to-demote is a genuinely deontic claim with no obvious mechanism
counterpart.

## Discipline note

I generated the survivor list and then refuted my own strongest entry. That is the correct
direction of travel and it should continue: the remaining two candidates need the same
hostile pass before the manuscripts are rewritten around them, not after.
