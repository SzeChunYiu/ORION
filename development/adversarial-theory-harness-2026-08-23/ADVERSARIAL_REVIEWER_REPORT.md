# Adversarial mathematical reviewer report: P1--P5 and the programme theorem

**Date:** 2026-08-23  
**Status:** internal adversarial review; not external, independent, or blinded  
**Review boundary:** scientific and mathematical content only. No pytest, CI,
manuscript build, empirical rerun, or historical-terminal mutation was used.

The counterexamples below were generated against integrated commit
`1b27b32b`. The shared checkout was repaired concurrently after the findings
were reported; see `THEOREM_AUDIT_LEDGER.md`, “Post-repair re-audit,” for the
current residual list.

**Final post-repair disposition:** every statement-level counterexample found
in this review has been answered by an explicit assumption or a corrected
theorem in the shared checkout. No known counterexample from this audit breaks
the final displayed results. The remaining gap is research strength, novelty,
and external empirical authority, not a known contradiction in the repaired
theorem layer.

## 1. Overall verdict

The new stack has a coherent and defensible core:

- set-theoretic factorization through information fibres;
- conditional Bayes risk on a finite decision alphabet;
- information-refinement monotonicity;
- total-variation testing lower bounds;
- minimal fronts in well-founded partial orders;
- deterministic cross-decision test covers; and
- pairwise-versus-global constraint incompatibility.

Those cores survive explicit counterexample attempts. The baseline stack was
not mathematically review-ready, however. Several manuscripts promoted a valid
conditional or almost-sure fact into an unconditional or pointwise statement.
The most serious error is P2's claim of a maximally permissive closure rule:
the stated realizability assumption does not characterize every history the
rule refuses, and the displayed branch order does not visibly require
observability/provider validity when `R(h)` is empty. P1, P3, and P5 contain
smaller but real counterexamples documented in the ledger.

The central publication-quality gap is deeper than these repairs. Much of the
new theorem layer is a correct specialization of elementary factorization,
Bayes decision theory, robust set-valued decision theory, hypothesis testing,
and set cover. The manuscripts mostly acknowledge that inheritance. A top-tier
theory contribution therefore cannot rest on restating the same fibre lemma in
five application vocabularies. It needs at least one technically nontrivial
result that couples the stages: for example, a sharp value/cost theorem for
active fibre refinement, a stochastic discriminator sample-complexity result,
or a necessary-and-sufficient registry-completeness theorem under adversarial
world completion.

This is not a recommendation to narrow the scientific ambition. It is a
recommendation to widen it correctly: replace repeated deterministic
factorization statements by one umbrella theorem, then make each paper own a
genuinely stronger specialization with assumptions and falsifiers that are
not inherited for free.

## 2. A common corrected mathematical foundation

The following results repair the stack under the widest assumptions supported
by its intended interpretation.

### 2.1 Pointwise factorization

**Theorem R1 (set-theoretic decision factorization).** Let `Omega`, `S`, and
`Y` be sets, let `s: Omega -> S`, and let `f: Omega -> Y`. The following are
equivalent:

1. there is `g: im(s) -> Y` with `f = g o s`;
2. `s(omega)=s(omega')` implies `f(omega)=f(omega')`.

If `Y` is nonempty, `g` can be extended to all of `S`. This statement is
pointwise, has no probability assumptions, and applies to the P1 transition,
P2 closure, P3 query, P4 terminal, and P5 revision maps.

**Proof.** A factor map takes one value at a shared interface value, proving
necessity. Under fibre constancy, assign to each `z in im(s)` the common value
of `f` on `s^{-1}(z)`. This is well defined. If required, assign any fixed
element of nonempty `Y` off the image. QED.

**Measurability boundary.** Fibre constancy is not by itself a universal
measurable-factorization theorem. If decisions must be measurable, one must
also require that the induced factor is measurable. Equivalently, in the
ordinary random-variable formulation, `f` must be measurable with respect to
`sigma(s)`. A concrete warning is `Omega=S={0,1}` with a full sigma algebra on
`Omega`, the trivial sigma algebra on `S`, identity `s`, and discrete identity
target `f`: all fibres are singletons, but the induced identity decoder on `S`
is not measurable.

