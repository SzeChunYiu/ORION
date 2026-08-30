# ORION06.CLAIM_PRESERVING_RECOVERY.v1 — causal coverage and no-repair certificates

**Paper:** ORION-06 — Recursive Recovery  
**Status:** `THEORY_PROVED__CROSS_DOMAIN_VALUE_UNTESTED`  
**Scientific authority delta:** `NONE`  
**Novelty authority:** `NONE`

This packet formalizes a boundary already implicit in ORION-06: a failed result is not
"recovered" merely because a later run is favourable. A recovery must preserve the
load-bearing claim identity and intervene on causes capable of changing the failed
predicates.

## 1. Fixed claim identity

Let a scientific claim identity `I` fix the question, population/domain, estimand,
protocol semantics, primary metric, threshold/gate and protected evidence contract whose
meaning must remain unchanged for an attempted repair to count as repair of the same claim.

Let `P = {p_1,...,p_n}` be the load-bearing predicates that must all hold for the claim's
success terminal. After an adverse run, let

`F = {p in P : p is false}`

be the failed predicate set.

A candidate repair action is **identity-preserving** only if it leaves `I` fixed. Changing a
threshold, comparator, protected corpus, outcome definition or success predicate after the
failure may define a scientifically useful successor, but it is not repair of the old
identity.

## 2. Causal locality model

Let `A_I` be the allowed identity-preserving repair actions. For each action `a`, let
`D(a) subseteq P` be the predicates whose truth value that action can causally affect under
the declared mechanism. Equivalently, for a predicate `p`, define its admissible repair
ancestors

`H(p) = {a in A_I : p in D(a)}`.

The load-bearing locality assumption is:

> If a repair set contains no action in `H(p)`, then the intervention leaves `p` unchanged.

This is deliberately only a necessary-causation model. An ancestor action may fail to repair
a predicate; ancestry alone does not guarantee success.

## 3. Theorem 1 — ancestor-hitting is necessary for claim-preserving recovery

If an identity-preserving repair set `S subseteq A_I` turns every failed predicate in `F`
true, then

`S intersect H(p) != empty`

for every `p in F`.

Equivalently, every valid repair is a **hitting set** of the failed predicates' admissible
ancestor families.

### Proof

Suppose some failed predicate `p` has `S intersect H(p)=empty`. By causal locality, applying
`S` cannot change `p`. Since `p` was false before the repair, it remains false afterward,
contradicting recovery of every failed predicate. ∎

This theorem is a falsifier: a reported repair that misses even one failed predicate's
causal-ancestor set cannot explain recovery of the old claim under the declared mechanism.

## 4. Corollary — no-repair certificate

If there exists a failed predicate `p in F` with

`H(p)=empty`,

then **no identity-preserving recovery exists** in the declared repair language.

The honest terminal is therefore one of:

- retain the adverse/negative result under the old identity;
- `CANNOT_CHECK` if the causal action map itself is unavailable;
- define a genuinely new successor identity whose scientific question or intervention
  language differs prospectively.

Increasing retries or searching longer inside the same action language cannot change this
logical obstruction.

## 5. Theorem 2 — minimum repair cost lower bound

Give every identity-preserving action a nonnegative cost `c(a)`. Define

`LB(F) = min_{S subseteq A_I : for all p in F, S intersects H(p)} sum_{a in S} c(a)`,

with `LB(F)=infinity` when no hitting set exists.

Then every successful identity-preserving repair has cost at least `LB(F)`.

### Proof

By Theorem 1 every successful repair lies in the feasible hitting-set family. `LB(F)` is the
minimum cost over that necessary family. ∎

This is a lower bound, not an optimal-repair theorem. Causal ancestors can be ineffective,
interact destructively, or create new failures, so realized repair cost may be strictly
larger.

## 6. Theorem 3 — dominated repair actions can be removed from the search language

Suppose actions `a` and `b` satisfy

`D(a) subseteq D(b)` and `c(b) <= c(a)`.

Then there exists a minimum-cost ancestor-hitting set that does not use `a` unless `a=b`.

### Proof

Take any feasible hitting set containing `a`. Replacing `a` by `b` preserves coverage of
every predicate previously hit by `a` and does not increase cost. Repeating removes all
strictly dominated actions from at least one optimum. ∎

This is a search reduction for the **necessary causal-coverage problem only**. It does not
say the dominating action is a better empirical repair after downstream interactions.

## 7. Identity-mutation theorem

Let `M` be an intervention that changes an identity-defining element of `I` after the
adverse outcome — for example the success threshold, primary endpoint, protected corpus or
meaning of a terminal. Even if the modified experiment succeeds, that success is not
logical evidence that the original failed claim was repaired, because the proposition being
evaluated is no longer the same proposition.

This is definitional rather than statistical: recovery is a relation between two states of
the **same** claim identity. An identity mutation may be valuable successor science, but its
result must be stored under a new identity and the old negative remains visible.

## 8. Consequences for recovery protocols

Before spending compute on a revival attempt, a mechanically auditable recovery packet
should therefore bind:

1. the exact old claim identity `I` and adverse terminal;
2. the failed predicate set `F`;
3. the allowed identity-preserving action set `A_I`;
4. a declared causal-effect map `D(a)` or explicit `CANNOT_CHECK` if it cannot be justified;
5. the ancestor-hitting lower bound and dominated-action reduction;
6. the selected repair actions **before** protected re-evaluation;
7. unchanged old thresholds/metrics/corpus plus the new result.

If the selected action set misses a failed predicate's ancestors, stop before protected
execution: the proposed lever cannot repair the declared failure under its own causal model.

## 9. Cross-domain successor

The planned Lean/mathlib + Defects4J + exact ORION benchmark should test more than recovery
rate. It should test whether the causal-coverage discipline predicts:

- which revival attempts are structurally incapable of repairing the old claim;
- false revival from identity mutation;
- unnecessary interventions beyond a minimum ancestor cover;
- verified recovery under objective native checkers;
- the cost gap between the hitting-set lower bound and realized repair.

Naive retry and generic donor/domain repair remain necessary comparators; the theorem does
not grant ORION empirical superiority.

## 10. Authority boundary

Earned: exact necessary conditions for claim-preserving recovery, a no-repair certificate,
a minimum causal-coverage cost lower bound, and a dominated-action search reduction.

Not earned:

- sufficiency of ancestor coverage;
- a causal graph for any particular historical ORION failure unless separately bound;
- cross-domain recovery benefit;
- superiority to naive retry, Active-VOI, debugging systems or research agents;
- external investigator authority, novelty or venue authority.

Generic causal ancestry and weighted hitting set are donor-owned mathematical primitives.

**Terminal:** `CLAIM_PRESERVING_CAUSAL_COVERAGE_PROVED__CROSS_DOMAIN_RECOVERY_UNTESTED`.
