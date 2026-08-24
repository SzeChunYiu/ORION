# P6 formal core V2.1 — normative closure

**Supersedes:** `FORMAL_CORE_V2.md` where the two differ.  
**Theory terminal:** `CLOSED_V2_1`  
**Date:** 2026-08-18

V2.1 absorbs the independent assumption audit from the parallel mathematical-completion lane. The central correction is that **dependency soundness guarantees safe over-approximate reopening, not graph-only minimality when conservative/spurious edges are allowed**. Minimality requires an explicit realizability/richness premise on the compatible semantics class.

All V2 definitions/results not changed below remain in force.

## 1. Support-sound dependency abstraction

For changed set `X`, let

\[
Aff_D(E,X)=
(X\cap Q_{cert}(E))
\cup
(Desc_D(X)\cap Q_{cert}(E)).
\]

### Definition 1 — support soundness

`D` is support-sound for semantics class `\mathfrak S` iff every support whose mutation may change validity of a certified claim is represented either by the claim itself being changed or by an ancestor path to that claim.

Support soundness permits conservative/spurious graph edges. It is not graph exactness.

### Theorem 1 — safe root-inclusive reopening

If `D` is support-sound and only `X` changes before invalidation, reopening every member of `Aff_D(E,X)` leaves no certification that may have been invalidated by the change.

#### Proof

For potentially invalidated certified `q`, either `q\in X`, hence it is in the first term, or support soundness supplies a changed ancestor in `X`, hence it is in the descendant term. `\square`

This is a **safety** result. It does not say every reopened descendant is actually invalid in the fixed semantics.

## 2. Soundness alone does not imply minimality

### Countermodel 2.1 — spurious dependency edge

Let `D` contain edge `x\to q`, while the admissible semantics class contains only a semantics in which `q` is supported solely by independent coordinate `y` and is invariant to changes in `x`.

`D` is support-sound because it omits no actual support; the edge is merely conservative. After changing `x`, a strategy that preserves `q` is sound for this class. Therefore reopening every graph descendant is not inclusion-minimal.

Thus

\[
\boxed{
\text{support soundness}\not\Rightarrow\text{graph-descendant minimality}
}
\]

when spurious edges are permitted.

The same observation applies to a directly changed certified root if the declared class restricts the allowed change so that the prior certification is known invariant. Uniform minimality therefore needs an adversarial-realizability premise for every member of the affected set, not only descendants.

## 3. Affected realizability

### Definition 3 — affected-realizable compatible class

A graph-compatible semantics class `\mathfrak S_D` is **affected-realizable** for `(E,X)` when, for every

\[
q\in Aff_D(E,X),
\]

there exists a semantics `\sigma_q\in\mathfrak S_D` and an admissible change of the declared changed set `X` such that:

1. the pre-change certification of `q` is valid;
2. all information visible to the graph-only repair strategy (`D`, `X`, pre-change certification) is unchanged;
3. if `q\in X`, the admissible direct change can invalidate the old certification of `q`; otherwise at least one path from `X` to `q` represents necessary support;
4. the chosen change invalidates that direct/necessary support and hence the old certification of `q`.

Affected realizability is a minimax/richness assumption. It is not implied by support soundness.

### Theorem 4 — uniform graph-only minimality under affected realizability

Let `D` be support-sound and `\mathfrak S_D` affected-realizable for `(E,X)`. Any repair strategy that:

- observes only `D`, `X`, and pre-change certification; and
- must be sound for every semantics in `\mathfrak S_D`

must invalidate or revalidate every member of `Aff_D(E,X)`. Consequently root-inclusive affected-set reopening is inclusion-minimal among uniformly sound graph-only strategies for this class.

#### Proof

Assume a uniformly sound strategy preserves some `q\in Aff_D(E,X)` without revalidation. Affected realizability supplies `\sigma_q` with exactly the same graph-visible information in which the declared change invalidates `q`. The graph-only strategy cannot distinguish this semantics, so it preserves the stale certification there, contradicting uniform soundness. Therefore every affected member must be invalidated/revalidated. The affected-set strategy changes no certification outside `Aff_D(E,X)`, so it is inclusion-minimal. `\square`

### Corollary 4.1

Full reset is uniformly sound under the same premises but strictly non-minimal whenever a certified claim exists outside `Aff_D(E,X)`.

### Boundary

