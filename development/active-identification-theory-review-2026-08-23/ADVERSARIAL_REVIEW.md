# Adversarial scientific review: active identification under licensed ambiguity

**Review date:** 2026-08-23  
**Reviewed source:** `development/active-identification-theory-2026-08-23/`  
**Verdict:** `PASS_FINITE_CORE / BLOCK_NOVEL_THEORY_CLAIM / REQUIRE_SCOPE_REPAIRS`  
**Authority:** same-repository adversarial review only; not external peer review, protected evaluation, empirical validation, or a systematic priority search.

## Executive finding

I found **no counterexample to Theorems 1--4, Corollary 1, or Propositions 1--2 under their exact finite, stationary, known-kernel, bounded-horizon assumptions**. The displayed finite arguments are mathematically sound. In particular:

- target-class transcript support separation is equivalent to zero-error decoding on a finite transcript space;
- the single-prior Bellman recursion is correct for an **at-most-\(n\)** horizon;
- the deterministic policy-tree risk vectors are exactly the displayed finite frontier, and world-independent behavioral randomization convexifies it under perfect recall;
- arbitrary nonempty, nonclosed, nonconvex, nonrectangular prior sets are valid for the **ex-ante** support-function minimax problem;
- the oriented KL/cost inequality is a valid necessary bound when every charged cost is strictly positive; and
- the two information-greedy propositions are correctly narrow.

This is not yet a top-tier novel theory contribution. The core mathematics is substantially donor-owned: finite POMDP policy vectors, Bayes/minimax decision theory, multiple-prior rectangularity, controlled sensing/change of measure, log-score information identities, and adaptive submodularity. The defensible residual is presently a **careful synthesis and audit interface** joining P3 support/credal envelopes to P5 adaptive discrimination. Manuscript integration should use that status, not advertise a historically new Bellman frontier or adaptive lower bound.

## Result-by-result audit

| Result | Edge cases checked | Disposition |
|---|---|---|
| Theorem 1, transcript purity (`THEORY.md:104-128`) | finite measurability; composite targets; randomized acquisition; early stopping; decoder existence | **Valid.** On a finite transcript alphabet, pairwise cross-class support disjointness and mutual singularity of positive class mixtures are equivalent. Random decoder noise cannot rescue an impure transcript. |
| Corollary 1 (`130-145`) | full-support noise; adaptive/random test choice; finite horizon | **Valid in the stationary model.** Actions do not create world information because the same policy kernel is used at a common history. Positive KL is compatible with common support and therefore with failure of finite exactness. |
| Theorem 2 (`165-201`) | zero costs; ties; zero-probability outcomes; at-most versus exactly \(n\); deferral | **Valid.** Zero-probability posteriors are harmless only because their Bellman weights are zero. Replace “acquisition is optimal” by “some optimal policy acquires” if a tie could otherwise be read as uniqueness. |
| Theorem 3 (`203-257`) | nonclosed/nonconvex \(\Pi\); policy randomization; attainment; horizon nesting | **Valid with an explicit perfect-recall convention.** \(h_\Pi\) is Lipschitz even for nonclosed \(\Pi\), and the policy minimum is attained on a finite/compact frontier. A worst-case prior itself need not be attained. The behavioral/mixed equivalence assumes world-independent private randomization and complete action--outcome recall. |
| Robust stopping consequences (`259-292`) | deterministic versus randomized stop; nonrectangular conditioning | **Valid as ex-ante statements.** The randomized equality is an existence criterion for a purely terminal randomized optimum, not an operational authorization to randomize a scientific claim. |
| TV identity (`294-305`) | composite target, equal two-point prior | **Valid.** It is the ordinary binary testing identity and only a pairwise lower bound for a larger target problem. |
| Theorem 4 (`307-365`) | oriented KL; infinite/zero KL; policy randomization; bounded stopping; composite target; cost zeros | **Valid and necessary only.** Positive costs are essential. \(\rho=0\) makes the premise impossible for \(\delta<1/2\); \(\rho=\infty\) makes the displayed cost bound trivial. The result gives neither global achievability nor an optimal composite-class allocation. |
| Proposition 1 (`369-387`) | extended log loss; compulsory one-step test; unequal costs | **Valid and classical.** The correct cost rule is \(I(Y;O_e)-c_e\), not a ratio. |
| Proposition 2 (`389-399`) | equal cost/cardinality; adaptive monotonicity/submodularity | **Valid as an inherited conditional theorem.** N3's XOR synergy shows that these hypotheses cannot be inferred from “information gain” or “Bayes-risk reduction” alone. |

