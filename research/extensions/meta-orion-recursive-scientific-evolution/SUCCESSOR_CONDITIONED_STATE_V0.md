# Successor-Conditioned Scientific State V0

**Status:** no-man's-land research target; protocol design only.

**Parent programme:** #625

**Prerequisites:** #627 interaction-only residual frozen on branch; #628 exact RSSI benchmark in development.

This document deliberately does **not** introduce a new claimed mathematical primitive. Sufficient statistics, bisimulation, predictive-state representations, event sourcing, dynamic assurance and epistemic-state replication are direct parents. The scientific question is whether their strongest forms are sufficient for **recursive scientific-standing migration** under protected authority, and whether a typed ORION state yields any future-value or efficiency advantage beyond them.

---

## 1. Why current-state correctness is insufficient

A framework transition can produce a state `F1` that is perfectly correct on every current task and every current standing check, while silently discarding a distinction that becomes load-bearing only after a later framework change.

Therefore the target is not merely:

```text
MigrationCorrect(F0 -> F1)
```

but:

```text
FutureScienceSufficient(F1_state | admissible future framework changes, kappa, B)
```

where `kappa` is the protected scientific constitution and `B` is the registered future resource/information bound.

A first-generation benchmark that never exposes a later change can reward an epistemically lossy migration.

---

## 2. Future-equivalence criterion

Let `h` and `h'` be two complete scientific histories and let a migration/compression map produce current scientific states:

```text
phi(h)  = z
phi(h') = z'
```

For a registered family of future scientific/framework transition sequences `U_B`, define `z` and `z'` as **future-science equivalent** when every admissible future sequence produces the same protected scientific consequences:

```text
z ~=_(kappa,B) z'
```

iff for every `u in U_B`:

- the same scientific claims remain supported/verified/authorized/reopened/invalidated/unknown;
- the same evidence routes remain admissible;
- the same hard obligations are discharged or reopened;
- the same negative knowledge is applicable or stale;
- the same protected authority decisions are available;
- the same justified-reach contracts are reachable under the declared budget.

This is intentionally analogous to task-relative sufficiency/bisimulation. ORION does not claim first ownership of that mathematics.

A migration is **future-science sufficient** on the registered family only if histories collapsed to the same migrated state are future-science equivalent.

---

## 3. Exact discriminator form

The benchmark should construct pairs with:

```text
CurrentObservable(F1_a) = CurrentObservable(F1_b)
CurrentTaskScore(F1_a)  = CurrentTaskScore(F1_b)
CurrentStanding(F1_a)   = CurrentStanding(F1_b)
```

but a protected future transition `u*` such that:

```text
StandingAfter(F1_a, u*, kappa) != StandingAfter(F1_b, u*, kappa)
```

A current-state representation that merges the pair is scientifically insufficient for recursive evolution.

A full-history/event-log baseline should normally retain the distinction. ORION earns no value merely for doing the same with more stored state.

---

## 4. D3/D4 delayed pair families

### DPAIR-1 — hidden evidence-route dependency debt

At `F1`, two claims have identical proposition, answer, visible standing and confidence.

- History A: current authorization depends on evidence route `r_old` whose semantic applicability is scoped to representation family `S_old`.
- History B: current authorization has an independent evidence route `r_independent` with no such scope.

The current surface does not require distinguishing them.

At D3, a representation/operator evolution exits `S_old`.

Gold:

```text
A -> REOPEN
B -> PRESERVE/TRANSPORT (according to exact witness)
```

A state that retained only `AUTHORIZED` loses the future distinction.

### DPAIR-2 — negative-cause debt

At `F1`, two negative-knowledge records have the same surface conclusion:

```text
method m failed on context c
```

- History A failed because required operator `q` did not exist.
- History B failed because a hard invariant makes `m` invalid even if `q` exists.

At D3, `q` is introduced.

Gold:

```text
A -> negative knowledge context-stale; route reopens
B -> negative knowledge remains applicable
```

A memory that stores only a failure label or method blacklist is future-insufficient.

### DPAIR-3 — authority-origin debt

At `F1`, two actions/claims are both `AUTHORIZED`.

- History A is authorized by a grant scoped to framework/schema version `F1/S1`.
- History B is authorized by an independently re-established grant whose scope explicitly transports across registered successor `S2`.

At D3, the framework migrates to `S2`.

Gold:

```text
A -> REOPEN / authority stale
B -> authority remains valid under explicit transport
```

Current authorization labels are identical; future authority is not.

### DPAIR-4 — obligation provenance debt

Two claims have the same current VERIFIED standing and identical evidence payloads.

- History A discharged obligation `o` because an earlier objective made one measurement dimension irrelevant.
- History B discharged `o` under a stronger measurement route independent of that objective.

