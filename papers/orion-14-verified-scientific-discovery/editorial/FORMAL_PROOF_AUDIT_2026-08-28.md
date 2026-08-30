# ORION-14 formal proof audit — 2026-08-28

**Review type:** simulated independent formal-methods pass for the Wave-1 recursive publication pipeline; not external peer review.  
**Audited source:** current `manuscript/sections/02a-verification-axis-identifiability.tex` on PR #1610.  
**Rule:** check assumptions, quantifiers, boundary cases, equality/inequality direction, and manuscript-level interpretations. Do not infer empirical generality from the formal results.

## P1 — finite exact-axis Bayes risk

### Statement audited
For finite benchmark support and finite nonempty output alphabet `A`, the minimum exact-terminal error available to a rule based on representation `D` is

`R*(D,A) = 1 - E_D[max_{t in A} P(Y=t | D)]`.

### Check
Condition on each positive-probability value `D=d`. A deterministic decision selects one terminal. Its conditional success probability is maximized by any terminal attaining `max_t P(Y=t|D=d)`. Randomization cannot improve a linear 0–1 risk over the simplex. Averaging the fibrewise optimum gives the displayed risk. A fixed tie order gives an optimizer on finite support.

### Boundary/degenerate cases
- `A` must be nonempty; stated.
- If the correct target lies outside `A` on a fibre, zero risk is impossible; captured by the maximum over `A`.
- Null fibres do not affect distributional risk and therefore cannot be certified pointwise; manuscript states this explicitly.

**Disposition:** `PASS`.

## Proposition 1 — zero-risk attainability

### Necessity
If `g(D)` has zero exact-terminal error, then on every positive-probability `D=d` fibre all positive conditional mass of `Y` must be on `g(d)`, and `g(d)` is in `A`. Otherwise that fibre contributes positive error.

### Sufficiency
If every positive-probability fibre is target-pure at some terminal in `A`, define `g(d)` as that terminal on positive-mass fibres and arbitrarily in `A` on null fibres. Then `Y=g(D)` almost surely and risk is zero.

### Quantifier audit
The manuscript correctly separates almost-sure benchmark authority from pointwise authority on null fibres.

**Disposition:** `PASS`.

## Corollary 1 — donor-product factorization

### Pointwise form
On a declared world class, a donor-only decision can equal the target everywhere iff target values are constant on every donor-state fibre and belong to the permitted output alphabet. Necessity follows because a function of donor state cannot take two target values on one fibre. Sufficiency follows by defining the decision on each fibre to be its unique target value.

### Distributional form
Under a benchmark distribution, the same condition is required only on positive-probability fibres. The displayed sum is the exact fibrewise Bayes error, not merely a loose lower bound, on the finite benchmark; the manuscript says it is attained by the fibrewise Bayes rule.

### Interpretation boundary
The theorem supports: a separate authority module has no *inherent representational advantage* once a donor product is given target-sufficient state, the same target relation, and an adequate alphabet. It does not support: centralization is unnecessary in every implementation, donor construction is equally safe operationally, or the exact gate list is universally necessary.

**Disposition:** `PASS`.

## Corollary 2 — terminal-preserving comparator adapters

### Setup
`V` is the complete candidate-visible record, `X` is comparator-native output, and `X` is generated from `V` by a measurable randomized kernel, so `Y - V - X` is a Markov chain. `V` and `X` are standard-Borel and the target alphabet is finite.

### Bayes-risk monotonicity
For finite terminal set, `P(Y=t|X)` is the conditional expectation of `P(Y=t|V)` through the Markov chain. Because pointwise maximum over finitely many coordinates is convex,

`E[max_t P(Y=t|X)] <= E[max_t P(Y=t|V)]`,

hence `R*(X,A) >= R*(V,A)`. A fixed-order argmax of the measurable conditional probabilities is measurable and attains `R*(X,A)`.

### Zero-error adapter condition
Applying Proposition 1 to `X` gives the necessary and sufficient positive-probability fibre-purity/alphabet condition. For deterministic `X` and pointwise world-class authority, every native-output fibre must be pure, including benchmark-null fibres.

### Binary-alphabet boundary
The source was tightened during this audit to say that a binary native alphabet cannot attain a three-terminal endpoint when all three target terminals have **positive probability**. This avoids an overbroad reading involving a nominal but null terminal.

### Semantic relabelling boundary
A native `Block`, parse failure, or free-text insufficiency output can be mapped to `CannotCheck` only if the prospectively declared mapping is target-pure on the relevant fibres. Otherwise the observed gap is an interface-attainability result rather than evidence of worse scientific judgement.

**Disposition:** `PASS_AFTER_TEXTUAL_TIGHTENING`.

## Proposition 2 — total-variation claim identifiability

### Setup
Two worlds induce probability measures `P0` and `P1` on the same measurable record space; prior weights are equal. With acceptance region `B` for world 1, error is

`[P0(B) + P1(B^c)] / 2 = [1 - (P1(B)-P0(B))]/2`.

Optimizing over `B` gives `(1-TV(P0,P1))/2` under the manuscript's TV convention. A Hahn decomposition for the finite signed measure `P1-P0` supplies a maximizing measurable region. Randomized tests cannot improve the optimum because their risks are convex mixtures/integrals of deterministic decisions.

### Boundary cases
- `TV=0` gives minimum error `1/2`; identical observable laws are unidentifiable under equal priors.
- `TV=1` permits zero Bayes error.
- The proposition is about identifiability from the specified observable record; it does not assert that any empirical pair of scientific worlds has a particular TV distance.

**Disposition:** `PASS`.

## Nuisance advantage and panel resolution

The nuisance quantity is a definition of Bayes advantage for a declared nuisance representation. The manuscript correctly states that a finite probe family can clear only its own class, not all decoders. The panel-resolution quantity `rho=max M-min M` is descriptive; `rho=0` logically supplies no observed ordering and cannot establish equality of latent competence. Combining nonzero resolution with mismatched terminal alphabets first supports an expressiveness distinction, consistent with Corollary 2.

**Disposition:** `PASS`.

## Cross-theorem consistency

- [x] pointwise and almost-sure claims are distinguished;
- [x] target-alphabet insufficiency is separated from poor decision logic;
- [x] data-processing direction is correct (`R_X >= R_V`);
- [x] standard-Borel/measurability assumption is present where the randomized adapter needs it;
- [x] total-variation convention matches the stated Bayes-error formula;
- [x] null fibres are not silently certified;
- [x] P4-X typed-donor tie is interpreted as a factorization/portability boundary, not centralization superiority;
- [x] V3 is interpreted as terminal/interface attainability before epistemic judgement.

## Formal terminal

`FORMAL_PROOF_AUDIT_PASS__ONE_SCOPE_TIGHTENING_APPLIED__EXTERNAL_PEER_REVIEW_NOT_CLAIMED`
