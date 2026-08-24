# Adversarial theorem audit ledger: P1--P5 theory stack

**Audit date:** 2026-08-23  
**Role:** internal adversarial mathematical review, not external or independent peer review  
**Scope:** every theorem, proposition, and labelled corollary newly added to the
P1--P5 theory sections, plus all three clauses of the programme stagewise-
sufficiency theorem. Empirical terminals were treated as immutable inputs and
were not reinterpreted.

**Baseline:** the row-by-row adversarial attempts audit integrated commit
`1b27b32b`. Several counterexamples were reported while the audit was running
and were then repaired in the shared checkout. The final section records the
separate post-repair re-audit so that repaired statements are not incorrectly
reported as still false.

## Verdict key

- **SOUND:** the stated assumptions defeat the attempted counterexample.
- **SOUND+ASSUMPTIONS:** mathematically correct after assumptions already
  suggested by the surrounding prose are made explicit.
- **OVERSTATED:** a nearby conditional theorem is true, but the displayed
  wording asserts more.
- **FALSE-AS-WRITTEN:** an explicit model satisfies the displayed assumptions
  and violates the conclusion, or a claimed optimum need not exist.
- **ILL-POSED:** a probability, conditional law, measurable rule, maximum, or
  minimum used by the statement is not defined under its declared objects.

The symbol `TV` in this audit means
`sup_B |P(B)-Q(B)|`, equal to one half of the `L1` distance when densities
exist. “Exact” is separated into pointwise exactness on the declared world set
and almost-sure exactness under a declared probability law.

## P1: epistemic transition envelopes

| ID | Audited result | Explicit adversarial attempt | Verdict | Required repair or residual problem |
|---|---|---|---|---|
| P1-A1 | Proposition 1, sound non-compensatory minimality | Use an empty admissible set, an infinite descending admissible chain, or a two-element minimal antichain. The first and third do not satisfy the antecedent `Gamma(e)=r`; the second violates well-foundedness. | **SOUND** | Say that the final optimization claim concerns a selector whose codomain is the front; an optimizer that returns outside its declared domain is not covered. |
| P1-A2 | Theorem 1, exact donor substitution | Let a fibre contain two decisions. Any `g(phi(e))` is single-valued and fails one; if every fibre is pure, choosing its unique decision defines `g` on `im(phi)`. Empty `E` is harmless. | **SOUND** set-theoretically | If a measurable or computable policy is intended, fibre constancy alone is not enough without a measurable-factorization or effective-quotient assumption. Distinguish these stronger variants. |
| P1-A3 | Corollary 1, information-equivalent products tie | Try two contexts with isomorphic but differently named revision sets. The corollary survives only if “reconstructs the tuple” includes the identity correspondence needed by the same decision rule. | **SOUND+ASSUMPTIONS** | State reconstruction up to a decision-preserving isomorphism, not merely equal component counts or unaligned encodings. |
| P1-A4 | Theorem 2, mixed-fibre Bayes bound | Take `E=[0,1]`, Lebesgue law, constant `phi`, and let `Gamma` be the indicator of a nonmeasurable subset. `Gamma(E)` is not a random variable and `p_y(z)` is undefined although the displayed assumptions mention only measurability of `phi`. | **ILL-POSED** | Require measurable `Gamma`, standard-Borel `Z`, a finite nonempty discrete output alphabet, and measurable Markov-kernel decoders. Then a fixed-order measurable argmax attains equality. |
| P1-A5 | Corollary 2, component essentiality and half-error clause | On one positive-mass fibre put class probabilities `(0.1,0.1,0.8)`. The fibre “contains two equiprobable decision classes,” yet Bayes error is `0.2`, not at least `0.5`. A zero-mass fibre also has no ordinary conditional class probabilities. | **FALSE-AS-WRITTEN** for the second sentence; first sentence is sound pointwise | Replace by `error = 1-max_y p_y(z)` on positive-mass fibres. The `1/2` conclusion requires that exactly two classes exhaust the fibre with probability `1/2` each. |
| P1-A6 | Corollary 3, licence-coupling impossibility | Let the context set be a singleton, or let `J_e` be a deterministic function of the remaining exposed fields. Omitting the separately named `J` coordinate then leaves pure decision fibres and an exact policy exists. | **FALSE-AS-WRITTEN** as a universal claim | Conditional essentiality is true iff the declared world class contains two contexts with the same reduced interface and different `Gamma`. The constructed two-world pair proves impossibility for a class containing that pair, not for every concrete interface. New problem **RP-LICENCE-REDUNDANCY**: characterize when authority is derivable from the retained interface. |
| P1-A7 | Theorem 3, conservative-envelope criterion | Test empty old fronts, new incomparable elements, and new elements below or above old minima. With the admissible extended order well founded, equality of fronts forces every new nonminimum to have an embedded old minimum below it; both conditions are necessary and sufficient. | **SOUND** | Make “below/above” explicitly strict. The proof also uses transitivity and the definition that every nonempty restricted subset has a minimal element. |
| P1-A8 | Proposition 2, universal front representation | Use an empty antichain, infinite antichain, or a non-well-founded ambient poset. The upward closure still has exactly the generators as minima; global well-foundedness is unnecessary. | **SOUND** | State that `H(e)` is an antichain in the reflexive partial order and `min` uses its strict part. This representation is structural and highly permissive, not an empirical universality claim. |