This correction should be applied consistently rather than adding different
measurability conventions to P1, P3, and P5.

### 2.2 Bayes risk, garbling, and the corrected stagewise theorem

**Theorem R2 (finite-target Bayes risk and irreversible garbling).** Let
`(Y,S,U)` have a joint law, where `Y` takes values in a finite nonempty set and
`S` and `U` are standard-Borel random elements. Let the downstream observation
be a garbling of `S`, meaning the Markov condition `Y - S - U`. Under zero-one
loss,

`R*(S) = E[1 - max_y P(Y=y | S)]`

is the smallest error among measurable possibly randomized rules using `S`,
and every rule using only `U` has error at least `R*(S)`. Equality at zero is
possible exactly when `P(Y in . | S)` is a point mass almost surely and the
corresponding label is available in the action alphabet.

For a finite nonempty action set `A` and measurable loss `L(a,y)`, replace the
display by

`E[min_{a in A} sum_y L(a,y) P(Y=y | S)]`.

**Proof.** Conditional on `S=s`, a randomized action has risk equal to a convex
combination of the finitely many conditional action risks. It cannot beat their
minimum; a fixed-order measurable tie break attains that minimum. For the
garbling claim, any `U`-based randomized decision, composed with the kernel from
`S` to `U`, is an `S`-based randomized decision, so it cannot beat the optimum
available from `S`. QED.

This is the correct stochastic programme theorem. Its pointwise deterministic
counterpart is Theorem R1. It also supplies the repairs for P1 Theorem 2, P4
Proposition 1's population reading, and P5 Theorem 2.

**Important non-applicability.** A later stage that performs a fresh experiment
on the world is not a garbling of the earlier interface. It can refine the
fibre and lower risk. Therefore “irreversible collapse” is true only between
acquisition events or across a downstream Markov chain. The P1--P5 feedback
loop must not be treated as one irreversible one-pass pipeline.

### 2.3 Correct essentiality of an omitted coordinate

**Theorem R3 (conditional coordinate essentiality).** Write a full interface
as `(X,J)` and a reduced interface as `X`. Omitting `J` prevents pointwise exact
decision on a declared class `Omega` if and only if there exist
`omega,omega' in Omega` such that

`X(omega)=X(omega')` but `f(omega)!=f(omega')`.

Under an equal mixture on such a pair, every reduced-interface rule has
zero-one error at least `1/2`. If a positive-mass reduced fibre has conditional
class probabilities `(p_y)`, its exact conditional Bayes error is
`1-max_y p_y`.

**Proof.** Apply Theorem R1 for the pointwise statement and Theorem R2 to the
two-point or general conditional law. QED.

This replaces P1's universal licence-coupling corollary. Omitting a coordinate
name is not itself an impossibility; its information may be redundant or
derivable. The scientific question is whether the protected world class
contains a witnessed cross-decision collision after the omission.

### 2.4 Conservative extension of a revision front

P1's conservative-envelope theorem is correct and can serve as the shared
partial-order result without repair.

**Theorem R4 (front preservation).** Under an order embedding that exactly
preserves old admissibility and a well-founded extended admissible order, the
new minimal front equals the embedded old front iff no genuinely new
admissible element is strictly below an old minimum and every genuinely new
admissible element is strictly above some old minimum.

**Proof sketch.** The two conditions respectively preserve minimality of every
old minimum and prevent every new element from being minimal. Conversely, if
fronts agree, a new predecessor would remove an old minimum. Every new
nonminimum has a minimal element in its down-set by well-foundedness; equality
of fronts makes that element an embedded old minimum. QED.

The empty-front case is included: if the old admissible set is empty, equality
of fronts requires the new admissible set to remain empty.

### 2.5 Robust closure and actual maximal permissiveness

P2 needs a different theorem rather than a verbal patch.

Let `K(h)` be the nonempty set of task worlds compatible with history `h`, and
let `c(w)=1` mean that closure is scientifically valid in world `w` under the
declared contract. Define

`Safe = {h : for every w in K(h), c(w)=1}`.

