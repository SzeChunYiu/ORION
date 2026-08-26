# FiberGuard R15 — coverage tax, missing mass, and valid inductive certificates

Date: 2026-08-26

Status: analytic response to the prospective R14 refutation. The classical missing-mass problem, Good--Turing estimation, nearest-neighbor methods, Lipschitz extension, selective prediction, conformal coverage, and generic distribution-shift theory are donor-owned. The FiberGuard-specific contribution is the exact decision-cost decomposition that separates finite-fibre authority, out-of-sample recurrence, structural certificate validity, and paid operational value.

## 1. The quantifier exposed by R14

R11 established an exact statement on a complete finite subject: after all 1,614 SAT12-ALL instances and their solver outcomes were fixed, the representation `{Pre,lobjois}` induced fibres on which one could compute exact action regret and total excess. R14 asked a different question: fit the representation policy on training outcomes and act on held-out states.

The result was adverse. Exact signatures recurred on only 52/1,614 official-fold predictions and 82/1,614 leave-family-out predictions. The same feature information was useful to a transparent learned selector, but exact equality was almost never available as an inductive policy key.

This addendum formalizes that distinction. A complete-fibre certificate remains exact. A finite training fibre is not a complete population fibre, and exact equality recurrence is not the same thing as certificate validity.

## 2. Setup

Let `X` be a state drawn from a declared test distribution, or uniformly from a declared finite evaluation panel. Let:

- `Phi(X)` be the acquired representation;
- `T` be a finite training subject;
- `S_T(X)` be the event that `Phi(X)` equals a representation value observed in `T`;
- `a_0` be the frozen fallback action;
- `a_T(Phi(X))` be the fitted representation action when `S_T(X)` holds and `a_0` otherwise;
- `c_T(X)>=0` be the complete acquisition charge;
- `R(a,X)=C(a,X)-C*(X)` be action regret relative to the same statewise oracle for every arm.

Define deployed and fallback excess losses

`L_T(X)=c_T(X)+R(a_T(Phi(X)),X)`

and

`L_0(X)=R(a_0,X)`.

The setup includes static and adaptive acquisition: `c_T(X)` may be the sum of all state-dependent charges on the realized path. It also includes randomized terminal actions after replacing `R` by the statewise expected regret of the declared mixed policy. Pathwise and expected semantics must remain distinct.

## 3. Exact coverage-tax identity

Define the covered-state action saving

`G_T(X)=R(a_0,X)-R(a_T(Phi(X)),X)`.

By the fallback contract, `G_T(X)=0` whenever `S_T(X)` fails.

### Theorem C-R15.1 — exact mean coverage tax

Let `q_T=P(S_T(X))`. Then

`E[L_T-L_0] = E[c_T] - q_T E[G_T | S_T]`.

Thus the representation policy improves mean total excess if and only if

`q_T E[G_T | S_T] > E[c_T]`.

#### Proof

Pointwise,

`L_T-L_0 = c_T - G_T`.

Taking expectation gives `E[c_T]-E[G_T]`. Since `G_T=0` off `S_T`,

`E[G_T]=P(S_T)E[G_T|S_T]`.

Substitution proves the identity and the strict-improvement criterion. ∎

The formula is not an asymptotic approximation. It is an exact identity for a probability distribution or a finite empirical panel.

### Corollary C-R15.2 — necessary coverage under bounded benefit

If `G_T(X)<=B` on covered states, then

`E[L_0]-E[L_T] <= q_T B - E[c_T]`.

A necessary condition for positive mean value is

`q_T B > E[c_T]`.

A highly valuable action correction can therefore still fail operationally when signature coverage is too small or acquisition is paid on uncovered states.

### Corollary C-R15.3 — no pointwise dominance with paid uncovered states

On every uncovered state,

`L_T(X)-L_0(X)=c_T(X)`.

If `P(not S_T and c_T>0)>0`, the representation policy is strictly worse than fallback on a positive-mass set. It cannot uniformly dominate fallback.

This is the exact failure mode of acquiring an expensive signature only to discover that the policy has no fitted action for it.

### Corollary C-R15.4 — adverse-event improvement is coverage limited

Let `H(a,x)` be any binary action-level adverse event, such as selecting a PAR10 solver when the statewise oracle is not PAR10. Because the deployed and fallback actions agree off `S_T`,

`P(H(a_0,X))-P(H(a_T(Phi(X)),X)) <= q_T`.

#### Proof

The two event indicators are identical off `S_T`. Their difference is at most one on `S_T`. Taking expectations gives the bound. ∎

This bound applies independently of the magnitude of numerical regret.

## 4. Exact recurrence and missing mass

Let `Y=Phi(X)` and suppose training values `Y_1,...,Y_n` and test value `Y_(n+1)` are iid from the representation distribution. Write `p_y=P(Y=y)` for every atom.

### Theorem C-R15.5 — exact equality recurrence

The expected exact-signature coverage after `n` training states is