## New retained negative results

### A1. A policy-state label does not enforce history-dependent availability in the displayed recurrence

**Overbroad extension:** lines 53--64 suggest that availability/no-repeat rules can be handled by placing state in \(W\) or “the policy state,” while the displayed \(\Gamma_n\) recurrence continues to use the same \(E,K_e,c_e\) at every node.

**Smallest witness.** Let \(W=Y=\{0,1\}\), \(g(w)=w\), uniform prior, and zero--one loss. A zero-cost test \(e\) deterministically returns \(w\), but \(e\) is unavailable in the initial laboratory state. The stationary recurrence with \(e\in E\) returns value 0; the legal controlled-state problem has no initial acquisition and value \(1/2\).

**Corrected statement.** Define state-indexed frontiers \(\Gamma_{n,s}\), legal sets \(E(s)\), state-dependent costs/kernels, and a next-state transition. The displayed theorem applies only to the stationary always-available model. This does not refute Theorems 1--3 as stated; it blocks the informal extension from being used without a new theorem.

### A2. Policy attainment does not imply a least-favourable prior exists

Let \(W=\{0,1\}\), \(\Pi=\{(\theta,1-\theta):0<\theta<1\}\), and risk vector \(v=(1,0)\). Then \(h_\Pi(v)=1\), but no \(p\in\Pi\) attains 1. Theorem 3 correctly states a supremum and proves policy attainment. Any integration text must not silently rename the supremum as an attained “worst-case prior” unless \(\Pi\) is compact.

### A3. Zero-cost separation destroys a positive acquisition-cost obligation

With two target worlds and a zero-cost perfect test, exact error 0 is achieved at total acquisition cost 0. This is outside Theorem 4 because it assumes \(c_e>0\). The successor theory should either charge a strictly positive resource vector or first quotient out the closure reachable through zero-cost acquisitions.

The source negative results N1--N8 remain valid and should remain immutable. None was re-labelled as a positive empirical result.

## Posterior, ambiguity, and policy-randomization boundaries

1. **Posterior conditioning.** For a history with positive likelihood under at least one licensed prior, the displayed \(\Pi_h\) is correct and its support union matches the support envelope. A history impossible under every licensed prior has no posterior; the packet correctly makes it an invalid model/interface terminal. A practical recovery/model-expansion rule is still absent.
2. **Nonrectangular \(\Pi\).** The vector frontier is safe because one policy is evaluated against one ex-ante licensed prior at a time. Posterior-by-posterior worst-case selection is a different, rectangularized game. N5 is a correct finite witness of that distinction.
3. **Behavioral randomization.** The convex-hull claim requires an independent random seed, a policy that cannot observe \(w\), and perfect recall of its action--outcome history. A root mixture and behavioral randomization are outcome-law equivalent under those conditions. Whether randomized terminal scientific actions are ethically or operationally admissible is not a theorem.
4. **Nonattainment.** The optimal policy is attained; a supremizing prior need not be. Approximate least-favourable priors are the most that can be reported for open \(\Pi\).
5. **Composite targets.** Theorems 1 and 4 correctly use \(g\)-classes. The pairwise KL bound is necessary but not sufficient for one policy to solve all cross-class pairs simultaneously.

## Nearest-work and novelty boundary

Primary metadata was checked on 2026-08-23 through Crossref DOI records, plus the JAIR/arXiv/PMLR primary article pages where applicable.