## P2: acquisition--authority envelopes

| ID | Audited result | Explicit adversarial attempt | Verdict | Required repair or residual problem |
|---|---|---|---|---|
| P2-A1 | Donor monotonicity | Add a policy point that dominates every old frontier point. The old *frontier* disappears, but the closed attainable set still grows because closure preserves inclusion. | **SOUND** for envelope inclusion | Do not imply Pareto-frontier inclusion: guarded attainable sets are monotone; sets of maximal/frontier points generally are not. |
| P2-A2 | Run-conditional acquisition ceiling | Permit arbitrary ranking and synthesis but prohibit invented evidence. Because submitted gold identities remain a subset of acquired gold identities, neither cardinality nor necessary-evidence obligation weight can exceed the stated ceiling. | **SOUND** | Retain nonempty gold, nonnegative weights, normalized identity, and the necessity (not sufficiency) of acquiring an element of `E_o`. |
| P2-A3 | Equal call counts do not identify exposure | For any positive integer `m`, one interface deterministically returns the sole gold item and another has disjoint output support. Both use `m` calls. | **SOUND** as an existential non-identification result | It does not say extremes exist under every fixed access contract. Call budget and source/action support must be named separately. |
| P2-A4 | Closure factorization | Put a state value in `S` that is outside `im(s)`. Fibre constancy does not define `g` there, but `Y_C` is nonempty, so `g` can be extended arbitrarily off-image. A mixed nonempty fibre defeats exactness. | **SOUND+MINOR-PROOF-GAP** | Define `g` first on `im(s)` and extend arbitrarily to `S`; add measurable-factorization assumptions if `g` must be measurable. |
| P2-A5 | Indistinguishable-world TV lower bound | Allow a third `cannot-check` output and randomization. Grouping all non-close outputs makes a binary test: `F_1=P_1(close)` and `L_0=1-P_0(close)`, so `F_1+L_0>=1-TV`. If laws coincide the sum is exactly one. | **SOUND+ASSUMPTIONS** | State common measurable transcript space, Markov-kernel decision rule, and the TV convention above. If `cannot-check` has a distinct graded loss, this binary formula no longer represents total risk. |
| P2-A6 | Maximally permissive sound completion | Let `R(h)=empty` but let provider observability be “unestablished.” As written, the first branch can close whenever “task contract is valid,” before the later unestablished-observability branch. Separately, adversarial realizability is assumed only for `R(h)!=empty`, so it does not prove that every other refused history has a nonclosable compatible world. A sound rule can strictly add a refused `R=empty` history if all its compatible worlds are in fact closable. | **FALSE-AS-WRITTEN / UNDERDEFINED** | Define `K(h)` as compatible worlds and close exactly when every `w in K(h)` is closure-safe. A registry rule is maximally permissive iff its conjunction of empty obligations, provider/observability validity, and other guards is equivalent to that robust-safe condition. New problem **RP-REGISTRY-COMPLETENESS**: prove both directions for a concrete obligation registry. |
| P2-A7 | Corollary, acquisition enlarges authority only by fibre splitting or obligation discharge | Let `R(h)=empty` and all compatible worlds be closable, but provider authenticity is initially unestablished. A donor authenticates the provider. Closure authority expands without splitting a target fibre or discharging an obligation as `R` is currently defined. Budget-reachability and output-alphabet changes are other omitted channels. | **FALSE-AS-WRITTEN** | Exhaustive invariant: authority cannot change if the compatible-world set/partition, obligation state, all contract-validity guards, reachable histories under budget, and output/action alphabet all remain fixed. Fibre refinement and obligation discharge are important sufficient mechanisms, not an exhaustive pair. |

