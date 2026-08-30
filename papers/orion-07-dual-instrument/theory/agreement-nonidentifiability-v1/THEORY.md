# ORION07.AGREEMENT_NONIDENTIFIABILITY.v1 — THEORY

**Paper:** ORION-07 — Dual Instrument
**Successor id:** `ORION07.AGREEMENT_NONIDENTIFIABILITY.v1`
**Candidate source:** PR #1617, `WAVE1_SUCCESSOR_THEORY_CANDIDATES_2026-08-28.md`, Priority A
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__INDEPENDENTLY_CHECKED`
**Scientific authority delta:** `NONE_FOR_MANUSCRIPT_CLAIMS` — see §7
**Packet layout source:** issue #1608, *Mandatory successor packet layout*
**Frozen paper bytes modified:** NONE

---

## 1. Why this successor exists

ORION-07 states, in `MANUSCRIPT_V3.md`, that inter-instrument agreement is **not**
validation, and supports that statement with one empirical case
(ORION-03-R2 / QG-20) in which both instruments agreed and both were later scored
misaligned.

The paper is correct, and its receipts already refuse to convert agreement into an
accuracy figure: `PREOUTCOME_AGREEMENT.json` carries
`aggregate_accuracy_computed: false`, and both `FINAL_SCORE.json` files carry
`aggregate_reliability_claim_authorized: false`.

What the paper does **not** yet have is the exact reason. "Agreement is not
validation" is currently justified by one counterexample. This note replaces the
counterexample-level justification with an exact, finite-sample, assumption-free
theorem that says precisely how much information agreement carries about accuracy,
and proves the answer is sharp.

The result is claim-preserving. It supplies the formal ground for a statement the
manuscript already makes at bounded scope. It licenses no reliability rate, no
calibration claim, no kappa, and no enlargement of `n_valid = 3`.

---

## 2. Setting

Fix a finite set of scored units indexed `i = 1..n`. Each unit carries

- `x_i in {0,1}` — the decision of instrument X (Lane A),
- `y_i in {0,1}` — the decision of instrument Y (Lane B),
- `t_i in {0,1}` — the later deferred scientific outcome on the same frozen axis.

`1` denotes *aligned with the deferred outcome map* on the axis under study, `0`
denotes *misaligned*. All three coordinates are frozen before outcome access under
the ORION-07 custody rule; nothing in this section assumes how they were produced.

Define the empirical quantities

```
a_hat   = (1/n) * #{ i : x_i = y_i }                 agreement rate
pX_hat  = (1/n) * #{ i : x_i = t_i }                 accuracy of X
pY_hat  = (1/n) * #{ i : y_i = t_i }                 accuracy of Y
q_hat   = ( pX_hat + pY_hat ) / 2                    mean instrument accuracy
c_hat   = (1/n) * #{ i : x_i = y_i = t_i }           joint-correct rate
```

Everything below is a statement about these counts. **No probability model, no
independence assumption, and no sampling assumption is used anywhere.** The same
statements hold verbatim for a population law `P` on `{0,1}^3` with
`a = P(X=Y)`, `pX = P(X=T)`, `pY = P(Y=T)`, `q = (pX+pY)/2`, `c = P(X=Y=T)`;
replace counting averages by expectations. This matters for ORION-07 specifically,
because at `n_valid = 3` no distributional statement would be admissible, and none
is needed.

---

## 3. The theorems

### Lemma 1 (pointwise accounting)

For every unit `(x, y, t) in {0,1}^3`,

```
1{x = t} + 1{y = t}  =  1{x != y}  +  2 * 1{x = y = t}.
```

**Proof.** Exhaustive over the three mutually exclusive and exhaustive cases.

1. `x != y`. Then `{x, y} = {0, 1}`, and since `t in {0,1}`, exactly one of `x, y`
   equals `t`. LHS `= 1`. On the right, `1{x != y} = 1` and `1{x = y = t} = 0`, so
   RHS `= 1`.
2. `x = y = t`. LHS `= 2`. RHS `= 0 + 2 = 2`.
3. `x = y != t`. Neither matches `t`, so LHS `= 0`. RHS `= 0 + 0 = 0`.

The three cases exhaust `{0,1}^3`. ∎

### Theorem 1 (exact decomposition of mean accuracy)

```
q_hat = (1 - a_hat)/2 + c_hat.
```

**Proof.** Average Lemma 1 over `i = 1..n` and divide by `2`. The average of
`1{x_i = t_i} + 1{y_i = t_i}` is `pX_hat + pY_hat = 2 q_hat`; the average of
`1{x_i != y_i}` is `1 - a_hat`; the average of `1{x_i = y_i = t_i}` is `c_hat`. ∎

This identity is the whole content of the result. Everything that follows is a
consequence of it together with the trivial range of `c_hat`.

### Theorem 2 (sharp mean-accuracy interval)

Because a unit can only be jointly correct if it is an agreement unit,
`0 <= c_hat <= a_hat`. Substituting into Theorem 1,

```
(1 - a_hat)/2  <=  q_hat  <=  (1 + a_hat)/2,
```

and the interval has width exactly `a_hat`. Both endpoints are attained, and every
value of `q_hat` compatible with the granularity `1/n` inside the interval is
attained.

**Attainability.** Fix `n` and integers `A = n*a_hat` and `C` with `0 <= C <= A`.
Take `C` units `(1,1,1)`, `A - C` units `(1,1,0)`, and split the remaining `n - A`
disagreement units arbitrarily between `(1,0,1)` and `(0,1,0)`. This realizes
agreement count `A` and joint-correct count `C` exactly, hence
`q_hat = (1 - a_hat)/2 + C/n`. Letting `C` run over `0..A` sweeps the interval. ∎

### Corollary 2.1 (perfect agreement is vacuous)

If `a_hat = 1`, Theorem 2 gives `0 <= q_hat <= 1`. Perfect agreement supplies **no
nontrivial bound whatsoever** on mean instrument accuracy.

### Corollary 2.2 (perfect disagreement pins the mean at chance)

If `a_hat = 0`, then `c_hat = 0` and Theorem 1 gives `q_hat = 1/2` **exactly**.
Two instruments that never agree have mean accuracy exactly one half, regardless of
anything else about them.

### Corollary 2.3 (agreement destroys level information monotonically)

The width of the attainable mean-accuracy interval is exactly `a_hat`. It is
strictly increasing in agreement. Higher agreement therefore carries strictly
**less** information about how accurate the instruments are.

### Theorem 3 (exact attainable region for the accuracy pair)

Fix `a in [0,1]`. The set of attainable pairs `(pX, pY)` is exactly

```
R(a) = { (u,v) in [0,1]^2 : |u - v| <= 1 - a  and  1 - a <= u + v <= 1 + a }
     = conv{ (1-a, 0), (1, a), (a, 1), (0, 1-a) }.
