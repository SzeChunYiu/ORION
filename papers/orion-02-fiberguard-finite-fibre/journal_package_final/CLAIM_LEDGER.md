# ORION-02 claim ledger V3 — finite-fibre certifiability

**Canonical manuscript:** `MANUSCRIPT_V3.md`
**Closure date:** 2026-08-31
**Scientific authority delta during publication closure:** `BOUNDED_CORRECTION_ONLY__R24_PAIRED_FLAGS_RECONSTRUCTED__NO_POSITIVE_PROMOTION`
**Submission authority before merge and author filing:** `false`

This ledger is the fail-closed claim surface for the bounded paper. It preserves the theorem claims, every adverse or null application result used in the manuscript, and the corrections that prevent those results from being over-read. Historical result bytes and retractions remain authoritative at their original paths; this ledger does not rewrite them.

## A. Formal claim surface

| ID | Claim | Status | Exact boundary |
|---|---|---|---|
| V3-C1 | A deterministic point certificate constant on a finite fibre $F_z$ has worst-case error at least $D_\phi(z)/2$, and the midpoint of the extreme target values attains equality. | **PROVEN** | Finite fibre, scalar target, deterministic fibre-constant certificate. |
| V3-C2 | An interval of radius smaller than $D_\phi(z)/2$ cannot cover every target value on the fibre. | **PROVEN** | Same finite-fibre setting. |
| V3-C3 | Under the balanced distribution on a diameter-attaining endpoint pair, every narrower fibre-constant interval has conditional miscoverage at least one half. | **PROVEN** | Worst-case conditional witness, not a distributional claim about any observed corpus. |
| V3-C4 | An $\varepsilon$-valid fibre-constant point certificate exists if and only if $D_\phi(z)\leq 2\varepsilon$; the midpoint is constructive. | **PROVEN** | Finite fibre and given target values; no estimator is supplied. |
| V3-C5 | The minimum unconstrained refinement into parts of diameter at most $2\varepsilon$ is the left-to-right greedy interval-cover count on the sorted target values. | **PROVEN** | Arbitrary partitions of a finite fibre are allowed. |
| V3-C6 | For a declared separator family $\mathcal S$, an $\mathcal S$-measurable $\varepsilon$-valid refinement exists exactly when every $\mathcal S$-indistinguishable pair within an original fibre has target gap at most $2\varepsilon$. | **PROVEN** | The refinement retains the original fibre identity and may split it only by the declared joint separator signature; the theorem neither learns nor prices the family. |
| V3-C7 | Without refinement, maximum whole-fibre certifiable coverage is the target-population mass of fibres satisfying $D_\phi(z)\leq 2\varepsilon$. | **PROVEN** | Fibre masses are assumed given; acceptance cannot split a fibre. |
| V3-C8 | The floor checker found zero violations on 784 registered finite configurations and its planted controls fired. | **CHECKER CORROBORATION** | Finite implementation check only; proof remains the authority. |
| V3-C9 | The refinement checker found zero violations on 4,704 main configurations plus its separator enumeration, matched greedy counts to exhaustive partition minima, and fired planted controls. | **CHECKER CORROBORATION** | Finite implementation check only; proof remains the authority. |

## B. Preserved application and repair boundaries