No claim is made that a real ORION dependency graph is exact or that its admissible semantics class is affected-realizable. Those are empirical/modeling obligations. Where realizability is unknown, P6 retains the safety theorem but not the minimality conclusion.

## 4. Preservation certificates under conservative graphs

A protected preservation certificate can establish that one member of `Aff_D(E,X)` is invariant under the exact change even when the graph conservatively connects it to `X`.

For unchanged affected descendant `q`, a valid certificate must bind exact changed set, claim/content/scope/epoch and an issuer outside the candidate transition's authority, and prove the old certificate derivation invariant under that change.

A directly changed certified root cannot **preserve the old certification by self-continuity**. It may end certified only through a new protected revalidation/re-certification derivation after the change. This distinguishes preservation from new certification.

With accepted sound preservation/revalidation proofs `K`, repair is minimal relative to `(D,X,K)` only for a compatible class that remains affected-realizable for every affected claim lacking an accepted proof.

## 5. Footprint fidelity

The V2 semantic-footprint definition is strengthened operationally.

### Definition 5 — read-footprint fidelity

A deterministic mechanic `m` is read-footprint faithful iff equal values on every declared semantic input imply equal requested effects, admissibility premises, written outputs, emitted obligations and failure terminal, unless a differing external input is explicitly declared.

Formally, for admissible `E,E'` agreeing on the declared semantic read interface,

\[
\tau_m(E)|_{SW(m)}=\tau_m(E')|_{SW(m)}
\]

and its side-condition outputs agree.

### Definition 6 — write-footprint fidelity

Every committed mutation must lie in `m`'s declared scientific write/effect scope. Hidden ambient mutation is inadmissible.

### Countermodel 6.1 — hidden read defeats declared separation

Suppose `m` declares no read of mutable ambient variable `z` but secretly branches on `z`; `n` writes `z`. Their declared read/write sets may appear disjoint, yet `m;n` and `n;m` can produce different scientific results. Declared sets without fidelity therefore do not establish commutation.

### Theorem 7 — history-aware commutation under faithful full separation

Stable contract: `P6.COMMUTE.RW_NONINTERFERENCE.V1`.

Let deterministic admissible `m,n` be read/write-footprint faithful and fully scientifically separated, including authority, provenance, obligations, dependency state, resources and declared external inputs. Whenever both orders are defined,

\[
\pi_{sci}(n(m(E)))=\pi_{sci}(m(n(E))),
\]

while ordered histories need only be equivalent under swaps of independent events.

#### Proof

Read fidelity makes each mechanic's behavior invariant to unobserved components; write fidelity and full separation prevent either from changing anything the other reads or writes. Hence each local result is order independent and all current scientific components coincide. Histories record opposite independent event order, so trace equivalence rather than literal equality is appropriate. `\square`

## 6. Results retained from V2

The following V2 results remain normative and unchanged:

- protected certificate-aware repair soundness, with the minimality qualifier adjusted to the realizability premise above;
- sequential authority non-escalation;
- hard residual-obligation persistence until an authorized discharge or typed non-success terminal;
- recursive-audit termination under well-founded rank/cycle detection;
- candidate-controlled self-admission countermodel;
- typed-erasure separation between bare computational semantics and epistemic admissibility;
- ordinary-transition, dependency-maintenance, self-adjusting-computation and typed-effect conservative special cases.

## 7. Executable regression obligations

`formal/check_theory_closure_v2_1.py` adds explicit regressions for:

1. root-inclusive safety;
2. the spurious-edge countermodel to minimality from soundness alone;
3. the affected-realizable minimax condition;
4. footprint-faithful commutation;
5. a hidden-read counterexample;
6. preservation/revalidation boundary for directly changed certified roots.

The earlier V2 checker remains useful but V2.1 is the normative P6 closure checker.

## 8. Final P6 theorem terminal

- `P6_SAFETY_THEORY = CLOSED_V2_1`
- `P6_MINIMALITY = CLOSED_UNDER_AFFECTED_REALIZABILITY`
- `P6_COMMUTATION = CLOSED_UNDER_FOOTPRINT_FIDELITY`
- `P6_BROAD_COMPONENT_NOVELTY = REJECTED`
- `P6_THEORY = FINISHED_V2_1`

The correction strengthens the paper because it distinguishes conservative dependency over-approximation from robust minimax necessity rather than treating every recorded edge as semantically realizable.