```

**Proof.** Write

```
alpha = (1/n) #{ i : x_i = t_i, x_i != y_i },
beta  = (1/n) #{ i : y_i = t_i, x_i != y_i },
c     = c_hat.
```

By case 1 of Lemma 1, on each disagreement unit exactly one of `x, y` matches `t`,
so `alpha + beta = 1 - a`. By cases 2 and 3, on agreement units `x` matches `t` iff
`y` does, and that happens exactly on the joint-correct units. Hence

```
pX = alpha + c,      pY = beta + c.
```

*Necessity.* `u + v = alpha + beta + 2c = (1 - a) + 2c`, and `c in [0, a]` gives
`1 - a <= u + v <= 1 + a`. Also `u - v = alpha - beta` with `alpha, beta >= 0` and
`alpha + beta = 1 - a`, so `|u - v| <= 1 - a`. Membership in `[0,1]^2` is trivial.

*Sufficiency.* Given `(u,v) in R(a)`, set

```
c     = (u + v - (1 - a)) / 2,
alpha = u - c,
beta  = v - c.
```

Then `c in [0, a]` by the sum constraint. Also
`alpha = (u - v + 1 - a)/2 >= 0` and `beta = (v - u + 1 - a)/2 >= 0` by the spread
constraint, and `alpha + beta = 1 - a` by construction. Realize these by placing
mass `c` on `(1,1,1)`, `a - c` on `(1,1,0)`, `alpha` on `(1,0,1)` and `beta` on
`(0,1,1)`. All four masses are non-negative and sum to
`c + (a - c) + alpha + beta = a + (1 - a) = 1`.

*Vertex form.* The four bounding lines meet pairwise at `(1-a, 0)`, `(1, a)`,
`(a, 1)` and `(0, 1-a)`, all of which lie in `[0,1]^2` for `a in [0,1]`. ∎

### Corollary 3.1 (agreement bounds the spread, sharply)

```
| pX - pY |  <=  1 - a,
```

attained at the vertices `(1-a, 0)` and `(0, 1-a)`.

### Corollary 3.2 (agreement constrains neither instrument alone)

For every `a in [0,1]` and every `u in [0,1]` there is an admissible configuration
with agreement `a` and `pX = u`. Take `v = 1 - a - u` when `u <= 1 - a`, and
`v = u - (1 - a)` otherwise; both choices lie in `R(a)`. Agreement therefore places
**no constraint at all** on either instrument's individual accuracy.

---

## 4. What the theorems say, in one sentence

Agreement is informative about **homogeneity** and never about **correctness**:
it bounds how far apart the two instruments' accuracies can be (Corollary 3.1,
tightening as agreement rises) while simultaneously widening the range of levels
those accuracies may share (Corollary 2.3), and it constrains neither instrument
alone (Corollary 3.2).

This is the exact formal content of the manuscript sentence *"this explicit case
shows why inter-instrument agreement is not validation."*

---

## 5. Binding to the ORION-07 case series

The three valid units are scored on the responsibility axis in
`instances/*/FINAL_SCORE.json` and in
`CLAIM_LEDGER_PROSPECTIVE_CASE_SERIES_2026-08-23.md`:

| unit | pre-outcome relation | X aligned | Y aligned | joint-correct |
|---|---|---|---|---|
| V0 (post-R6O) | `AGREE` | yes | yes | yes |
| Q3-R1 / QG-19 | `AGREE` | yes | yes | yes |
| Q3-R2 / QG-20 | `AGREE` | no | no | no |

Therefore, with `n = 3`:

```
a_hat  = 3/3 = 1
c_hat  = 2/3
pX_hat = pY_hat = 2/3
q_hat  = 2/3
```

Theorem 1 is satisfied exactly: `(1 - 1)/2 + 2/3 = 2/3 = q_hat`.

The scientifically important consequence is Corollary 2.1. The observed agreement
of `3/3` constrains mean accuracy to `[0, 1]` — that is, to nothing. The value
`q_hat = 2/3` is carried **entirely** by the deferred outcomes and not at all by the
agreement. Had the deferred outcomes been withheld, the same perfect agreement
would have been equally consistent with `q_hat = 0`.

The Q3-R2 unit is the in-repository witness for the upper part of the interval
being unattained: agreement `1` with joint-correct `0` on that unit.

This is a re-reading of already-frozen scored artifacts. No score, terminal,
digest or receipt is altered, and no new unit is created.

---

## 6. Strongest falsifier

The theorems are exact and exhaustively checked, so they cannot fail as
mathematics. What can fail is their **relevance**:

1. **Non-binary alphabet.** ORION-07 scores three axes with `AGREE`/`DISAGREE`
   relations and diagnosis/move labels drawn from larger vocabularies. Lemma 1
   depends on `t in {0,1}` and would need restating for a `k`-ary alphabet; case 1
   ("exactly one is correct on disagreement") is false for `k >= 3`, where both
   instruments may be wrong while disagreeing. The binary reduction used here is
   *alignment vs non-alignment against the frozen deferred map*, which is the form
   the paper actually scores, so the reduction is faithful — but any future
   multi-class reliability statement must not cite these theorems.
2. **Additional identifying assumptions.** A predeclared and independently
   defensible joint error model, multiple populations with differing prevalence, or
   conditional independence would add identifying information beyond `a`. Those are
   classical no-gold latent-class assumptions and are donor methodology.
3. **Deferred gold.** The theorems are silent once `t` is observed on enough units;
   at that point accuracy is estimated directly and agreement is irrelevant to it.

Route 3 is the route ORION-07 already takes. That is the correct route, and this
note supplies the reason the other two are not shortcuts.

---

## 7. Authority boundary

`scientific_authority_delta = NONE` with respect to every ORION-07 manuscript
claim, terminal, score, receipt and ledger row.

Specifically, this note:

- does **not** authorize a reliability estimate, kappa, calibration claim or
  population generalization; `n_valid = 3` stands unchanged;
- does **not** promote agreement into a correctness score anywhere;
- does **not** alter `aggregate_accuracy_computed: false` or
  `aggregate_reliability_claim_authorized: false`;
- does **not** create, rescore or reinterpret any frontier unit;
- does **not** touch `submission_tmlr/`, whose bytes are bound by
  `papers/publication_closure/PACKAGE_ADOPTION_V2.json` under issue #1601.

What it does establish is a proved, independently checked mathematical statement
that may be cited **in support of an existing bounded claim**. Whether the ORION-07
manuscript cites it is a separate editorial decision recorded in
`CLAIM_DISPOSITION.md`; this packet does not make that edit.

## 8. Donor boundary

The mathematics is elementary and **donor-owned**. Two-by-two accounting identities
of this kind, Fréchet-type bounds on joint events given marginals, and the
non-identifiability of accuracy from agreement without a gold standard are standard
in the no-gold diagnostic-test and latent-class literature. Corollary 2.1 is the
familiar observation that concordance does not establish validity.

No novelty is claimed for Lemma 1, Theorem 1, Theorem 2 or their corollaries.

The ORION-specific content is narrow and is limited to: the exact binding of these
donor facts to the ORION-07 dual-instrument contract in §5, the observation that the
frozen three-unit case series instantiates the vacuity corollary exactly, and the
statement in §4 separating homogeneity from correctness as the precise thing
inter-instrument agreement measures. Theorem 3 and Corollary 3.2 are stated in full
because the sharp region — as opposed to the mean interval alone — is what makes the
"constrains neither instrument alone" statement precise; they are also expected to
be classical.

Any future manuscript treatment must subtract this donor literature explicitly
rather than presenting the theorems as an ORION contribution.