## P3: epistemic portrait envelopes

| ID | Audited result | Explicit adversarial attempt | Verdict | Required repair or residual problem |
|---|---|---|---|---|
| P3-A1 | Fibre criterion for identification | At a fixed nonempty fibre, singleton image, fibre constancy, and existence of one common answer are equivalent. But no measurable spaces are declared. Globally, take `Omega=Y={0,1}`, `Sigma_Omega=2^Omega`, trivial `Sigma_Y`, identity `O`, and discrete query output. Fibres are singletons, yet the induced identity decoder is not `Sigma_Y`-measurable. | **SOUND set-theoretically; ILL-POSED measurably** | Replace “observation-measurable” in the local statement by “observation-only.” For a global measurable decoder require `qG` to be `sigma(O)`-measurable (or a quotient condition), not just fibre constancy. New problem **RP-MEASURABLE-QUOTIENT**. |
| P3-A2 | Universal factorization of sufficient interfaces | By definition any sufficient `S` has a decoder onto `T_q`, so it refines `T_q`. Additional information in `S` cannot change the displayed *set-robust* loss table after `T_q` is recovered. For unrealized `y`, however, `T_q(y)` can be empty and `sup` over it has no declared decision meaning. | **SOUND+ASSUMPTIONS** | Restrict decision claims to `y in O(Omega)` or define an explicit invalid-observation terminal. The “same actions” conclusion is for the displayed worst-case loss; probability-sensitive Bayes decisions can differ if summaries also carry licensed probabilities. |
| P3-A3 | Information-refinement monotonicity | A refined fibre is a subset of the coarse fibre. Images and suprema shrink, and minimizing over a common nonempty action set preserves the inequality. No finite counterexample exists under these assumptions. | **SOUND** | Require a common nonempty action set and defined nonempty identified sets at realized worlds. Finiteness is sufficient for minimum attainment but not necessary if infima are used. |
| P3-A4 | Closed-form robust merge/split/unresolved risks | Suppose the only licensed probability is `p=0.5`, while a loose report merely says `p in [0.2,0.8]`. The actual worst false-merge loss is `0.5 c_FM`, not `0.8 c_FM`. Thus membership in a bounding interval does not make both endpoints feasible. | **OVERSTATED** | If the credal set is exactly the full interval, the formulas are correct. For an arbitrary nonempty credal set `K_y`, use `c_FM(1-inf K_y)`, `c_FS sup K_y`, and `c_U`; loose external bounds give upper bounds, not equalities. New problem **RP-CREDAL-SHARPNESS**. |
| P3-A5 | Pairwise compatibility is insufficient | With constant `O` and `C1={1,2}`, `C2={2,3}`, `C3={1,3}`, all pairwise intersections are nonempty and the triple intersection is empty. | **SOUND** | Explicitly include the observation fibre in “pairwise compatible” when applying the proposition to data. This is an elementary obstruction; algorithmic novelty must come from richer constraint structure. |

## P4: verification-axis identifiability

