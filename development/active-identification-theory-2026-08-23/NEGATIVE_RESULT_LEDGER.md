# Retained negative results and successor research identities

Every failed conjecture below is retained. The witness harness checks the
finite arithmetic. A failed conjecture is not relabelled as a positive result;
it opens a sharper problem with an explicit next discriminator.

## N1. More target mutual information need not mean lower classification error

**Failed conjecture.** With one test remaining, the test of maximum target
mutual information also minimizes Bayes zero--one error.

**Finite counterexample.** Let the binary target have prior \(1/2\). For
binary outcome \(O=1\), test A has probabilities \((0,1/5)\) in target states
\((0,1)\); test B has probabilities \((1/5,1/2)\). Then

- \(I(Y;O_A)=0.1080315461\) bits and Bayes error \(2/5\);
- \(I(Y;O_B)=0.0731040079\) bits and Bayes error \(7/20\).

Information gain chooses A, while the correct zero--one objective chooses B.

**New research identity.** Loss-aligned acquisition rather than
representation-neutral information gain.

**Next discriminator.** Compare each proposed acquisition score to the exact
Bellman reduction for the declared terminal loss; search for loss classes in
which the ordering agrees.

## N2. Positive KL does not give finite exact identification

**Failed conjecture.** If every cross-target pair has positive KL divergence
under some test, a finite adaptive programme exactly identifies the target.

**Finite counterexample.** One repeatable Bernoulli test has success
probability \(1/4\) in world 0 and \(3/4\) in world 1. Its oriented KL is
\(\tfrac12\log 3>0\), but every binary string of every finite length has
positive probability in both worlds. No finite transcript is target-pure.

**New research identity.** Support-singular exact science versus
divergence-controlled approximate science.

**Next discriminator.** Use support separation for finite exactness; use KL,
Chernoff information, and declared error tolerance for approximate or
asymptotic claims.

## N3. Zero myopic target information does not imply zero programme value

**Failed conjecture.** If every single next test has zero mutual information
about the target, stopping is optimal.

**Finite counterexample.** Let \(W=(X_1,X_2)\) be uniform on two independent
bits and target \(Y=X_1\oplus X_2\). Tests reveal the individual bits. Each
alone has \(I(Y;X_i)=0\), but the pair identifies \(Y\). Under zero--one loss
and cost \(1/10\) per test, stopping has risk \(1/2\), any one-test programme
costs \(1/10\) and still has error \(1/2\), while the two-test programme costs
\(1/5\) and has zero terminal error.

**New research identity.** Complementary and synergistic scientific
acquisitions.

**Next discriminator.** Estimate Bellman continuation value or conditional
multi-test interaction, not only immediate marginal information.

## N4. Information-per-cost greedy is not exact under a hard budget

**Failed conjecture.** Selecting tests in decreasing mutual-information per
cost maximizes total information under a budget.

**Finite counterexample.** A finite world contains three independent uniform
bit blocks. Tests A, B, C reveal disjoint blocks of respectively 5, 3, and 3
bits and cost respectively 3, 2, and 2. With budget 4, ratio-greedy chooses A
for 5 bits and cannot add another test. B plus C costs 4 and reveals 6 bits.

**New research identity.** Budget-feasible acquisition frontiers and
approximation certificates.

**Next discriminator.** Test adaptive-submodularity or knapsack-submodularity
assumptions and report an approximation factor; otherwise solve the exact
finite policy/knapsack problem.

## N5. Posterior-local robust Bellman recursion can rectangularize authority

**Failed conjecture.** For any ex-ante credal set, condition every prior on the
observation, minimize worst-case loss separately at each observation, and
average those local values to obtain the ex-ante minimax policy.

**Finite counterexample.** The acquisition reveals \(Z\in\{0,1\}\). The target
is binary and the credal set contains two priors:

- \(p^A(0,0)=0.9\), \(p^A(1,1)=0.1\);
- \(p^B(0,1)=0.1\), \(p^B(1,0)=0.9\),

where atoms are \((Z,Y)\). At each value of \(Z\), the conditioned credal set
contains both deterministic labels, so the locally randomized minimax error is
\(1/2\). Ex ante, always predicting 0 has error \(0.1\) under both priors, and
is minimax. The local calculation let nature combine the rare adverse
conditional of one prior at \(Z=0\) with the rare adverse conditional of the
other at \(Z=1\), a prior not licensed by the original set.