`q_n = P(Y_(n+1) in {Y_1,...,Y_n})`

`    = sum_y p_y [1-(1-p_y)^n]`,

where the sum is over the atoms of the representation distribution. The missing mass is

`M_n=1-q_n`.

#### Proof

Condition on the test value `Y_(n+1)=y`. It is observed in training unless all `n` training draws avoid `y`, an event of probability `(1-p_y)^n`. Multiply by `p_y` and sum over atoms. A nonatomic test value matches any one of finitely many training values with probability zero and contributes nothing to the recurrence sum. ∎

### Corollary C-R15.6 — exact equality has zero finite-sample coverage for nonatomic representations

If the law of `Phi(X)` is purely nonatomic, then `q_n=0` for every finite `n`.

Therefore an equality-keyed policy with positive feature cost and fallback on unseen signatures is strictly worse in expectation than the fallback by exactly `E[c_T]`: it obtains no action correction at all.

This does not say continuous features lack predictive value. It says exact numerical equality is an unsuitable inductive equivalence relation unless the representation has meaningful atoms, quantization, or repeated structure.

The estimation of missing mass from observations is classical and receives no novelty credit. FiberGuard uses the missing mass as one term in a downstream decision-cost identity rather than as a new species-estimation problem.

## 5. Why a training-fibre certificate is not a future-state certificate

A finite training certificate for signature `y` computes

`rho_T(y)=min_a max_{x in T:Phi(x)=y} R(a,x)`.

That is exact on the displayed training states. Without a completeness claim or a structural extension assumption, it says nothing about unobserved states with the same representation.

### Theorem C-R15.7 — unbounded same-signature extension attack

Fix any finite training subject, any signature `y`, and any action `a` selected from its training fibre. If the admissible domain places no restriction on the regret vector of unseen states, then for every `M>0` there exists an extended domain containing one new state `x_M` such that:

- `Phi(x_M)=y`;
- every training state, cost, representation, and certificate is unchanged;
- `R(a,x_M)=M`;
- some competing action has regret zero on `x_M`.

Consequently no finite training-fibre upper bound is a distribution-free upper bound for future members of the representation fibre.

#### Proof

Append one state with the same declared representation. Keep the complete training restriction unchanged. Assign the selected action excess cost `M` and one other action excess cost zero on the new state. These assignments satisfy nonnegative regret and preserve every observed byte while violating any proposed bound below `M`. Since `M` is arbitrary, no finite universal extension bound exists. ∎

This theorem is a scope result, not computational hardness. It identifies the additional premise required for inductive authority.

## 6. A valid structural route: Lipschitz excess certificates

Let the representation space carry a declared metric `d`. Assume terminal action cost and oracle cost obey

`|C(a,x)-C(a,x')| <= L_a d(Phi(x),Phi(x'))`

and

`|C*(x)-C*(x')| <= L_* d(Phi(x),Phi(x'))`.

### Lemma C-R15.8 — regret Lipschitz constant

For every action,

`|R(a,x)-R(a,x')| <= (L_a+L_*) d(Phi(x),Phi(x'))`.

#### Proof

Expand the difference of `C(a,.)-C*(.)` and apply the triangle inequality and the two assumptions. ∎

Let `L^R_a` be any valid regret Lipschitz constant, including `L_a+L_*`. For training subject `T`, define

`U_T(a,x)=min_{z in T} [R(a,z)+L^R_a d(Phi(x),Phi(z))]`.

### Theorem C-R15.9 — exact neighborhood upper certificate

For every state `x` and action `a`,

`R(a,x) <= U_T(a,x)`.

Thus

`U_T(x)=min_a U_T(a,x)`

is a certified upper bound achieved by the action minimizing `U_T(a,x)`. If `U_T(x)<=epsilon`, the policy has a valid `epsilon`-regret certificate at `x`; otherwise it must refine, defer, or act without that certificate.

#### Proof

For every training state `z`, Lipschitz continuity gives

`R(a,x)<=R(a,z)+L^R_a d(Phi(x),Phi(z))`.

The inequality holds for every `z`, hence for their minimum. Minimizing the valid action-wise upper bounds preserves validity for the selected action. ∎

### Corollary C-R15.10 — certificate coverage is monotone in the training subject

If `T subseteq T'`, then

`U_(T')(a,x)<=U_T(a,x)`

for every action and state. Therefore the certified set

`K_epsilon(T)={x:min_a U_T(a,x)<=epsilon}`

can only grow as valid training anchors are added.

### Hostile control

Using an underestimated `L^R_a` invalidates the certificate. This is not a tunable calibration constant that may be selected for attractive coverage after test outcomes. It must be proved, externally validated, or replaced by a probabilistic guarantee with its own stated authority.

Lipschitz extension and nearest-neighbor reasoning are classical. The paper-specific role is to supply an explicit, auditable bridge from a coverage-producing representation relation to an action-regret certificate. The theorem does not establish that SAT12-ALL has a useful low-dimensional metric or a small valid constant.