**Theorem R5 (unique robust-maximal closure set).** A pointwise robust-sound
closure rule may close only histories in `Safe`. The rule that closes exactly
`Safe` is sound and is the unique maximally permissive sound rule in the order
of closure-set inclusion.

**Proof.** Closing outside `Safe` closes in at least one compatible world with
`c(w)=0`, violating soundness. Closing exactly `Safe` is correct in every
compatible world at each history it closes. Every other sound closure set is
therefore a subset. QED.

Let `P(h)` be the implemented conjunction of empty registered obligations,
provider and observability validity, custody, resource, and any other hard
closure guards. Then the registry rule `close iff P(h)` equals the robust-
maximal rule **if and only if**

`P(h) <=> h in Safe`

for every declared history. The forward direction is registry soundness; the
reverse direction is registry completeness. P2's current adversarial
realizability assumption addresses only part of the reverse direction, namely
some histories with nonempty `R(h)`. It must also cover every other failed
guard, and `P(h)` must be evaluated as one conjunction before branch ordering.

This theorem is wider than the current obligation-specific claim because any
future donor can alter observations, world compatibility, obligation status,
validity, reachability, or action alphabets. It also gives an exact target for a
top-tier P2 theorem: prove that a concrete registry predicate equals `Safe` for
a nontrivial scientific-world model.

### 2.6 Identified sets and credal decisions

P3's set-theoretic identification and refinement results are correct on
realized observations. The robust binary proposition should be replaced by the
following more general result.

**Theorem R6 (binary robust action over an arbitrary credal set).** Let
`K_y` be a nonempty set of licensed probabilities for binary `theta`, with
`l_y=inf K_y` and `u_y=sup K_y`. Under false-merge, false-split, and constant
deferral losses `c_FM,c_FS,c_U >= 0`, the worst-case risks are

- `Rbar(M|y)=c_FM(1-l_y)`;
- `Rbar(S|y)=c_FS u_y`;
- `Rbar(U|y)=c_U`.

Thus deferral is minimax whenever its cost is no larger than the other two
values. If only outer bounds `K_y subset [l,u]` are known, the expressions
using `l,u` are conservative upper bounds and need not equal the true robust
risks.

**Proof.** The first loss is decreasing affine in `p`, so its supremum over
`K_y` is its value at the infimum (as a supremum even if the infimum is not
attained). The second is increasing affine, and the third is constant. QED.

For global measurable decoders, P3 should use the measurable boundary after
Theorem R1. For robust decisions it should restrict to realized observations,
because an empty identified set is a model/interface inconsistency terminal,
not an ordinary set over which scientific loss is optimized.

### 2.7 Pointwise versus benchmark-distribution verification

P4 should split one corollary into two levels.

**Theorem R7 (two verification authorities).** For a declared world class,
pointwise extensional equivalence holds exactly under Theorem R1 plus target-
alphabet membership on every world. Under a benchmark law, zero population
error requires only almost-sure fibre purity and alphabet membership. Neither
condition implies the other on zero-probability worlds unless the benchmark
support equals the declared class.

The existing equal-prior TV result is correct with
`TV(P,Q)=sup_B |P(B)-Q(B)|`. It identifies an evidence limit, not the truth of
either competence explanation.

This distinction matters scientifically. A finite panel can support an
almost-sure claim under its sampling law without establishing an extensional
scientific rule over all declared cases. Conversely, a pointwise theorem can
hold without showing that the required state is observable or estimable on a
naturalistic population.

### 2.8 Deterministic and stochastic discriminator programmes

**Theorem R8 (deterministic discriminator cover with attainment boundary).**
On a finite ambiguous fibre, a nonadaptive deterministic panel is exact iff
its distinguished-pair sets cover every cross-decision pair. For a finite test
family, the least additive cost is exactly the finite weighted set-cover
optimum. For an arbitrary test family, only equality of infima is automatic; a
minimum exists if, for example, every incidence pattern that occurs has an
attained least-cost representative.