| ID | Audited result | Explicit adversarial attempt | Verdict | Required repair or residual problem |
|---|---|---|---|---|
| P4-A1 | Proposition 1, exact-axis attainability | On any positive-mass finite fibre a rule emits one allowed terminal; zero error requires singleton conditional target support contained in the output alphabet. Randomization cannot improve the maximum conditional success. | **SOUND+ASSUMPTIONS** | Require a nonempty output alphabet. The proposition is almost-sure under the benchmark law, not pointwise on zero-mass worlds. |
| P4-A2 | Corollary 1, donor-product factorization and mixed-fibre bound | Put probability one on `w0` and zero on an observationally identical `w1` with the opposite target. Bayes error is zero almost surely, yet pointwise extensional equivalence on `{w0,w1}` is impossible. | **OVERSTATED BY MIXING QUANTIFIERS** | State two results: pointwise factorization iff every declared fibre is pure and alphabet-compatible; almost-sure factorization/Bayes risk iff positive-mass conditional fibres are pure. Use an expectation for general `D`, or retain the finite-support sum explicitly. |
| P4-A3 | Proposition 2, claim-level TV lower bound | Add randomization or nondominated measures. Every rule still has equal-prior error at least `(1-TV)/2`; identical laws make every observation uninformative and a constant guess attains `1/2`. | **SOUND+ASSUMPTIONS** | Declare the common measurable space and TV convention. “Minimum” may be safest as `infimum` on pathological measurable spaces; the lower bound itself is unaffected. |

## P5: minimal method revision

| ID | Audited result | Explicit adversarial attempt | Verdict | Required repair or residual problem |
|---|---|---|---|---|
| P5-A1 | Theorem 1, revision factorization | A cross-decision fibre defeats every single-valued rule; pure fibres define a decoder on `im(phi)`. Infinite or incomparable revision fronts do not change the argument because the output is the front itself. | **SOUND** set-theoretically | A measurable/implementable selector needs the same additional quotient assumptions as P1/P3. |
| P5-A2 | Theorem 2, arbitrary-loss Bayes bound and zero-one specialization | The conditional law and measurable selector are undeclared for arbitrary `Z`. More decisively, let `Y={0,1}`, `D={abstain}`, and use `L(a,y)=1[a!=y]`; every rule has risk one, whereas `1-E max_y p_y(Z)` can be zero on pure fibres. | **ILL-POSED**, and the zero-one display is **FALSE-AS-WRITTEN** | Require standard-Borel `Z`, measurable target/interface, finite nonempty `D,Y`, and measurable kernels. The first formula is correct. The second requires `D=Y` (or every target label is available with ordinary classification loss); otherwise use `1-E[max_{a in D} P(Y=a|Z)]` only when actions are target labels. |
| P5-A3 | Corollary 1, no sound-and-complete self-promotion | Two protected states share the exact internal transcript but require opposite binary actions. Any transcript-only action is equal in both, so it violates soundness or completeness. | **SOUND** | The result proves the need for a protected distinguishing interface, not necessarily a human or physically external evaluator. Cryptographic or isolated custody can satisfy the information condition. |
| P5-A4 | Theorem 3, discriminator cover and minimum-cost set cover | Pair coverage is exactly equivalent to unique cross-decision joint signatures. But let one required pair be distinguished by tests `t_n` of cost `1/n`. Exact panels exist with costs tending to zero; no minimum-cost panel exists. `T` was not declared finite. | Cover equivalence **SOUND**; claimed minimum **FALSE-AS-WRITTEN** | Say “infimum equals the weighted set-cover infimum” for arbitrary `T`. A minimum exists if `T` is finite, or more generally if every realized incidence pattern has an attained least cost. New problem **RP-DISCRIMINATOR-EXISTENCE**. |
| P5-A5 | Proposition 1, adaptive leaf purity | For a deterministic terminating decision tree, two cross-decision states at one reachable leaf force one wrong output; pure leaves admit their common label. | **SOUND** for deterministic fixed outcomes | The following prose must use equality of complete adaptive transcript laws, not merely identical one-test marginals. Two tests can each be marginally fair in both states while their joint correlation differs. New problem **RP-STOCHASTIC-DISCRIMINATION**: characterize sequential Bayes/minimax risk and cost under history-dependent kernels. |

## Programme theorem: stagewise sufficiency and irreversible collapse