At D3, objective evolution makes the formerly irrelevant dimension load-bearing.

Gold differs despite identical current status.

### DPAIR-5 — revision-path debt

Two framework states expose identical current objects and task behavior but were reached by different valid revision orders.

Known path-dependent revision/categorical countermodels establish that order information can matter. The benchmark should make one later transition expose that difference in scientific standing.

A path-erased state is future-insufficient on this family.

---

## 5. Strong baselines

The benchmark is invalid if ORION is compared only with a lossy current-state summary.

Mandatory arms:

```text
S0 current-standing-only summary
S1 claim/evidence dependency graph
S2 dynamic-assurance / change-impact graph
S3 immutable full event log + deterministic replay
S4 ESR-style immutable evidence log + belief lineage / semantic rollback
S5 donor meta-product state with authority/version + negative-history context
O  ORION typed standing state
```

Where possible, `S3` is the fidelity ceiling: it keeps the whole history. A claim that ORION is more scientifically correct than a complete history baseline requires a real difference in inference/authority semantics, not missing information in the comparator.

---

## 6. What ORION could still earn

Several outcomes are scientifically distinct.

### Outcome A — full log / donor state matches ORION

Terminal:

`FULL_HISTORY_OR_DONOR_STATE_SUFFICIENT`

Interpretation: ORION's typed state is an engineering representation, not a new scientific capability.

### Outcome B — ORION matches fidelity at lower cost

Possible bounded result:

`TYPED_STATE_EFFICIENCY_VALUE`

Requires prospectively frozen costs for:

- retained bytes/objects;
- reconstruction/replay cost;
- standing-revalidation cost;
- future-transition decision cost;
- false reopen/preserve rates.

This is an efficiency/integration result, not new epistemology.

### Outcome C — donor product has the information but still makes invalid standing decisions

Candidate stronger result:

`SCIENTIFIC_STANDING_SEMANTICS_INCREMENTAL_VALUE`

Only defensible if the donor product is given the same history/fields and its failure arises from the missing scientific obligation/authority composition rather than a weaker implementation.

### Outcome D — no current representation is sufficient under the registered future family

Then the correct result is not automatic framework invention. Register the missing discriminator/state distinction and run the recursive-atom/donor procedure again.

---

## 7. Successor-generation experiment

The strongest test uses D0–D4:

```text
D0: F0 learns/proposes F1
D1: external acceptance of F1
D2: fresh current-generation science
D3: new framework/scientific transitions requiring preserved distinctions
D4: protected evaluation of successor F2 and inherited standing
```

Compare F0 and F1 not only as solvers, but as **successor generators**.

A positive recursive claim requires:

```text
DirectImprove(F1,F0) on D2
and
MetaImprove(F1,F0) on D3/D4
and
StandingIntegrity(F1 lineage) on D4
```

No protected D4 information may flow backward into F1 or its state-compression policy.

---

## 8. Non-compensatory metrics

### Current-generation

- D2 justified task success;
- invalid promotion rate;
- false reopen rate;
- unknown calibration;
- cost.

### Future-state sufficiency

- future-equivalence pair accuracy;
- lost-load-bearing-distinction count;
- future standing error rate;
- stale negative-knowledge error;
- stale authority error;
- obligation-drop error;
- path-erasure error.

### Recursive generation

- D4 justified successor success;
- inherited-standing integrity after F2;
- protected-evaluator violation;
- state/history retention cost;
- replay/revalidation cost.

A task-score gain cannot compensate for invalid scientific promotion.

---

## 9. No-man's-land boundary

After RSE-0 saturation, no direct prior identified in the programme jointly claims and prospectively evaluates all of the following as one bounded scientific-agent experiment:

1. recursive change to the scientific epistemic framework rather than only code/workflow/model/objective;
2. explicit migration of heterogeneous scientific standing including claims, obligations, negative knowledge and authority;
3. matched full-history/dynamic-assurance/ESR/donor-meta-product baselines;
4. same-current-state / different-future-standing pairs;
5. disjoint D3/D4 successor-generation evaluation;
6. non-compensatory protected scientific authority.

This is an **unoccupied experimental question after the recorded saturation**, not a declaration that no related work exists or that ORION has already solved it.

A stronger parent satisfying this exact conjunction reopens RSE-0 immediately.

---

## 10. Next executable tranche

Do not add another framework abstraction first.

Implement DPAIR-1 through DPAIR-3 in the exact RSSI harness, then add:

- current-state-only baseline;
- full-event-log reconstruction baseline;
- coordinated donor-meta-product baseline;
- byte/cost accounting;
- hidden seed regeneration.

Only if an interaction residual survives those arms should ORION implement a learned or adaptive framework-evolution controller.