| ID | Preserved record | Status | Release interpretation |
|---|---|---|---|
| V3-E1 | The outcome-exposed paired-route recovery had 0 feasible candidates among 99 frozen development candidates, changed no route decision, and ended `FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE`. | **R18 NULL; FORMER POSITIVE RETRACTED** | Corroborating null only. It grants no conditional, family-shift, production, external-independence, novelty, or journal authority. |
| V3-E2 | The exact joint-route repair ended `FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS`. The invalid diagonal shortcut changes one exact randomized minimax value from 35 to 70; identical learned and fallback marginal profile sets can have joint values 0 and 50 under different compatibility relations. | **R19 ANALYTIC SPECIFICATION REPAIR** | Correct joint compatibility and acquisition timing are required inputs. No paired ASlib experiment was executed; no transfer or production value follows. |
| V3-E3 | The initial certified-neighbourhood study ended `CERTIFICATE_INVALID` on both registered splits. On the official split, full-space and reduced-space coverage were 0.210 and 0.331, with held-out violation rates 0.169 and 0.182; family-disjoint coverage was zero. | **PRESERVED ADVERSE RESULT** | Limited action coverage was not a valid certificate. |
| V3-E4 | After the recorded conformal-neighbourhood implementation repair, both registered splits ended `VALID_WITHOUT_COVERAGE_OR_VALUE`; the marginal criterion was met at the primary tolerance only with zero held-out coverage and no decision-value improvement over the single-best fallback. | **CORRECTED OPERATIONAL NULL** | Validity without coverage or value does not create routed-case conditional validity, family-shift validity, deterministic fibre safety, production value, external independence, novelty, or journal authority. |
| V3-E5 | The held-out density-backoff study covered 32 of 44 datasets, below its frozen 0.95 gate. Its lexical control covered 39 of 44. The paired exact McNemar test gave $p=0.0923$ and the paired bootstrap interval included zero. | **R23 ADVERSE; PAIRED DIFFERENCE NOT ESTABLISHED** | The primary geometry missed its own gate. The higher control count is descriptive and is not evidence of a decisive paired difference. |
| V3-E6 | The held-out arm-conditional study covered 44 of 44 datasets but incurred 20 strict violations, ending `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`. | **R24 PRIMARY ADVERSE** | The certificate is invalid by its own frozen criterion. Full coverage does not rescue validity. |
| V3-E7 | The frozen R24 fold records serialize the geometry-selected arm and paired `violation_strict` flags under both policies. Reconstruction gives 20/44 geometry violations and 14/44 matched lexical-control violations, with `(both, geometry only, control only, neither)=(14,6,0,24)` and exact two-sided McNemar $p=0.03125$. | **R24 PAIRED COMPARATOR CORRECTION; BOTH ADVERSE** | The former comparator `CANNOT_CHECK` interpretation is retracted. Both arms fail the frozen 0.10 validity gate. Geometry superiority is unsupported; the bounded strict-endpoint result does not establish broad lexical superiority. |
| V3-E8 | On the 44 R24 held-out decisions, the available bound had Pearson correlation $r=-0.144$ with realised excess; a 20,000-permutation test gave $p=0.353$. | **SELECTOR DIAGNOSTIC; NO USEFUL SIGNAL ESTABLISHED** | The frozen sample did not establish a useful association. It does not prove zero population association. |
| V3-E9 | The application records did not directly measure target diameters of accepted empirical fibres. | **NOT ESTABLISHED** | It is forbidden to cite R18, the neighbourhood studies, R23, or R24 as empirical evidence that $D_\phi(z)>2\varepsilon$. |
| V3-E10 | In the BNSL study, the zero-cost `basic_extended` representation already induced 1,179 singleton fibres and attained the virtual-best action on all 1,179 corpus instances; adaptive and best-static robust excess were both zero. The raw positive-looking terminal arose because the material-value and equality predicates overlapped at zero. | **R20 CONSUMED NULL; RAW POSITIVE TERMINAL QUARANTINED** | The additive authority label is `C_R20_BNSL_ADAPTIVE_NULL__FREE_STATIC_REPRESENTATION_ALREADY_VBS`. It establishes neither unseen-instance generalization nor adaptive superiority, and the exposed lane may not be retuned. |
| V3-E11 | The prospectively frozen TSP-LION2015 executor stopped before any learned model, legal pair, route interval, test loss, or comparison because 21 required feature-cost cells had no numeric cost under the frozen grammar. | **`CANNOT_CHECK_TSP_DIRECT_RELATIVE_SOURCE_OR_RESOURCE`** | This is a subject-prerequisite `CANNOT_CHECK`, not a null, adverse, or positive mechanism result. It did not consume a round and cannot be repaired after observing the failure by dropping or imputing the cells. |
| V3-E12 | The untouched-subject CSP-MZN direct-relative/joint-route recovery ended `C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE`; the certified router increased mean total excess and timeouts relative to its registered same-information comparator. | **R21 ADVERSE; ROUND 2 CONSUMED** | A recorded cross-run exact-tie custody defect changed no decisions, losses, aggregates, or terminal and was later resolved additively on separate hosted runners. The predecessor `CANNOT_CHECK` receipt remains preserved; no external independence or positive authority follows. |
| V3-E13 | Before a Round-3 freeze existed, a recursive search exposed rows from a cached ASlib checkout. The conservative exposure boundary is the entire cached ASlib tree, which is disqualified as an untouched Round-3 source. | **`PRE_FREEZE_OUTCOME_EXPOSURE__ROUND_NOT_CONSUMED`** | No model, metric, interpretation, or science terminal was produced. The incident is a custody failure, not a null/adverse/positive result or `CANNOT_CHECK` adjudication; the round count remains 2/3. |