**New research identity.** Dynamic provenance for ambiguity: which posterior
combinations remain licensed after an adaptive path?

**Next discriminator.** Carry world-risk vectors until the root credal
scalarization, or explicitly replace fixed-prior ambiguity by a rectangular
historywise model and justify that stronger adversary.

## N6. Deterministic policies need not be robust-minimax

**Failed conjecture.** Because finite-horizon Bayes policies can be chosen
deterministically, the same is true for credal minimax policies.

**Finite counterexample.** There are two unobserved target worlds, zero--one
loss, and the credal set contains each point mass. Either deterministic label
has worst-case error 1. A fair randomized label has error \(1/2\) in both
worlds.

**New research identity.** Auditable randomization at unresolved scientific
frontiers.

**Next discriminator.** Decide whether randomization is operationally and
ethically admissible. If it is, optimize over the convex risk frontier; if it
is not, report the deterministic robust value separately.

## N7. The identified support set is not a calibrated risk object

**Failed conjecture.** Two interfaces with the same target identified set have
the same Bayes decision floor.

**Finite counterexample.** Both binary models have identified set
\(\{0,1\}\). One licensed prior is \((0.99,0.01)\), with Bayes zero--one error
0.01; the other is \((0.5,0.5)\), with error 0.5.

**New research identity.** Calibrated portrait envelopes: provenance for
weights as well as support.

**Next discriminator.** Audit whether weights are licensed and externally
calibrated. If not, retain the set-robust rule rather than inventing a prior.

## N8. World information can be scientifically irrelevant to the target

**Failed conjecture.** Maximizing information about the latent world is a safe
surrogate for maximizing information about the authorized decision.

**Finite counterexample.** Let \(W=(Y,N)\), with decision target \(Y\) one
uniform bit and nuisance \(N\) ten independent uniform bits. A test revealing
all of \(N\) has 10 bits of world information and zero target information. A
test revealing \(Y\) has one bit of both and reduces zero--one decision error
from \(1/2\) to zero.

**New research identity.** Claim-relative experimental design.

**Next discriminator.** Score acquisitions against \(g(W)\) and the declared
loss; use world recovery only when the scientific target truly requires it.

## A1. A policy-state label does not enforce state-dependent availability

**Failed extension.** Destructive, no-repeat or otherwise state-dependent
tests can be handled by mentioning a finite policy state while retaining the
stationary \(\Gamma_n\) recursion over one always-available set \(E\).

**Finite counterexample.** Two equiprobable target worlds have zero--one loss.
A zero-cost test reveals the world perfectly but is illegal in the initial
laboratory state. The stationary recursion admits it and returns value zero;
the legal controlled-state problem has no initial acquisition and value
\(1/2\).

**New research identity.** State-indexed active-identification frontiers.

**Next discriminator.** Define \(\Gamma_{n,s}\), \(E(s)\), state-dependent
costs/kernels and next-state transitions, then compare the recurrence with
exhaustive enumeration of legal destructive and no-repeat policy trees.

## A2. Policy attainment does not imply a least-favourable prior exists

**Failed extension.** Because the robust policy minimum is attained for an
arbitrary credal set, an attained worst-case prior also exists.

**Finite counterexample.** Let
\(\Pi=\{(\theta,1-\theta):0<\theta<1\}\) and risk vector \(v=(1,0)\).
Then \(\sup_{p\in\Pi}p\cdot v=1\), but no licensed prior attains that value.

**New research identity.** Approximate least-favourable-prior certificates for
open credal registries.

**Next discriminator.** Either prove compactness of \(\Pi\), or report a
convergent sequence of epsilon-worst priors without naming any member least
favourable.

## A3. Zero-cost separation defeats a positive cost obligation

**Failed extension.** The information--cost lower bound supplies a positive
resource obligation even when informative tests can have zero charged cost.

**Finite counterexample.** A zero-cost perfect test separates two opposite
target worlds with exact error zero and total acquisition cost zero. This lies
outside Theorem 4's strict-positive-cost assumption.

**New research identity.** Multi-resource lower bounds with free preprocessing
and zero-cost reachability.

**Next discriminator.** Charge a strictly positive resource gauge or quotient
the entire zero-cost acquisition closure before applying an information--cost
bound.
