# When a Representation Can Certify: Sharp Fibre-Diameter Limits and Minimal Refinement

**ORION-02 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** representation-level certification, exact refinement and refine-or-abstain law  
**Primary route:** TMLR  
**Specialist fallback:** Machine Learning / uncertainty-methods venue  
**Authority:** `BOUNDED_THEORY_READY__PACKAGE_BUILD_OPEN__EMPIRICAL_PROMOTION_OPTIONAL_SUCCESSOR`

## Abstract

A representation can be sufficient for choosing an action while remaining insufficient for certifying the value attached to that action. We give an exact finite-space characterization of this gap. Let a representation `phi` partition instances into fibres, let `V` be the scalar target to be certified and let `D_phi(z)` be the target-value diameter of fibre `z`. Any deterministic point certificate that depends only on `phi(x)=z` has worst-case error at least `D_phi(z)/2`, and this bound is attained by the midpoint of the fibre extremes. Consequently, a fibre-constant certificate with tolerance `eps` exists if and only if `D_phi(z) <= 2 eps`.

The same quantity yields an exact repair calculus. For a finite fibre, the minimum number of refined states required for `eps`-valid certification is the number returned by a greedy interval sweep over the sorted target values. If refinement is restricted to an available separator family, certification is possible exactly when every pair that the separators leave indistinguishable differs in target value by at most `2 eps`. Without refinement, maximum whole-fibre coverage is the probability mass of fibres already satisfying the diameter condition. These results convert an information-loss obstruction into a constructive refine-or-abstain frontier.

Exhaustive independent checks find no violations on the registered finite families and include planted failures to verify that the checkers can reject false statements. We also preserve the adverse empirical programme that motivated the theory. A frozen held-out certificate reached 44/44 nominal coverage but violated its strict target on 20/44 cases; a no-geometry lexical control also reached 44/44 and violated on 14/44. Eleven of 44 realised excesses already exceeded the registered tolerance, making the full-coverage gate arithmetically infeasible, and the available selection score was not detectably associated with realised excess. These observations do not measure the real corpus's fibre diameters. They show why marginal coverage and a weak selector cannot substitute for conditional certifiability. The contribution is therefore a sharp representation-level theorem and exact refinement method, not an empirical superiority or broad transfer claim.

## 1. Introduction

Modern prediction and decision systems rarely operate directly on the full object of scientific interest. They compress an instance into a state, embedding, summary, feature vector or certificate key, and downstream procedures act on that representation. The representation may preserve everything needed for one decision while erasing distinctions needed for another. A state can rank actions correctly but fail to determine their values. A classifier can predict accurately on average while a certificate fails on the subset on which it is used. A compressed record can identify a candidate but not justify a uniform guarantee about every original instance that maps to the same record.

This paper asks a deterministic question that sits underneath statistical calibration:

> When can a fixed representation support a uniformly valid certificate, and what is the smallest refinement required when it cannot?

The answer is governed by the target variation hidden inside each representation fibre. If two instances look identical to the certificate but require substantially different target values, no downstream tuning can recover the erased distinction. This is an information boundary rather than a computational limitation. Unlimited optimization over a certificate that sees only the coarse representation cannot distinguish members of the same fibre.

The same observation also gives a constructive design rule. Once every refined fibre has target diameter no larger than twice the desired tolerance, a valid midpoint certificate exists. Refinement therefore need not be described vaguely as “adding more features.” It can be posed as an exact partition problem: which target-separated instances must become distinguishable, how many refined states are required, and whether the available feature or separator vocabulary can realize that partition.

The paper makes five contributions.

1. It proves the sharp `D/2` worst-case floor for deterministic fibre-constant certificates.
2. It proves the necessary-and-sufficient condition `D <= 2 eps` for tolerance-`eps` certifiability.
3. It gives an exact greedy algorithm for the minimum unconstrained finite refinement.
4. It characterizes realizability under a restricted separator vocabulary.
5. It derives the exact whole-fibre refine-or-abstain coverage identity and relates the theory to a preserved adverse certificate study without claiming that the study directly measured fibre diameters.

## 2. Setting

Let `X` be a finite instance set, `Z` a representation space and

`phi : X -> Z`

an observable representation. For `z in Z`, define the fibre

`F_z = {x in X : phi(x)=z}`.

Let `V : X -> R` be the scalar quantity to be certified. The fibre diameter is

`D_phi(z) = max_{x,x' in F_z} |V(x)-V(x')|`.

A deterministic point certificate is a function `c : Z -> R`. Because `c` receives only `z`, it must issue the same value for every member of `F_z`. At tolerance `eps >= 0`, the certificate is valid on `F_z` when

`|c(z)-V(x)| <= eps`

for every `x in F_z`.