## C. Forbidden promotions and open authority

| ID | Proposed promotion | Status | What would be required |
|---|---|---|---|
| V3-X1 | Broad cross-domain or unseen-instance transfer. | **NOT CLAIMED / OPEN** | Fresh prospective evidence under a declared disjoint evaluation design. |
| V3-X2 | Production, deployment, or hardware/resource advantage. | **NOT CLAIMED / OPEN** | Separate operational evidence and a declared cost/resource model. |
| V3-X3 | Computational-hardness or universal statistical-estimation result. | **NOT CLAIMED / OPEN** | A separate theorem with the required complexity or statistical assumptions. |
| V3-X4 | Comparative superiority of the R23 geometry or either R24 arm. | **NOT ESTABLISHED / FORBIDDEN** | R23's paired difference was not established. R24 is reconstructable but adverse to geometry on the strict-violation endpoint, and both policies fail validity; broader superiority would require a prospective, prespecified comparison of valid certificates. |
| V3-X5 | External independence, external replication, final novelty priority, acceptance, or journal authority. | **OPEN** | Genuinely independent review/replication and the venue's editorial process. |
| V3-X6 | Earlier all-$t$ gadget formulas, their minimax corollaries, the conditional four-index compiler theorem, and single-block sharpness. | **SUPERSEDED FOR SUBMISSION** | The independent proof audit found undeclared cross-gadget, dominance, padding, integrality, and single-block assumptions. Historical records remain intact. |

## Stable proof-regression boundary aliases

The independent V3 checker binds three historical claim IDs in addition to V3-C1--C7. They remain stable aliases rather than being silently renumbered during publication editing.

| ID | Bound claim | Status | Current ledger binding |
|---|---|---|---|
| V3-C14 | The current empirical studies establish $D_\phi(z)>2\varepsilon$ on accepted empirical fibres. | **NOT ESTABLISHED / FORBIDDEN** | Same boundary as V3-E9. |
| V3-C15 | The theory establishes broad cross-domain transfer, production benefit, physical or hardware advantage, or computational hardness. | **NOT CLAIMED / FORBIDDEN** | Same boundary as V3-X1--V3-X3. |
| V3-C16 | The superseded all-$t$ gadget and compiler claims remain live submission claims. | **SUPERSEDED FOR SUBMISSION** | Same boundary as V3-X6; historical records remain intact. |

## Prior-work and novelty boundary

Comparison of experiments, sufficient-statistic theory, robust decision theory, interval covering, conformal prediction, and selective prediction are prior-work families. The paper does not claim invention of the midpoint of an interval or the greedy interval-cover primitive. Its bounded contribution is the unified fail-closed finite-fibre calculus linking exact deterministic certificate radius, the tolerance threshold, minimum abstract refinement, restricted-separator realizability, and whole-fibre abstention, together with the explicitly adverse application boundary. Final priority and significance remain review questions rather than repository-granted authority.

## Stop rule

The bounded theorem/adverse paper does not wait for a broader selector or transfer experiment. Any successor empirical promotion must be prospective, use disjoint train/calibration/test custody, and preserve the present nulls if it fails. No post-outcome change to tolerance, risk level, representation, separator vocabulary, selector threshold, or comparator can increase the authority of the frozen application studies.
