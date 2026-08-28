# ORION11.COSTED_EPISTEMIC_ORDERING.v1 — THEORY

`scientific_authority_delta: NONE`
**Status: PREREGISTRATION — DESIGN ONLY, NOT EXECUTED.** No result exists. Nothing
in this file is evidence. `RESULT.json`, `CLAIM_DISPOSITION.md` and
`independent_checker/` are deliberately absent and must be produced *after* the
protocol is frozen and executed, by a different author than this document.

- **Successor identity (issue #1608):** `ORION11.COSTED_EPISTEMIC_ORDERING.v1`
- **Candidate identity (ledger #1615 Priority 4):** `ORION11.COSTED_RESPONSIBILITY_ORDERING.v1`
  — recorded there as `HYPOTHESIS_ONLY` with **no scientific authority**.
- **Predecessor evidence:** `experiments/r4-faithful-comparator-v1/` (PR #1603),
  verdict `H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION`.
- **Packet layout:** issue #1608, "Mandatory successor packet layout".

---

## 1. Why this successor exists

R4 removed the comparative mechanism-necessity reading of `ORION-11.NECESSITY.V2.2.4`:
a faithful Active-VOI comparator granted the same ordered search matches ORION on
both registered components (hidden-shift success `1.00000`, forbidden high-level
mutation `0.00000`; McNemar `b/c = 0/0`).

What R4 left is a **cost** observation on one frozen world family: among arms
clearing both gates, ORION spends mean `1.8341` intervention units against `2.6676`
for `activevoi_search_admitted_parent` (ratio `0.6876`) under an identical `4.0`
budget. That gap is not a result. It is a question: *is level-ordered diagnosis
cheaper than the alternatives at equal success and safety, and if so, why?*

This packet exists to answer that question in a way that can **fail**.

## 2. The priced-ordering theorem

### 2.1 Setting

Exactly one latent repair class `i* ∈ {1,…,n}` is correct. Let `p_i = P(i* = i)`
with `Σ p_i = 1`. Checking class `i` costs `c_i > 0` and, if `i = i*`, reveals it and
terminates the search. Checks are serial. For an ordering `σ` (a permutation of the
classes) the expected cost is

    E[C(σ)] = Σ_k p_{σ(k)} · Σ_{j ≤ k} c_{σ(j)}.

### 2.2 Theorem A (unconstrained priced ordering)

*`E[C(σ)]` is minimized by any `σ` sorting the classes in nonincreasing `p_i / c_i`.*

**Proof (adjacent exchange).** Take adjacent positions `k, k+1` holding classes `i`
and `j`, and let `S = Σ_{m<k} c_{σ(m)}` be the cost already committed. Only two terms
of the sum depend on the order of `i` and `j`:

- `i` first: `p_i (S + c_i) + p_j (S + c_i + c_j)`
- `j` first: `p_j (S + c_j) + p_i (S + c_j + c_i)`

The difference (`i` first minus `j` first) is `p_j c_i − p_i c_j`. Hence placing `i`
first is no worse exactly when `p_j c_i ≤ p_i c_j`, i.e. `p_i / c_i ≥ p_j / c_j`.
Every permutation can be transformed into the sorted order by a finite sequence of
adjacent transpositions, each weakly reducing `E[C]`; therefore the sorted order is
optimal. ∎

This is the classical adjacent-exchange (Smith-ratio) argument. **It is donor-owned
prior mathematics and is claimed here only as the correct baseline, not as a
contribution.**

### 2.3 The responsibility filtration

ORION's `K/W/M` levels induce a filtration `F_0 ⊆ F_1 ⊆ … ⊆ F_L`, where `F_ℓ` is the
set of repair classes at epistemic level at most `ℓ`. Write `L(i)` for the level of
class `i`.

**Assumptions.**

- **(A1) Noninterference.** Check outcomes are conditionally independent given `i*`;
  checking a class at level `ℓ` updates the posterior over higher levels only by
  conditioning on "not this class".
- **(A2) Veto-monotonicity.** An admissible ordering may open level `ℓ+1` only after
  every class in `F_ℓ` has been excluded. Admissible orderings are exactly the
  topological orderings of the filtration.
- **(A3) Safety.** Mutating at level `ℓ' > L(i*)` before `F_{L(i*)}` is exhausted is a
  *forbidden high-level mutation*, carrying a penalty outside the cost budget (it is
  a gate failure, not a priced outcome).
- **(A4) Nonnegative cost.** `c_i > 0` for all `i`.

### 2.4 Theorem B (level-monotone optimality, constrained)

*Under (A1)–(A4), the expected-cost-optimal **admissible** policy processes levels in
order and, within each level, sorts by nonincreasing `p_i / c_i`.*

**Proof.** (A2) makes the admissible set exactly the topological orderings. Within a
level all classes are mutually incomparable, so Theorem A's adjacent exchange applies
verbatim and forces the `p/c` order inside each level. Across levels, any adjacent
transposition that would move a level-`ℓ+1` class before an unexhausted level-`ℓ`
class leaves the admissible set, so no such exchange is available. ∎

### 2.5 Theorem C (the price of the filtration) — the falsifier

*Level-monotone ordering coincides with the unconstrained optimum of Theorem A if and
only if the filtration is **ratio-aligned**:*

    min_{i ∈ F_ℓ} (p_i / c_i)  ≥  max_{j ∉ F_ℓ} (p_j / c_j)   for every ℓ.

*If the filtration is ratio-aligned, level-monotone ordering is exactly the flat
`p/c` ordering and confers **no cost advantage whatsoever** over a flat `p/c`
baseline. If it is not ratio-aligned, the unconstrained `p/c` order is strictly
cheaper than any admissible order, and the difference is the price paid for (A2)
veto-monotonicity — a cost ORION **pays**, not one it saves.*

**Proof.** Immediate from Theorems A and B: the sorted-by-`p/c` order is admissible
precisely when it is topological for the filtration, which is the stated condition.
Otherwise the optimum lies outside the admissible set, and by Theorem A every
admissible order has strictly greater expected cost. ∎

### 2.6 What Theorem C means for this successor — read this before designing gates

Theorem C says the level filtration can **never** make ORION cheaper than flat `p/c`
ordering. In the ratio-aligned case they tie; otherwise ORION is strictly more
expensive. Therefore:

> **Any cost advantage ORION shows over faithful Active-VOI must be attributable to
> Active-VOI ordering *worse than* `p/c`, not to level-monotonicity ordering *better
> than* `p/c`.**

This is a genuine and severe prediction, and it is the reason a simple `p/c` donor
baseline is mandatory (#1615): if `gain_per_cost_greedy` matches or beats ORION on
cost at equal success and safety — which the theory says it should — then the
"level-ordering economy" residual left by R4 is **not an ORION mechanism property**
and the empirical mechanism claim dies. The theory predicts its own empirical
falsification, and the experiment is built to observe it.

The remaining live possibility, and the only one that would leave anything standing,
is the **joint** one: ORION pays a bounded ordering premium over unconstrained `p/c`
(quantified by Theorem C) and in exchange holds `forbidden_high_level_mutation_rate
= 0` where the unconstrained baselines do not. That is a *safety-priced-ordering*
statement, not a cost-superiority statement, and it must be tested as such.

## 3. Hypotheses

- **H1 (cost, primary).** At equal success and safety, ORION's paired expected-cost
  ratio against faithful Active-VOI is `< 0.80` with a 95% upper confidence bound
  `< 0.80`.
- **H2 (optimality gap).** On theorem-valid worlds ORION's mean cost is within
  `1.10×` the exact dynamic-programming optimum.
- **H3 (donor baseline — the discriminator).** ORION's cost is **not** lower than
  `gain_per_cost_greedy` at equal success and safety. *Theorem C predicts H3 holds;
  if it does, H1's advantage is a property of Active-VOI's ordering, not of ORION.*
- **H4 (safety pricing).** ORION holds `forbidden_high_level_mutation_rate = 0` on
  every world stratum while unconstrained `p/c` and flat VOI do not.
- **H5 (mechanism attribution).** Any ORION cost advantage **disappears** on the
  registered assumption-violation controls (one of A1–A4 broken at a time). If it
  persists there, the theorem is not the explanation and the mechanism story is wrong
  regardless of how favourable the headline numbers are.

## 4. Relationship to the retained and retracted ORION-11 results

- The internal `ORION-11.NECESSITY.V2.2.4` terminal is **retained** and is not
  re-litigated here. R4's anchor gate reproduced all four unchanged arms at the
  committed rates.
- The comparative mechanism-necessity reading is **retracted** and is not revived by
  any outcome of this packet. A favourable outcome here would license a *cost/safety*
  statement only.
- R4's replication arm remains **`CANNOT_CHECK`**
  (`INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ`). This packet does
  not read it, does not depend on it, and does not convert it to a pass or a failure.
  Its instrument fault is fixed on a separate branch.
- No frozen ORION-11 byte is modified to run this successor (issue #1608 standing rule).

## 5. Scope limits fixed in advance

New world family, generated independently of the R4 worlds. No outcome of this packet
transfers to naturalistic tasks, to model-general settings, or to any other paper. A
result confined to one stratum is **intermediate**, not terminal: it obliges a revival
iteration that either extends the working regime or attributes the failure, and it may
never be reported as a bounded success on its own.
