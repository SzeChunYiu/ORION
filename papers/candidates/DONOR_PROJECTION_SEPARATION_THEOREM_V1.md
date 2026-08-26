# Donor-projection separation theorem V1

**Date:** 2026-08-18  
**Purpose:** formalize the strongest honest sense in which an engulfed ORION envelope can strictly exceed an isolated donor without using a weak strawman.

## 1. Setup

Let the full scientific decision state be

\[
\omega\in\Omega
\]

and let the correct protected decision be

\[
F:\Omega\to\mathcal Y.
\]

A donor family `i` natively observes only a projection

\[
\pi_i:\Omega\to X_i.
\]

An **isolated donor decision rule** is any deterministic function

\[
g_i:X_i\to\mathcal Y.
\]

This definition does not weaken the donor inside its intended scope. It states only what information that isolated donor interface exposes for the cross-structure task.

## 2. Projection insufficiency theorem

### Theorem 1

If there exist `\omega_0,\omega_1\in\Omega` such that

\[
\pi_i(\omega_0)=\pi_i(\omega_1)
\]

but

\[
F(\omega_0)\neq F(\omega_1),
\]

then no isolated donor rule `g_i\circ\pi_i` can be correct on both states.

### Proof

Because the donor projections are equal, deterministic `g_i` must return the same output on both states. The protected gold decisions differ, so at least one output is wrong. `\square`

This is a standard indistinguishability argument. The contribution is the explicit cross-donor instantiation, not the mathematical trick.

## 3. ORION-16 instantiation — computation/repair versus scientific admissibility

Construct two mechanic states with identical bare transition, dependency projection and incremental-computation status:

\[
\pi_{repair}(\omega_0)=\pi_{repair}(\omega_1).
\]

In `\omega_0`, the hard scientific verification obligation is satisfied and commit authority is valid; in `\omega_1`, the verification evidence is unavailable. The protected decisions are respectively

\[
F(\omega_0)=AUTHORIZED,
\qquad
F(\omega_1)=CANNOT\_CHECK.
\]

Therefore no rule observing only the bare repair/computation projection can decide scientific admissibility correctly on both.

This is the cross-donor reading of ORION-16's typed-erasure separation theorem.

## 4. ORION-17 instantiation — navigation evidence versus transformed closure

Construct two inquiry states with identical fixed-chart navigation history, retrieved evidence identity/value, route status and resource state. Let the only difference be the active scientific obligation after an authorized objective transformation:

- `\omega_0`: evidence `x=5` must satisfy `x>3`;
- `\omega_1`: the same evidence must satisfy `x>7`.

A fixed-navigation/evidence projection that omits the transformed obligation is identical in both states, while

\[
F(\omega_0)=TASK\_STOP,
\qquad
F(\omega_1)=CONTINUE\;\text{or}\;CANNOT\_CHECK.
\]

Hence fixed navigation plus evidence validity alone cannot determine post-transform scientific closure.

An objective-evolution donor alone has the dual insufficiency if it sees the new objective but not whether the relevant content-bound evidence/coverage premises are available. The combined atlas state separates both.

## 5. ORION-18 instantiation — generic permission versus scientific discharge

Construct two requests with identical generic authorization facts:

- same principal/effect;
- same in-scope valid grant;
- same commit epoch;
- no generic security blocker.

In `\omega_0`, the target scientific obligation has an exact typed discharge; in `\omega_1`, that evidence is unavailable. A generic-authorization projection is identical, but

\[
F(\omega_0)=AUTHORIZED,
\qquad
F(\omega_1)=CANNOT\_CHECK.
\]

Therefore generic action authorization alone cannot implement the scientific-authority decision on both states.

Similarly, a provenance-only projection can be identical for two uses of the same valid source while the target obligations differ (supporting a sentence versus independently verifying a claim).

## 6. Engulfed envelope separation

Let the ORION envelope observe a joint projection

\[
\Pi_J=(\pi_{i_1},\ldots,\pi_{i_k})
\]

containing every coordinate on which `F` actually depends for the protected cross-structure task.

### Proposition 2

If `F` is a function of `\Pi_J`, then a joint envelope rule can represent `F` even when each isolated `\pi_{i_j}` is individually insufficient.

This is the formal sense in which engulfing can produce a **strict cross-task expressivity advantage over isolated donors**.

## 7. Why this does not beat the ideal donor product

Define the ideal donor product to expose the same joint information `\Pi_J` and implement the same cross-interface laws. It is then not an isolated donor. The projection-insufficiency theorem no longer applies because the distinguishing information is available.

Consequently:

\[
\text{ORION} > \text{isolated donor on some cross-structure tasks}
\]

can coexist with

\[
\text{ORION} = \text{ideal donor product}
\]

when both share the complete joint semantics.

This is the correct target for the ORION programme:

1. absorb strong donors;
2. prove when isolated views are insufficient;
3. supply the missing joint interface;
4. compare against the ideal product;
5. claim further superiority only if an additional law or measurable engineering property survives.

## 8. Executable witness

`checkers/check_donor_projection_separation_v1.py` freezes the ORION-16, ORION-17 and ORION-18 indistinguishable-pair constructions and verifies that every isolated rule is forced to make the same decision within each pair while the gold terminals differ. It also verifies that the joint envelope coordinates separate the pairs.

## 9. Claim boundary

Permitted:

> On explicit cross-structure tasks, a donor interface that omits a decision-relevant coordinate can be strictly insufficient; the donor-complete ORION envelope separates finite pairs that isolated repair, navigation or generic-authorization projections cannot.

Not permitted:

> ORION outperforms every implementation of TMS, POMDP planning, UCON, FAVA, ETAS, or other donors.

A donor augmented with the missing coordinates/interface is no longer the isolated projection addressed by the theorem and belongs in the donor-product baseline.
