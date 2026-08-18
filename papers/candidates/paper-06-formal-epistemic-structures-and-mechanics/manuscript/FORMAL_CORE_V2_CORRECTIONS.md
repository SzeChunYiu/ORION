# P6 formal core V2 corrections

**Candidate:** Formal Epistemic Structures and Mechanics  
**Date:** 2026-08-17  
**Relationship to V1:** normative addendum; all V1 definitions/results not changed below remain in force  
**Authority:** formal working object; novelty and ORION-faithfulness remain `CANNOT_CHECK`

## 1. Why this addendum exists

The V1 formal core correctly separates selective reopening, scientific-projection commutation, trace equivalence, non-escalation, recursive descent and protected promotion roots. Adversarial review found one missing premise in the graph-only minimality theorem and one premise that should be explicit in the commutation theorem.

This file narrows those claims. It does not add promotion authority.

## 2. Support-sound dependency graphs

Let `D` be a directed dependency abstraction over state coordinates and claims. For changed set `X`, write `Desc_D(X)` for strict graph descendants.

### Definition V2.1 (support soundness)

`D` is support-sound for semantics class `S` when every support whose mutation may change the validity of a certified claim is represented by an ancestor path to that claim.

Soundness permits conservative/spurious edges. It is not graph exactness.

### Theorem V2.1 (safe downstream reopening)

Let `D` be support-sound for `S`. Suppose only coordinates/claims in `X` change before invalidation. Reopening every certified claim in `Desc_D(X)` leaves no claim certified whose validity may have been invalidated by that change.

#### Proof

Take any certified claim `q` that may have been invalidated by the change. Support soundness supplies an ancestor path from some changed element $x\in X$ to `q`; hence $q\in\operatorname{Desc}_D(X)$. The reopening operator removes its certified terminal. Therefore no potentially invalidated certification remains. $\square$

This is a safety theorem. It does not establish that every reopened descendant was actually invalid under the fixed semantics.

## 3. Countermodel to minimality from soundness alone

### Countermodel V2.1 (spurious edge)

Let `D` contain `x -> q`. Let the admissible semantics class contain only a semantics in which `q` is supported by independent coordinate `y` and is invariant under changes to `x`.

`D` is support-sound: no actual support is omitted. The edge `x -> q` is conservative. After changing `x`, preserving `q` is sound. Therefore reopening `q` is not inclusion-minimal for this fixed class.

Consequently:

\[
\text{support soundness alone}
\not\Rightarrow
\text{inclusion-minimal descendant reopening}.
\]

The V1 minimality wording is superseded by the robust theorem below.

## 4. Robust graph-only minimality

### Definition V2.2 (path realizability for a changed set)

A graph-compatible semantics class `S_D` is path-realizable for changed set `X` and certified state `E` when, for every certified claim

\[
q\in\operatorname{Desc}_D(X),
\]

there exists a semantics $\sigma_q\in\mathfrak S_D$ and a change of `X` admissible under that semantics such that:

1. the initial certificate of `q` is valid;
2. at least one path from `X` to `q` in `D` represents necessary support in `sigma_q`;
3. the changed value invalidates that necessary support and therefore invalidates `q`;
4. the graph and all information available to the reopening strategy are unchanged.

This is a richness/realizability condition on the admissible class, not a property implied by graph soundness.

### Theorem V2.2 (uniform graph-only minimality under path realizability)

Let `D` be support-sound and let `S_D` be path-realizable for `X`. Any reopening strategy that:

- observes only `D`, `X`, and the pre-change certification state; and
- must be sound for every semantics in `S_D`

must reopen every certified claim in `Desc_D(X)`. Thus descendant reopening is inclusion-minimal among uniformly sound graph-only strategies for that class.

#### Proof

Assume a uniformly sound graph-only strategy preserves some certified $q\in\operatorname{Desc}_D(X)$. Path realizability supplies a semantics `sigma_q` compatible with exactly the same observed graph/state information in which the changed support along a path from `X` is necessary and the change invalidates `q`. Because the strategy observes no information distinguishing `sigma_q`, it preserves `q` there as well, leaving a stale certification. This contradicts uniform soundness. Hence every descendant must be reopened. Since descendant reopening changes no certification outside the descendant set, it is inclusion-minimal. $\square$

### Corollary V2.2.1

Full reset is uniformly sound under the same premises but is strictly non-minimal whenever a certified claim exists outside `Desc_D(X)`.

### Boundary

This theorem is robust/minimax relative to a model class. It does not claim that a real ORION dependency graph is complete, path-realizable, or free of conservative edges.

## 5. Footprint-faithful mechanics

### Definition V2.3 (read-footprint fidelity)

A deterministic mechanic `m` is read-footprint faithful when, for all admissible states `E,E'`,

\[
E|_{R_m}=E'|_{R_m}
\Longrightarrow
\tau_m(E)|_{W_m}=\tau_m(E')|_{W_m}.
\]

Its requested effects, emitted obligations, authority/provenance requirements and failure terminal must likewise depend only on declared inputs or explicitly registered external inputs.

### Definition V2.4 (write-footprint fidelity)

A mechanic is write-footprint faithful when every committed state/effect mutation lies in its declared write/effect scope. Undeclared mutation is inadmissible even if the final value appears correct.

### Definition V2.5 (strong operational separation)

Mechanics `m,n` are strongly operationally separated when:

\[
W_m\cap(R_n\cup W_n)=\varnothing,
\qquad
W_n\cap(R_m\cup W_m)=\varnothing,
\]

both are footprint faithful, and neither changes an authority, provenance object, obligation, dependency edge, invariant input, resource state or hidden ambient object consumed by the other.

## 6. History-aware commutation

### Theorem V2.3 (projection commutation under footprint fidelity)

Let `m,n` be deterministic admissible mechanics that are strongly operationally separated. Whenever both sequential compositions are defined,

\[
\pi_{sci}(\tau_n(\tau_m(E)))
=
\pi_{sci}(\tau_m(\tau_n(E))).
\]

Their ordered audit histories need not be identical. If their commit events are independent, the histories are equivalent under the trace congruence generated by swapping adjacent independent events:

\[
H_{mn}\equiv_I H_{nm}.
\]

#### Proof

Read-footprint fidelity ensures that each mechanic observes the same declared inputs in either order. Write-footprint fidelity and strong separation ensure disjoint committed effects and prevent changes to shared side conditions. Therefore each coordinate and scientific side structure has the same final value in both orders. The history records different event order; one independent adjacent swap relates the two traces. $\square$

### Counterexample V2.3.1

If `m` declares no read of `x` but accesses `x` through hidden mutable ambient state, a preceding write by `n` can alter `m`'s result although the declared footprints appear separated. Declared sets without enforcement therefore do not prove commutation.

## 7. Executable regression link

`formal/check_assumption_regressions_v2.py` and `formal/assumption_countermodels_v2.jsonl` freeze:

- the safe reopening result;
- a path-realizable stale-certificate witness and a spurious-edge negative control;
- declared-write and separation positive/negative controls;
- scientific-projection equality with distinct trace-equivalent histories;
- authority narrowing/escalation, recursive descent/cycle and self-authorization controls.

The bounded artifacts support the theorem wording but do not prove the unbounded results.

## 8. Claim boundary

P6 may currently claim that the corrected formal object and proofs/checks exist. It may not claim that:

- dependency graphs are exact in ORION;
- selective reopening is novel;
- footprint fidelity has been established for every ORION mechanic;
- the calculus is a conservative embedding of all donors;
- the formal structure improves real scientific systems;
- P6 is a distinct publishable paper.