| ID | Audited clause | Explicit adversarial attempt | Verdict | Required repair or residual problem |
|---|---|---|---|---|
| U-A1 | Exactness by composition of stagewise factor maps | With correctly typed deterministic maps `S_0 -> S_1 -> ... -> S_m -> Y`, composition is exact. The prose does not explicitly give these compatible domains, but no counterexample survives once it does. | **SOUND+FORMALIZATION** | State the commuting diagram: each required next state equals its factor map of the supplied interface, and the final target equals the final factor. |
| U-A2 | A collapsed cross-target pair cannot be repaired downstream | If all later variables are deterministic functions of `S_i`, equal `S_i` values remain equal downstream. A later experiment that queries the world defeats the conclusion, but violates the premise. | **SOUND+SCOPE-RISK** | Replace “later stage” by a Markov/no-new-world-information condition. The theorem does not apply across feedback loops that acquire fresh evidence. New problem **RP-ACTIVE-REOPENING**: quantify how much new experiment channels can undo an earlier collapse. |
| U-A3 | Conditional Bayes impurity lower bound | Without a probability law, measurable target, regular conditional probabilities, or finite/standard-Borel output, the impurity is undefined. A later random variable correlated with the world can beat it unless excluded. | **ILL-POSED** | Under a joint law, finite target alphabet, standard-Borel interface, and downstream Markov chain `Y - S_i - U`, every `U`-based rule has risk at least the Bayes risk from `S_i`; unrestricted `S_i` decoding attains it. |

## Triage summary

The factorization, refinement, finite-fibre, TV, and partial-order cores survive
adversarial attack. The manuscript stack nevertheless contains **six blocking
statement defects** before a mathematical-review claim should be made:

1. P1's universal licence-omission impossibility;
2. P1's two-equiprobable-classes half-error wording;
3. P2's maximally permissive completion and its purported exhaustive corollary;
4. P3's interval-risk equality without a sharp credal-set assumption;
5. P5's zero-one specialization for an arbitrary action set;
6. P5's minimum-cost existence for an unrestricted test family.

In addition, all population Bayes claims and the umbrella theorem require one
shared measurable-probability convention, and P4 must not mix pointwise
extensional equivalence with almost-sure benchmark attainability.

## Post-repair re-audit of the shared checkout

The following baseline defects were repaired after they were found:

- P1 now restricts the half-error statement to exactly two exhaustive
  half-probability classes and makes licence essentiality conditional on a
  witnessed cross-decision fibre.
- P2 now defines the compatible-world robust-safe set, proves its unique
  maximality directly, and states registry soundness and completeness as
  separate implications.
- P3 now declares the credal interval sharp and closed.
- P4 now separates pointwise factorization from almost-sure benchmark
  attainability.
- P5 now restricts its zero-one formula to `D=Y` and declares a finite test
  family before invoking a minimum-cost set-cover optimum.
- The umbrella now declares standard-Borel spaces, measurable maps, a finite
  target alphabet, and no later world-bearing observation.

The final shared-checkout re-audit confirmed that the remaining findings were
also repaired:

- P1 now makes `Gamma` measurable and its finite output alphabet nonempty.
- The umbrella now declares `W ~ mu` and makes the downstream no-new-world-
  information premise a Markov condition.
- P3 now says “observation-only” in its local set-theoretic theorem and gives
  the separate measurable-decoder boundary.
- P2 now defines robust-set enlargement through changes to the observation or
  compatible-world class and lists validity, obligation, fibre, and registered
  reachability channels without claiming exhaustiveness beyond its state.
- P5 now uses complete adaptive transcript laws/history-conditional kernels
  for stochastic nonseparability and makes the action set nonempty.
- P4's output alphabet was made nonempty while retaining the pointwise versus
  almost-sure distinction.

**Current mathematical disposition:** no explicit counterexample in this audit
still breaks a corrected displayed theorem under its final stated assumptions.
The receipt remains important provenance for why the assumptions are present;
it must not be read as a counterexample to the repaired versions. The open
items are now research-strength and novelty problems---measurable/effective
factorization beyond the declared setting, concrete registry completeness,
active reopening, stochastic discriminator cost, credal sharpness, and
naturalistic external validity---rather than known theorem-validity defects.