| Packet component | Nearest donor work | Boundary |
|---|---|---|
| Bellman/policy-vector recursion | Smallwood & Sondik, *The Optimal Control of Partially Observable Markov Processes over a Finite Horizon*, DOI `10.1287/opre.21.5.1071` | Theorem 2 and the deterministic part of Theorem 3 are a static-hidden-state specialization of finite-horizon POMDP policy trees/alpha vectors. |
| Robust/ambiguity recursion | Iyengar, *Robust Dynamic Programming*, DOI `10.1287/moor.1040.0129`; Nilim & El Ghaoui, DOI `10.1287/opre.1050.0216`; Wiesemann, Kuhn & Rustem, *Robust Markov Decision Processes*, DOI `10.1287/moor.1120.0566` | These own robust dynamic-programming/rectangular-uncertainty theory. The packet's fixed ex-ante prior-set scalarization is a simpler, different game, not a replacement. |
| Robust POMDP vector formulations | Nakao, Jiang & Shen, *Distributionally Robust Partially Observable Markov Decision Process with Moment-Based Ambiguity*, DOI `10.1137/19M1268410`; Li & Xiang, distance-based ambiguity, DOI `10.1080/24725854.2025.2505980` | These are mandatory direct neighbors before any “robust frontier” novelty claim. |
| Dynamic nonrectangular ambiguity | Epstein & Schneider, *Recursive multiple-priors*, DOI `10.1016/S0022-0531(03)00097-8` | N5 illustrates the established rectangularity/dynamic-consistency boundary. |
| Adaptive KL lower bounds | Naghshvar & Javidi, *Active sequential hypothesis testing*, DOI `10.1214/13-AOS1144`; Nitinawarat, Atia & Veeravalli, *Controlled Sensing for Multihypothesis Testing*, DOI `10.1109/TAC.2013.2261188`; Naghshvar & Javidi, DOI `10.1109/JSTSP.2013.2261279`; Garivier & Kaufmann, PMLR 49 (2016) | Theorem 4 is the standard event data-processing plus adaptive change-of-measure obligation. Novelty would require a sharper composite-target allocation/attainment theorem. |
| Greedy approximation | Golovin & Krause, *Adaptive Submodularity*, JAIR 42 (2011), primary page `https://jair.org/index.php/jair/article/view/11095`, arXiv `1003.3967` | Proposition 2 is explicitly inherited. Each concrete utility still needs an adaptive-submodularity proof. |
| Exact transcript separation | elementary finite classification/testing support separation; Blackwell comparison is adjacent | Theorem 1 is useful as an interface theorem, but historical novelty is not established and should not be asserted. |

**Novelty disposition:** `CANNOT_CHECK_DISTINCT_THEOREM_NOVELTY`. The donor map is now stronger than the source packet's map, but this remains a targeted audit rather than a systematic full-text priority search. The combined vocabulary—support envelope + credal provenance + adaptive discriminator—may be a useful programme synthesis. That is not the same as a new mathematical theorem.

## Integration recommendation

### Safe to integrate after scope edits

- the support-envelope/conditioned-credal distinction;
- finite target-class transcript purity and the full-support-noise boundary;
- the finite risk-vector frontier as a **donor-derived common representation**;
- the explicit distinction between fixed ex-ante credal minimax and rectangular historywise ambiguity;
- the oriented pairwise information-cost obligation as a necessary, nonattainability-neutral bound; and
- N1--N8 plus A1--A3 as retained research identities.

### Do not integrate as written

- “new Bellman/frontier theorem,” “new adaptive KL bound,” or any broad superiority claim;
- state-dependent/destructive/no-repeat experiments without a state-indexed recurrence;
- a named worst-case prior when \(\Pi\) is nonclosed;
- an executable randomized scientific policy without protocol authorization;
- zero-cost or general-measurable/infinite-horizon extrapolations;
- empirical use of \(K_e\), posterior risks, or KL values without protected kernel validation.

### Best successor theorem targets

1. a state-indexed nonrectangular frontier with a necessary-and-sufficient dynamic-consistency/rectangularity characterization;
2. a composite-target, cost-weighted Chernoff allocation with matching achievability and lower bound;
3. exact credal-specific dominance/pruning or frontier-complexity results beyond alpha-vector enumeration; or
4. a joint world-and-kernel ambiguity theorem with finite-sample coverage under adaptive kernel estimation.

Until one of these survives a dedicated literature audit and adversarial proof review, the strongest honest status is **scientifically useful finite synthesis, not top-tier theorem novelty**.