**Proof.** A joint test signature is equal for a pair iff no chosen test
distinguishes it. Exactness is therefore precisely pair coverage. With finitely
many tests, the feasible family is finite and a nonnegative-cost minimum is
attained. For arbitrary tests, the same feasible panels define the same
set-cover infimum, but costs `1/n` on tests sharing one required incidence
pattern show that attainment can fail. QED.

**Theorem R9 (adaptive transcript criterion).** Fix a terminating adaptive
policy and let `P_theta` be the induced probability law of its complete test-
action-outcome transcript in latent situation `theta`. Exact decision is
possible almost surely iff there are measurable decision regions such that
every `P_theta` is concentrated on the region carrying `G(theta)`; equivalently,
the transcript laws aggregated over different required decisions are mutually
singular. Under a prior, the minimum zero-one error is the conditional Bayes
impurity given the complete transcript.

**Proof.** A decoder is exact iff its inverse decision regions have probability
one under every state assigned that decision and zero under states assigned a
different decision. This is exactly separation of the decision-indexed laws.
The population statement is Theorem R2 with the transcript as the interface.
QED.

Equality of each test's one-step marginal distribution is not enough to prove
impossibility. For example, two fair-bit tests can be perfectly correlated in
one state and perfectly anticorrelated in another; each marginal is identical,
but the joint transcript identifies the state. A safe sufficient condition for
impossibility is equality of the outcome kernel for every action at every
reachable history, which inductively makes the complete adaptive transcript
laws identical.

## 3. Explicit counterexample suite

The accompanying standalone harness encodes the smallest finite witnesses for
the main statement defects. They are mathematical models, not empirical tests:

1. a three-class fibre invalidating P1's half-error wording;
2. a redundant omitted licence coordinate invalidating unconditional
   essentiality;
3. a refused but robust-safe history invalidating P2 maximality under only the
   displayed `R!=empty` realizability premise;
4. a loose probability interval invalidating P3's risk equality;
5. a zero-mass world separating P4 pointwise from almost-sure exactness;
6. an unavailable-label action set invalidating P5's zero-one specialization;
7. decreasing-cost tests showing that the P5 set-cover infimum need not be
   attained; and
8. equal one-test marginals with different joint correlations, invalidating a
   marginal reading of stochastic nonseparability.

The harness intentionally does not touch pytest or CI. Its receipt is local
counterexample evidence only.

## 4. Recursive research programme opened by the negatives

Every negative finding above becomes a new, discriminating research problem.
None licenses a positive manuscript claim until its theorem or experiment is
completed.

### RP-MEASURABLE-QUOTIENT: when is a scientific interface operationally sufficient?

**Problem.** Characterize interface classes for which pointwise fibre
constancy guarantees a measurable, computable, or statistically learnable
decoder.  
**Positive terminal.** A theorem under explicit standard-Borel/quotient or
effective-representation assumptions, with a counterexample outside them.  
**Negative ascent.** If measurable factorization fails, identify the least
additional interface sigma algebra or representation refinement that restores
it.

### RP-REGISTRY-COMPLETENESS: when do obligations exactly characterize safe closure?

**Problem.** Prove both `P(h)=>Safe(h)` and `Safe(h)=>P(h)` for a nontrivial
world/obligation model, including provider validity, observability, custody,
and invalid-registry histories.  
**Positive terminal.** Equality with the robust safe set and a constructive
completion procedure.  
**Negative ascent.** Every counterworld supplies a missing obligation/guard or
shows that the registry is overconservative; add it under a new contract
identity and retest both directions.

### RP-ACTIVE-REOPENING: how much can new evidence reverse an interface collapse?

**Problem.** Replace the one-pass pipeline by a feedback system where later
stages can buy experiments. Bound reduction in Bayes impurity by experiment
cost, mutual information, total variation, or Blackwell deficiency.  
**Positive terminal.** A tight value-of-information or regret bound with an
attaining acquisition policy on a broad world class.  
**Negative ascent.** A failed bound must expose which adaptive dependence,
nonstationarity, or cost geometry it omitted.

### RP-STOCHASTIC-DISCRIMINATION: beyond deterministic set cover

