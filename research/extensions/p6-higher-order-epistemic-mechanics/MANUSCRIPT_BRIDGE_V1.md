# Higher-order epistemic mechanics — successor manuscript bridge V1

**Status:** additive successor material only. This document does not alter the content-bound P6 V2.1 peer-review package and does not claim a new peer-review-ready paper.

## 1. Motivation: from method mechanics to mechanics of revision

The existing P6 formalism treats a mechanic as a typed transformation with declared state ownership, obligations, effects, failure terminals and composition conditions. The MethodFibre extension adds claim-relative structural reduction and equivalence. The next research question is higher order: **when an anomaly appears, which mechanic is scientifically admissible to apply to the epistemic system itself?**

Recent work on M-open model discovery, representational-regime change, objective evolution, state/interface adequacy, rational metareasoning, uncertainty containment and social evidence makes one point increasingly difficult to avoid: an observed failure is compatible with several different responsible layers. The failure alone is not a write permission.

The tranche implemented here deliberately does not encode a universal taxonomy of those layers. It instead introduces the smaller mathematical contract needed to state and falsify a locality principle.

## 2. Claim-relative higher-order mechanic

For a declared claim/task `C`, define a candidate higher-order mechanic as a content-bound partial transition contract

```text
m_C = (Read, Write, Pre, Req, Pres, Auth, Cost)
```

where:

- `Read(m)` is the set of epistemic coordinates inspected;
- `Write(m)` is the set that may be materially changed;
- `Pre(m)` are applicability preconditions;
- `Req(m)` are hard evidence / validation obligations;
- `Pres(m)` are preservation obligations;
- `Auth(m)` are externally supplied authority domains required to perform the transition;
- `Cost(m)` is declared resource cost.

`Cost` is intentionally not authority currency. A cheap broad rewrite is not less epistemically invasive merely because it is cheap.

The executable record is `HigherOrderEpistemicMechanic.v1` in `src/orion/transfer/v2/higher_order_epistemic_mechanics.py`. Every record is content-digested and mechanically rejects `can_self_authorize=true`.

## 3. Fail-closed admissibility

A mechanic is assessed under explicit obligation states:

```text
SATISFIED / VIOLATED / UNRESOLVED
```

with assessment terminal:

```text
ADMISSIBLE / BLOCKED / UNRESOLVED.
```

Known violated hard requirements, forbidden material writes, or absent required authority block. Missing or explicitly unresolved obligation evidence remains unresolved. This separates **“not currently licensed”** from **“scientifically refuted.”**

## 4. A bounded revision-invasiveness preorder

Tranche 1 defines a deliberately conservative, claim-relative necessary preorder:

```text
m1 ⪯_C m2
```

only when:

```text
Write(m1) ⊆ Write(m2)
Pres(m1)  ⊇ Pres(m2)
Auth(m1)  ⊆ Auth(m2)
```

for the same declared claim `C`.

Strict comparison requires at least one strict component. This is **not** claimed to be the final semantics of scientific minimal change. It is an executable design relation whose purpose is to expose countermodels and determine whether richer semantic witnesses are required.

## 5. Minimal admissible revision

Given candidate mechanics `A_C`, define the bounded minimal set

```text
Min_C(A_C) = {m ∈ A_C : no admissible m' is strictly less invasive than m}.
```

The implementation has four non-authorizing selection outcomes:

- `UNIQUE_MINIMUM`;
- `MULTIPLE_MINIMA`;
- `NO_ADMISSIBLE`;
- `UNRESOLVED`.

Two guards are load-bearing.

### 5.1 Incomparable minima are not tie-broken away

If a measurement repair and an execution repair are both admissible but neither is ordered below the other, the result is `MULTIPLE_MINIMA`; no mechanic is selected simply because it is cheaper, more confident, or listed first.

### 5.2 A narrower unresolved candidate blocks escalation

Suppose model-class expansion is admissible but a strictly narrower evidence-route repair remains unresolved. The system does **not** promote the model rewrite as the minimal justified response. The selector returns `UNRESOLVED` with `NARROWER_UNRESOLVED_CANDIDATE`.

This is the first executable form of the programme principle:

> missing discrimination evidence is not permission to escalate the epistemic write footprint.

## 6. Frozen countermodels

`COUNTERMODELS_V1.json` binds six deterministic cases:

1. evidence acquisition dominates broader model rewrite even when the broader rewrite is cheaper;
2. measurement and execution repairs are incomparable minima;
3. unresolved narrow evidence repair blocks broader model escalation;
4. missing objective-mutation authority blocks a zero-cost objective rewrite;
5. candidate write access to a protected evaluator is blocked;
6. a clean single narrow repair reaches a unique minimum.

`COUNTERMODEL_SUMMARY_V1.json` reports 6/6 expected outcomes and terminal `TRANCHE1_FORMAL_COUNTERMODELS_GREEN`. This terminal grants neither scientific authority nor Self-ORION adoption.

## 7. What the countermodels establish — and what they do not

They establish that the implementation is non-vacuous on the frozen finite panel: it can accept a clean narrow transition, preserve incomparable alternatives, fail closed on missing authority, and refuse a broad escalation when a narrower unresolved candidate exists.

They do **not** establish that:

- the set-based preorder is the correct universal theory of scientific minimality;
- every scientific failure admits a useful minimal revision;
- the provisional `K/W/M/F/Q/...` coordinate vocabulary is complete;
- minimal revision is globally optimal under all costs and future consequences;
- Self-ORION improves by using this calculus;
- the formal object is novel relative to belief revision/effect systems/rational metareasoning.

Those remain #452/#454/#463/#455 questions.

## 8. Cross-paper consequences if the formalism survives

### P1 — Recursive Epistemic Reconstruction
P1 already contains empirical pressure for lower-level exclusion before high-level mutation on a frozen mechanical family. A successor P1 claim could map its evidence/execution/formulation/search-universe actions into higher-order mechanics, but the present P1 peer-review result must not be broadened by this bridge.

### P3 — Global Knowledge Portrait
Representation alignment / obstruction can eventually supply preservation or reconstruction witnesses for frame changes. P3 mapping evidence cannot itself authorize a higher-order revision.

### P4 / P8 — Verification and epistemic authority
`Auth(m)` must consume their authority semantics rather than invent a parallel permission system. The present tranche only checks for an externally supplied authority domain.

### P5 — Self-ORION
The intended future discriminator is whether revision-level locality reduces false broad self-changes and harmful transfer. No P5 manuscript claim changes until #455 executes a prospectively frozen experiment.

### P7 — Epistemic navigation
A representation-changing route may alter the available mechanic set and therefore the local revision order. P7 can supply transition/reopen semantics but not scientific adoption authority.

### P9/P10 successors
A learned model may rank or propose mechanics, but probability or embedding similarity cannot create admissibility, minimality evidence, novelty, or authority.

## 9. Next formal tranche

Before extending the calculus, #463 should pressure whether the following can be expressed with existing formal parents rather than new ORION vocabulary:

1. semantic witnesses for revision ordering beyond write-set inclusion;
2. responsibility states with competing causes rather than a flat class label;
3. interface/state sufficiency and representation reconstruction;
4. constrained value of computation with hard obligations;
5. uncertainty-containment mechanics that change admissible scope without rewriting the model;
6. correlated social reports / epistemic independence;
7. composition of diagnostic -> revision -> preservation/reopening -> protected authority.

If those pieces do not admit one coherent calculus, they should remain separate modules. A smaller mathematics is an acceptable and preferred outcome over a forced grand theory.
