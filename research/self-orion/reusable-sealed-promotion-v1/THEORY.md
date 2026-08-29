# Leakage-adjusted reusable sealed promotion

## 1. Setting

A campaign proceeds through adaptively chosen rounds `j=1,2,...`. Let `F_{j-1}` contain every public artifact released before round `j`: prior candidates, scores, one-bit decisions, negative history, costs, failures, and all earlier promotion receipts. Candidate `C_j`, its stopping time, and its requested evaluation may be arbitrary `F_{j-1}`-measurable functions.

Within evaluator epoch `e`, the protected sample is `S_e`. The candidate generator never receives `S_e`, raw protected labels, or unredacted evaluator traces. It may nevertheless learn about `S_e` through the released transcript `Z_{j-1}`. Reuse is therefore not free merely because the evaluator returns only pass/fail.

For each candidate there are three non-compensatory statistical components:

```text
H_F,j: protected fresh benefit is at or below the registered minimum;
H_R,j: retention loss exceeds the registered tolerance;
H_H,j: harmful transfer is at or above the registered maximum.
```

Promotion requires rejection of all three component nulls, plus deterministic resource, custody, authority, byte-identity, and receipt gates.

A candidate is scientifically bad whenever at least one component null is true.

## 2. Approximate max-information assumption

For the protected sample and previously released transcript, assume

```text
D_infinity^beta_j(P_(S_e,Z_(j-1)) || P_(S_e) tensor P_(Z_(j-1))) <= kappa_j.
```

Equivalently, for every measurable event `A`,

```text
P((S_e,Z_(j-1)) in A)
  <= exp(kappa_j) P((S_e',Z_(j-1)) in A) + beta_j,
```

where the probability on the right uses an independent draw `S_e'` with the same marginal law. This is a registered property of the complete transcript released before the candidate is evaluated. It is not inferred from the number of visible fields, and it does not reset merely because an evaluator receives a new name or process ID.

The operational ledger stores a rational upper bound `B_j >= exp(kappa_j)` and an exact rational additive debit `beta_j`.

## 3. Fixed-candidate component validity

For component `q` in `{F,R,H}`, let

```text
phi_j,q(c,S_e) in {0,1}
```

be the registered rejection rule for a fixed candidate `c`. Whenever `H_q,j(c)` is true, require

```text
P(phi_j,q(c,S_e)=1) <= u_j
```

for every fixed `c` that could be submitted at round `j`. This fixed-candidate guarantee may come from a confidence sequence, e-process, exact paired test, masked test, or another prospectively justified procedure. The theorem below does not repair an invalid test.

## 4. Adaptive transfer lemma

**Lemma 1.** If the max-information and fixed-candidate assumptions hold, then for an adaptively chosen `C_j=C_j(Z_{j-1})` satisfying component null `H_q,j`,

```text
P(phi_j,q(C_j,S_e)=1) <= B_j u_j + beta_j.
```

**Proof.** Define the event

```text
A={(s,z): phi_j,q(C_j(z),s)=1 and H_q,j(C_j(z)) is true}.
```

Under the product distribution in which `s` is independent of `z`, condition on `Z_{j-1}=z`. The candidate is then fixed, so the event has conditional probability at most `u_j`. Hence the product probability of `A` is at most `u_j`. The approximate max-information inequality transfers this event to the adaptive joint distribution with probability at most `exp(kappa_j)u_j+beta_j`, which is at most `B_j u_j+beta_j`. `square`

## 5. Intersection-union promotion

**Lemma 2.** If candidate `C_j` is scientifically bad and promotion requires every component rejection, then

```text
P(C_j is promoted) <= B_j u_j + beta_j.
```

**Proof.** At least one of `H_F,j`, `H_R,j`, or `H_H,j` is true. Select any true component. Promotion is a subset of rejection of that component, so Lemma 1 applies. Deterministic gates can only reduce the promotion event. `square`

The intersection-union structure matters. There is no need to add three component error probabilities merely because three gates are evaluated: a bad candidate has at least one true component null, and promotion requires that true null to be rejected.

## 6. Global theorem

Let the effective debit be

```text
d_j = B_j u_j + beta_j.
```

Assume the ledger enforces the pathwise budget

```text
sum_j d_j <= alpha_total
```

across every retry, resumption, evaluator epoch, and stopping path.

**Theorem 1 (reusable sealed familywise false-promotion control).** Under the assumptions above, for arbitrary adaptive candidate generation, evaluator requests, and data-dependent stopping,

```text
P(at least one scientifically bad candidate is promoted) <= alpha_total.
```

**Proof.** By Lemma 2, the bad-promotion event at round `j` has probability at most `d_j`. The union bound over the realized countable round sequence gives at most `sum_j d_j`, which is pathwise bounded by `alpha_total`. Stopping early removes future terms and cannot increase the bound. `square`

## 7. Evaluator epochs

An epoch boundary changes statistical accounting only when its protected data and release mechanism justify a new bound. The ledger therefore records:

- protected dataset identity or sealed commitment;
- transcript identity inherited from every earlier use of that dataset;
- the independently justified `B_j` and `beta_j` bounds;
- whether the epoch uses genuinely independent protected data.

Renaming an evaluator, rotating a key, restarting a process, or re-randomizing a prompt does not reset leakage. When a new independent protected sample is used and no information about it was previously released, the initial bound may take `B_j=1,beta_j=0`.

## 8. Retention, harm, and authority are not alpha substitutes

The theorem controls false statistical promotion under its assumptions. It does not authorize promotion when:

- protected data were accessed by the candidate;
- the evaluator or threshold was modified after outcome access;
- retention or harm endpoints are missing;
- resource limits were exceeded;
- the candidate controls the promotion key;
- an execution failed or used stale artifacts;
- negative history was deleted;
- the fixed-candidate test is invalid;
- the max-information bound is absent or understated.

Every such condition is a separate veto producing `UNRESOLVED` or `REJECT`, never a compensating numerical penalty.

## 9. Exact operational accounting

The implementation stores all probabilities as exact rational numbers. A round declares:

```text
raw_alpha = numerator / denominator
inflation = numerator / denominator  # a registered upper bound on exp(kappa)
beta = numerator / denominator
effective_debit = inflation * raw_alpha + beta
```

The independent checker recomputes the debit, hash chain, cumulative spend, duplicate semantics, gate conjunction, and decision without importing the campaign writer.

## 10. Donor boundary

The probability-transfer step is an application of approximate max-information/adaptive-data-analysis arguments. Conditional testing, confidence sequences, e-processes, intersection-union tests, online error control, and reusable holdout mechanisms are donor areas. The contribution claimed by this lane is the integrated scientific-promotion contract and its exact executable custody semantics, plus any future longitudinal evidence obtained under the frozen protocol. No general priority claim is made until a current primary-source novelty audit and independent review are complete.