**Problem.** Given history-dependent experiment kernels, find the minimum
expected or worst-case cost required to reach a declared decision error.  
**Positive terminal.** Achievability and converse bounds, ideally with
approximation guarantees under explicit adaptive-submodularity or likelihood-
ratio conditions.  
**Negative ascent.** Correlated outcomes, model misspecification, or
nonidentical costs become separately frozen successor families rather than
being averaged away.

### RP-CREDAL-SHARPNESS: valid and sharp scientific portrait envelopes

**Problem.** Distinguish an outer probability bound from the sharp image of
the source-compatible world set, and quantify the price of conservative
outer approximation in downstream minimax decisions.  
**Positive terminal.** Coverage plus a bound on excess decision diameter or
regret caused by nonsharpness.  
**Negative ascent.** Coverage failure repairs the world/constraint model;
excess width repairs computation or acquisition. These are different causes.

### RP-LICENCE-REDUNDANCY: when is an authority coordinate genuinely new information?

**Problem.** Determine whether licence/authority is independent of, derivable
from, or only probabilistically predictable from the remaining donor state.  
**Positive terminal.** A witnessed cross-decision collision and its prevalence,
or a representation theorem proving derivability on the declared class.  
**Negative ascent.** If the coordinate is redundant, the architecture claim is
retired and the search moves to the next unresolved relation.

## 5. Harness lanes for continued ascent

The programme should run four scientific harness lanes, each with immutable
terminals.

| Lane | Unit | Gate | Positive terminal | Negative terminal and recursive move |
|---|---|---|---|---|
| H0 finite logic | Small finite worlds, fibres, posets, credal sets, and test families | Enumerate all objects up to a declared size and compare statement to definition | No counterexample in the finite domain plus a human proof that does not rely on finiteness accidentally | Minimal counterexample retained; repair the theorem or open a missing-assumption problem |
| H1 stochastic information | Explicit probability kernels and adaptive transcripts | Compare exact Bayes risk, TV/deficiency bounds, and proposed acquisition policies | Matching converse/achievability bound under named kernel conditions | Gap classified as measurability, correlation, adaptivity, misspecification, or cost-geometry failure |
| H2 adversarial contracts | Compatible-world sets, obligation registries, provider/custody guards | Test both soundness and completeness against `Safe` | Registry predicate equals robust safe set on the declared model | Unsound counterworld adds a guard; overconservative history demands a sharper obligation model |
| H3 external scientific panel | Source-disjoint naturalistic clusters with protected gold and matched donor interfaces | Worst-domain validity, harm, resolution, transfer, and custody gates | Predeclared cross-domain result with source-disjoint replication | Retain the adverse terminal and assign it to acquisition, representation, axis, transition, or revision research |

H0 cannot promote an empirical claim. H3 cannot repair a false theorem by a
favourable average. The lanes must converge: a top-tier claim needs a correct
theorem, an execution whose observation contract satisfies that theorem, and
evidence whose custody supports the intended population statement.

## 6. Manuscript-level disposition

The concurrent repair pass completed items 1--3 below. Items 4--6 remain the
scientific ascent agenda before a top-tier claim:

1. replace the six false/overstated statements listed in the ledger;
2. install one shared conventions paragraph for sets versus measurable spaces,
   pointwise versus almost-sure exactness, nonempty alphabets/actions, regular
   conditional laws, and the TV convention;
3. replace the umbrella's deterministic “irreversible” wording by Theorem R2
   and explicitly exempt fresh-evidence feedback;
4. present Theorem R1 once as parent mathematics, then remove any implication
   that five renamings create five independent theoretical novelties;
5. elevate one recursive problem above into a nontrivial theorem rather than
   relying only on definitions and elementary equivalences; and
6. keep every 7/229, 27/36, saturated-axis, 21/24, `NOT_SUPPORTED`, and
   `CANNOT_CHECK` terminal attached to its original evidence identity.

The correct wide headline after these repairs is not that the programme has
solved naturalistic scientific authority. It is that it has a common
information-and-authority formalism, exact finite witnesses of several
failure modes, and a sharply defined research programme for active recovery of
the missing distinctions. The wider empirical claims still require the
protected source-disjoint studies already frozen by the programme.