## 7. Three quantities that must not be conflated

For inductive FiberGuard, every result must report separately:

1. **recurrence coverage:** whether a test representation relation finds a training anchor;
2. **certificate validity:** whether the anchor-to-test extension bound is mathematically justified;
3. **decision value:** whether covered action savings exceed acquisition cost and adverse uncovered-state effects.

Exact signature recurrence without complete-fibre authority does not by itself grant certificate validity. A valid structural certificate with negligible coverage may have no operational value. A predictive learned selector may have value without deterministic certificate authority.

This three-way split is the corrected application architecture:

- a learned selector predicts broadly;
- FiberGuard certifies only the subset supported by a complete fibre or valid extension theorem;
- the controller refines, routes, or abstains elsewhere;
- all acquisition charges are paid in the same oracle-relative objective.

## 8. Exact interpretation of R14

R14's training-selected exact policy used the frozen global robust action on uncovered signatures, so Theorem C-R15.1 applies directly.

### Official CV

- coverage `q=52/1614=0.0322180916976456`;
- mean feature cost `22.974684014869887`;
- fallback mean excess `5448.31466542751`;
- deployed mean excess `5380.232187112763`;
- mean improvement `68.082478314747`.

The identity implies a coverage-weighted action saving of

`5448.31466542751 + 22.974684014869887 - 5380.232187112763`

`=91.057162329616887`.

Conditional on the 52 recurrent signatures, the average action saving is approximately `2826.27423076926`. The covered cases are valuable; there are simply too few of them. The catastrophic-rate reduction is `0.00743494423791826`, below the absolute coverage ceiling `0.0322180916976456`.

### Leave-family-out

- coverage `82/1614=0.05080545229244114`;
- mean feature cost `22.773909541511774`;
- mean improvement over fallback `106.7292317224295`;
- conditional saving on recurrent signatures approximately `2549.00085365855`;
- catastrophic-rate reduction `0.01053283767038416`, below the coverage ceiling.

These decompositions explain the `PARTIAL_MEAN_ONLY` terminal without retuning it. The exact arm extracts large savings from a very small recurrent subset and pays acquisition cost everywhere.

## 9. Consequences for the manuscript

The strongest defensible application statement is now:

> Complete finite representation fibres yield exact transductive action-regret certificates. Out of sample, equality-keyed policies incur an exact coverage tax; on SAT12-ALL, exact numeric recurrence is only 3.2% under official CV and 5.1% under source-family shift. A future inductive certificate requires a separately justified extension relation.

The paper must not claim that finite training-fibre regret is a future-state upper bound. It must not hide the R14 learned-baseline dominance. It must not run the R12/R13 adaptive controller on the same exact-equality terminal relation and describe the result as solving the coverage problem.

## 10. Next prospectively frozen gate

A valid successor needs a separate development subject and an untouched test subject. Before test outcomes, it must freeze:

- the representation metric or coarsening;
- the source of a valid deterministic or probabilistic extension bound;
- the tolerance defining certificate coverage;
- the acquisition policy and fallback;
- stronger learned algorithm-selection baselines;
- coverage, certificate validity, and total decision cost as separate estimands.

A deterministic Lipschitz lane must preserve any failure to validate the constant. A probabilistic lane must state marginal versus conditional coverage and must not relabel a conformal guarantee as worst-case fibre authority. Cross-scenario transfer and independent reproduction remain required for a top-tier application claim.

## 11. Prior-art boundary

The following are donor-owned:

- Good--Turing and modern missing-mass estimation;
- nearest-neighbor and Lipschitz extension methods;
- selective classification and abstention;
- conformal prediction and covariate-shift correction;
- generic algorithm-selection generalization bounds;
- generic cost-aware feature acquisition.

Recent missing-mass work continues to study estimation beyond iid samples; current conformal work explicitly addresses adaptive abstention and covariate shift; and current algorithm-selection theory studies generalization under distribution change. FiberGuard's residual candidate is not any one of those mechanisms. It is the exact oracle-relative decomposition linking finite-fibre certificates, coverage, acquisition price, hostile uncovered states, and a fail-closed extension contract for consequential solver actions.

## 12. Verification and authority

`verify_fiberguard_coverage_tax_r15.py` checks:

- 3,000 exact finite coverage-tax systems;
- 3,000 catastrophic-rate coverage bounds;
- 91 rational atomic distributions across 455 sample-size cells and 61,747 weighted train/test sequences;
- 100 same-signature extension attacks up to inserted regret 100;
- 500 metric systems with 11,564 action/state upper-bound checks;
- 1,744 cost-to-regret Lipschitz conversions;
- 11,564 training-set monotonicity checks;
- an explicit underestimated-constant failure;
- and the exact R14 aggregate decomposition.

The analytic proofs carry the theorem statements. Finite execution is implementation corroboration only. No representation metric, Lipschitz constant, cross-scenario result, external reproduction, novelty decision, production value, or journal authority is granted by this tranche.