An interval certificate likewise depends only on `z`; write its centre as `c(z)` and radius as `r(z)`. A refinement `phi'` of `phi` is any representation whose fibres are subsets of the original fibres. The theory assumes no distribution, smoothness, model class, exchangeability condition or computational hardness. Those enter only when fibre structure or target values must be estimated from data.

## 3. The sharp certification floor

### 3.1 Point certificates

**Theorem 1 — sharp fibre floor.** For every nonempty fibre `F_z` and every deterministic point certificate `c(z)`,

`max_{x in F_z} |c(z)-V(x)| >= D_phi(z)/2`.

Choose two fibre members whose target separation equals the diameter. By the triangle inequality, their separation is no greater than the sum of their distances from `c(z)`, so at least one distance is at least half the diameter. The bound is attained by the midpoint

`c*(z) = (min_{x in F_z} V(x) + max_{x in F_z} V(x))/2`.

The minimum possible worst-case error of a fibre-constant point certificate is therefore exactly `D_phi(z)/2`.

The theorem is intentionally simple. Its role is to make explicit that a certificate's limit can be caused by representation identity rather than by optimization, sample size or model capacity. If the representation merges target-separated instances, no better learner operating on the same representation can remove the worst-case ambiguity.

### 3.2 Interval certificates

**Theorem 2 — interval floor.** No interval of radius less than `D_phi(z)/2` can contain the targets of every member of `F_z`.

Any interval covering all fibre targets must have width at least their diameter. This interval statement also yields a worst-case probabilistic witness: a conditional distribution placing equal mass on a diameter-attaining pair gives miscoverage at least one half to every smaller fibre-constant interval. The witness establishes possibility, not a claim that real fibres follow that distribution.

## 4. Exact certifiability and minimum refinement

### 4.1 Necessary and sufficient condition

**Theorem 3 — certifiability equivalence.** An `eps`-valid deterministic point certificate constant on `F_z` exists if and only if

`D_phi(z) <= 2 eps`.

Necessity follows from Theorem 1. For sufficiency, the midpoint certificate has worst-case error exactly half the diameter. Thus every original fibre is either already certifiable at the declared tolerance or must be refined or rejected. There is no need for an informal intermediate category.

### 4.2 Exact unconstrained refinement cost

Consider one finite fibre and sort its target values:

`v_1 <= v_2 <= ... <= v_n`.

A refined part is certifiable exactly when its target diameter is at most `2 eps`. The problem becomes covering the sorted values with the fewest intervals of length `2 eps`.

**Theorem 4 — minimum refinement by greedy sweep.** Start at the smallest uncovered target value, place one part containing every subsequent value no more than `2 eps` above it, and repeat on the remaining suffix. The number of parts produced is the minimum possible.

The exchange argument is standard. Any feasible first part containing the smallest remaining value ends no later than that value plus `2 eps`; the greedy part therefore covers at least as many consecutive values as any other feasible first part. Replacing an optimal first part with the greedy one cannot increase the number of remaining parts, and induction completes the proof.

Let `k*(z,eps)` denote this minimum. The exact number of additional representation states needed inside the fibre is `k*(z,eps)-1`. The quantity is information-theoretic: it assumes arbitrary refinements are available.

### 4.3 Separator-constrained realizability

Real systems cannot generally partition instances arbitrarily. Let `S` be a family of predicates or features that may be used to refine the representation. Two instances are `S`-indistinguishable when every separator takes the same value on both.

**Theorem 5 — separator realizability.** An `S`-measurable `eps`-valid refinement exists if and only if every `S`-indistinguishable pair satisfies

`|V(x)-V(x')| <= 2 eps`.

If one indistinguishable pair exceeds the limit, every representation measurable with respect to `S` keeps the pair in one atom and cannot certify it. Conversely, if no such pair exists, every joint `S`-signature has diameter at most `2 eps`, and midpoint certificates are valid on all signatures.

This separates two questions that are often conflated. `k*` is the best possible partition size under unrestricted information. Separator realizability asks whether the information a system can actually compute contains the distinctions needed to attain that optimum—or any valid refinement at all.

## 5. The refine-or-abstain frontier

Suppose original fibres have probability mass `P(phi=z)` under a declared population. A whole-fibre certificate that either accepts all members of a fibre or abstains on all of them may accept exactly the fibres with `D_phi(z) <= 2 eps`.

**Theorem 6 — coverage identity.** Maximum whole-fibre coverage without refinement is

`sum_z P(phi=z) * 1{D_phi(z) <= 2 eps}`.

Refining an uncertifiable fibre buys that fibre's probability mass at the state cost needed to split it into certifiable parts. Under unrestricted refinement, the cost is `k*(z,eps)-1`; under a fixed separator family, the cost is the smallest realizable partition or infinity when one target-separated pair is inseparable.

The identity gives a concrete design frontier. For each fibre, a system should ask:

- what target range is hidden by the current representation;
- which separated pairs available features can distinguish;
- how much population coverage the fibre carries;
- what representation, acquisition or abstention cost is required to make it safe.

## 6. Independent verification

The proofs provide general authority. Separate exhaustive programs serve as hostile transcription and implementation checks.

The registered floor checker enumerates 784 finite configurations. It finds no point certificate beating `D/2`, no smaller interval covering both diameter endpoints and no balanced two-point witness with miscoverage below one half. Negative controls reveal member identity to the certificate and require the checker to observe that the floor can then be beaten.

The refinement checker covers 4,704 main configurations plus nested separator enumerations. It compares the greedy count with independent exhaustive set-partition search. The certifiability, necessity, separator and coverage statements have zero violations. Planted false statements trigger the expected alarms, while a no-alarm control remains silent.

These computations do not replace the proofs. They demonstrate that the executable interpretations match the manuscript statements on broad bounded families and that the test harness can detect counterexamples.

## 7. The empirical failure that motivated the theory

The theoretical paper arose from a sequence of certificate constructions whose failures remain part of the result history.

A first held-out attempt improved coverage to 32/44 but failed a frozen 0.95 coverage gate. Its lexical negative control reached 39/44, so the proposed geometry did not outperform a simple outcome-independent control.

A second arm-conditional construction reached 44/44 nominal coverage but produced 20/44 strict held-out violations. A matched lexical control also covered all 44 cases and produced 14 violations. Full coverage at the registered tolerance was already impossible on the realised sample: 11/44 excesses exceeded `tau=0.02`, while the gate allowed at most a 0.10 violation rate. A split-conformal bound valid at the registered level was 0.061381, approximately 3.07 times the target tolerance.

An oracle abstention analysis found a safe interior operating point: removing the 25% largest realised excesses left 33 cases with zero violations and a bound of 0.016837. That oracle is not deployable because realised excess is unavailable at decision time. The available pre-outcome score did not recover it. Its Pearson correlation with realised excess was -0.1442, with permutation `p=0.3528`; score-based abstention made retained violation rates worse.

The correct conclusion is narrow. The study establishes an invalid certificate, an infeasible full-coverage gate on the realised excess distribution and an inadequate selector. It does not identify the actual representation fibres or measure `D_phi(z)` on the corpus. The theory states what a successor must estimate: target variation conditional on the observable representation and separators that can distinguish the high-variation cases.

## 8. Relation to prior work

The paper does not claim the underlying mathematical ingredients as new in isolation. Sufficient-statistic and comparison-of-experiments theories already make information relative to a decision problem. Robust decision theory studies sets of states compatible with observations. Interval covering on a line supplies the greedy primitive. Conformal and selective-inference methods govern sampling and selection validity.

The residual is their exact composition at the representation-certification interface: a sharp fibre floor, a necessary-and-sufficient tolerance condition, exact minimum refinement, separator realizability and a whole-fibre coverage law, with statistical calibration and selector quality kept as separate layers.

## 9. Limitations

The theory is finite and deterministic. It does not solve estimation of fibre extremes in large or continuous spaces. Exact target values may be unavailable, and learned separators may introduce their own uncertainty. Distribution shift can change fibre mass or target variation. A refinement valid for one claim or tolerance need not support another.

The empirical certificate programme is small and domain-specific. Its adverse outcome motivates the distinction but does not validate the theoretical quantities in natural data. No claim is made about broad model performance, causal benefit of refinement, or universal optimality of the chosen representation vocabulary.

## 10. Reproducibility and availability

A release package should bind the theorem statements and proofs, exhaustive checkers, planted counterexamples, adverse certificate records, selector diagnostics and exact reproduction environment. The anonymous manuscript and named archive should point to the same immutable scientific payload while keeping identity-bearing metadata outside the blinded surface.

## 11. Conclusion

A certificate cannot recover distinctions that its representation erases. On each fibre, half the target diameter is the exact worst-case point-certification floor, and diameter at most twice the tolerance is exactly the condition for a valid fibre-constant certificate. The obstruction is constructive: greedy interval covering gives the minimum unrestricted refinement, separator indistinguishability characterizes realizability, and fibre mass gives an exact refine-or-abstain frontier.

The result turns a failed-certificate problem into a measurable representation-design problem. A successor should not merely tune a bound or increase model capacity. It should determine which target-separated instances have been merged, acquire the distinctions needed to split them, or abstain where those distinctions remain unavailable.

---

## Editorial production note — not manuscript prose

This master preserves the current V3 theorem set and adverse empirical ceiling. Before adoption, reconcile it with `MANUSCRIPT_V3.md`, `CLAIM_LEDGER_V3.md` and the verified paper-local bibliography; then rebuild the target template, figures, anonymous/named surfaces, archive and exact-byte manifest. No claim should be widened to empirical transfer without a new prospectively frozen study that directly estimates or bounds the relevant conditional variation.
