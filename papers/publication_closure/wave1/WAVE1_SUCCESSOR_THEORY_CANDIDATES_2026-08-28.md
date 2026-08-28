# Wave-1 successor theory candidates — 2026-08-28

**Status:** `HYPOTHESIS_ONLY__NO_SCIENTIFIC_AUTHORITY`  
**Protocol freeze:** `false`  
**Manuscript authority:** `NONE`  
**Submission authority:** `false`  
**Wave-1 filing rule:** `SUCCESSOR_SCIENCE_MUST_NOT_SILENTLY_BLOCK_A_SOUND_BOUNDED_SUBMISSION`

This note applies the same negative-to-theory discipline used for Wave 2 to the Wave-1 papers in issue #1609. It is not a manuscript rewrite, proof-complete result, protocol freeze, novelty claim, or reason to hold an already coherent bounded paper open.

The governing rule is

`adverse/CANNOT_CHECK -> mechanism diagnosis -> theorem-shaped successor -> strongest falsifier -> prospective proof/test`

not

`adverse/CANNOT_CHECK -> tune until positive`.

A second rule is specific to Wave 1:

> If the current bounded paper is already scientifically coherent, the successor theory is optional breadth. It becomes submission-blocking only if the manuscript chooses to retain the broader claim that the successor is meant to establish.

Several candidates below use generic information-sufficiency ideas. Those ideas are donor mathematics. In particular, comparison of experiments/sufficient information, latent-class identifiability, group invariance, set coverage, dependency closure, and common-mode validation are not ORION novelty claims. The possible ORION residual is the exact connection between those generic objects and the already-frozen ORION counterexamples.

---

## Executive disposition

| Paper | Disposition | Successor theory / action | Blocks bounded Wave-1 submission? |
|---|---|---|---|
| ORION-14 | `THEORY_RESPONSE_ALREADY_EXISTS` | V4 fibrewise attainability already explains saturation/non-discrimination | **No** |
| ORION-12 | `NEW_THEORY_CANDIDATE` | `ORION12.ROUTE_EXCLUSIVE_MASS_FRONTIER.v1` | No, unless external superiority is retained |
| ORION-13 | `NEW_THEORY_CANDIDATE` | `ORION13.MINIMAL_SEMANTIC_SEPARATOR.v1` | No |
| ORION-05 | `SHARP_CORE_ALREADY_EARNED` | do not manufacture a broader support claim; broader cone/classification belongs to sequel owners | **No** |
| ORION-09 | `NEW_THEORY_CANDIDATE` | `ORION09.REGIME_INFORMATION_COMPLEXITY.v1` | No |
| ORION-10 | `NEW_THEORY_CANDIDATE` | `ORION10.CERTIFICATE_EXPLANATION_GAP.v1` | No |
| ORION-06 | `NEW_THEORY_CANDIDATE` | `ORION06.CLAIM_PRESERVING_RECOVERY.v1` | No for the single-programme case study |
| ORION-07 | `NEW_EXACT_THEORY_CANDIDATE` | `ORION07.AGREEMENT_NONIDENTIFIABILITY.v1` | No for benchmark-definition paper |
| ORION-08 | `NEW_THEORY_CANDIDATE` | `ORION08.BINDING_SUFFICIENCY_LATTICE.v1` | No |
| ORION-16 | `NEW_ANALYTIC_GENERALIZATION` | `ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1` | No |
| ORION-17 | `THEORY_RESPONSE_ALREADY_EXISTS` | closure-carrying transform/composition theory already explains the old necessity failure | **No** |
| ORION-18 | `IDENTIFICATION_BOUNDARY` | `ORION18.COMMON_MODE_GOLD_NONIDENTIFIABILITY.v1` | No for bounded calculus; yes only for external-validity wording |
| ORION-19 | `NEW_THEORY_CANDIDATE` | `ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1` | No for current bounded causal-diagnosis claim |
| ORION-23 | `THEORY_RESPONSE_ALREADY_EXISTS` | responsibility-relative certificate transport already answers the historical self-scoring defect | **No** |

---

# Priority A — exact or near-exact theory from evidence already in the repository

## ORION-07 — Agreement non-identifiability

### Candidate ID

`ORION07.AGREEMENT_NONIDENTIFIABILITY.v1`

### Trigger

The current paper correctly says that two materially different instruments can agree prospectively while their agreement is not itself a correctness score. The evidence is currently too small for calibration/reliability claims, and the instruments share repository evidence, vocabulary, and receipt substrate, so statistical independence is not earned.

### Exact binary theorem candidate

Let `X,Y in {0,1}` be two instrument decisions and `T in {0,1}` the later truth. Let

`a = P(X=Y)`

be the observed agreement rate, and let

`q = (P(X=T)+P(Y=T))/2`

be the mean instrument accuracy.

On disagreement events `X!=Y`, exactly one binary instrument is correct. On agreement events, either both are correct or both are wrong. Therefore

`q = (1-a)/2 + P(X=Y=T)`.

Since `0 <= P(X=Y=T) <= a`, every compatible system obeys

`(1-a)/2 <= q <= (1+a)/2`.

Both bounds are attainable, and every value in the interval is attainable by varying the fraction of agreement events on which both instruments are correct.

In particular, if `a=1`, then

`0 <= q <= 1`.

Perfect agreement alone supplies **no nontrivial accuracy bound**.

### Meaning for ORION-07

This is the mathematical version of “agreement is pre-outcome data, not validation.” Architectural heterogeneity does not repair the identification problem unless it comes with defensible assumptions on the joint error process or later gold.

Classic no-gold latent-class methods obtain identification only after adding assumptions such as multiple populations with different prevalences and conditional independence. Those assumptions are donor methodology, not ORION novelty.

### Strongest falsifier / alternative explanation

The theorem itself is exact under the binary setup. What can fail is its relevance to the final benchmark if the scientific decision alphabet is not binary or if a separately justified error model supplies additional identifying assumptions.

The strongest competing route is therefore not “more agreement”; it is a predeclared model with independently defensible assumptions, or deferred gold.

### Minimum decisive successor

The registered prospective series should:

1. freeze each frontier item and both instrument decisions before outcome access;
2. record agreement separately from deferred correctness;
3. obtain at least the preregistered item count with later scientific outcomes;
4. report each instrument's calibration/reliability and the conditional value of agreement;
5. never count retrospective typed reconstructions as new prospective items.

The current benchmark-definition/systems paper need not wait for this series.

---

## ORION-13 — Minimal semantic separator theorem

### Candidate ID

`ORION13.MINIMAL_SEMANTIC_SEPARATOR.v1`

### Trigger

The current structured-projection result has zero false merges on the frozen disjoint public-reference set, while flat predicate canonicalization false-merges. The paper deliberately does not claim universal necessity of every semantic coordinate.

### Theorem candidate

Let each candidate merge pair have semantic coordinate vector

`c(x) = (referent, construct, measurement, context, modality, attribution, ...)`

and gold merge verdict `M(x)`.

For a coordinate subset `S`, let `pi_S(c)` be the projection to `S`.

**Sufficiency.** `S` is merge-sufficient on a domain iff `M` is constant on every positive-mass/protected fibre of `pi_S`.

**Coordinate necessity.** A coordinate `j in S` is necessary relative to `S` if there exist two admissible pairs `x,x'` such that

`pi_{S\{j}}(c(x)) = pi_{S\{j}}(c(x'))`

but

`M(x) != M(x')`.

Such a pair is a minimal collision witness: any merge rule that omits `j` must assign the same representation to two cases requiring different verdicts.

A minimum sufficient semantic basis is therefore a minimum hitting/separating set over all opposite-verdict collision pairs.

### Why this is better than “all typed coordinates matter”

It permits the science to simplify. If one coordinate is redundant on the actual protected domain, remove the universal-necessity language rather than defending it. If each coordinate has a collision witness, minimality is earned exactly on that domain.

### Strongest falsifier

A smaller coordinate subset that remains fibre-pure on the protected set and an independently frozen challenge set falsifies necessity of the removed coordinates.

### Minimum decisive proof/test

Use the existing structured public-reference cases to compute all opposite-verdict collision pairs, solve the exact minimum-separator problem, and then freeze a challenge set constructed without looking at candidate-subset errors. No raw-text extraction is required.

This is optional theory breadth; it does not block the already scoped structured-mapping submission.

---

## ORION-09 — Regime information complexity

### Candidate ID

`ORION09.REGIME_INFORMATION_COMPLEXITY.v1`

### Trigger

SixLCU admits an exact low-order boundary, but StabPrep refutes the universal `boundary-is-low-order` motif. Under the frozen StabPrep natural feature vocabulary, mixed feature cells create an exact irreducible error floor of `43/1146`.

### General finite theorem

For finite cases with binary regime label `Y` and feature map `phi`, group cases into feature fibres `F_z`.

Any deterministic classifier using only `phi` must assign one label per fibre. Its minimum possible empirical error is therefore

`E*(phi) = (1/N) * sum_z min(n_z^0, n_z^1)`,

where `n_z^y` is the number of protected cases in fibre `z` with label `y`.

Hence:

- exact classification is possible iff every fibre is label-pure;
- a feature extension can improve the optimum only by splitting mixed fibres;
- no optimizer/model class can beat `E*(phi)` without additional information.

This is a generic information-sufficiency fact, not ORION novelty.

### ORION-specific successor object

Define the **regime separator complexity** of a compiler family relative to a prospectively frozen semantic feature library as the minimum feature cost/order needed to make every target fibre pure.

SixLCU supplies a low-complexity control. StabPrep supplies a nonzero lower bound for the current vocabulary.

### Strongest falsifier

If an already-frozen feature was omitted or encoded incorrectly and independent reconstruction makes all StabPrep fibres pure, the current “irreducible vocabulary floor” interpretation is wrong.

### Minimum decisive successor

1. independently recompute the `43/1146` minority-mass floor;
2. freeze a semantics-derived extension library before testing its labels;
3. measure the minimum separator cost/order, not merely the accuracy of one learned classifier;
4. retain a nonzero lower bound if no frozen extension purifies the fibres.

This turns the StabPrep negative into a complexity question instead of another formula search.

---

## ORION-10 — Certificate complexity versus explanation complexity

### Candidate ID

`ORION10.CERTIFICATE_EXPLANATION_GAP.v1`

### Trigger

`F2(t)=C_Dxx(t)` is theorem-backed exact for the frozen R6M unit objective, while compact regime explanations were successively refuted, including 64 exact hybrid witnesses against `B'`. The cost certificate survives the explanation failure.

### Candidate theorem structure

Separate two representations:

- `C(x)`: information used by the exact cost certificate;
- `Psi(x)`: a frozen human-readable explanation vocabulary/regime language.

An exact cost certificate can exist whenever the exact cost `f(x)` is recoverable from `C(x)`.

A `Psi`-only explanation of a target `R(x)` can be exact only if `R` is constant on every `Psi` fibre. If two instances share `Psi(x)` but require different exact regime explanations or different explanation-relevant structural decompositions, no formula that factors only through `Psi` can be exact.

Thus one may have

`certificate exactness = 1`

while

`explanation-language exactness < 1`.

### What is not proved yet

The existing 64 hybrid witnesses refute one enlarged formula `B'`; they do not automatically prove a lower bound for every reasonable compact explanation language.

### Strongest falsifier

An exact formula inside the prospectively frozen explanation class that covers every protected hybrid witness falsifies the proposed explanation gap for that class.

### Minimum decisive successor

Freeze the explanation grammar first: allowed primitive predicates, operators, interaction order, and expression-size budget. Then either:

- construct two same-`Psi` cases with different exact explanation targets, proving an information lower bound; or
- synthesize an exact formula inside the frozen grammar.

Either outcome is scientifically useful. Do not change the grammar after reading which hybrid rows it misses.

---

## ORION-16 — Dependency-closed selective revalidation

### Candidate ID

`ORION16.DEPENDENCY_CLOSED_REVALIDATION.v1`

### Trigger

The current bounded certificate-lifting semantics has five registered scientific lift coordinates, minimal one-coordinate separations, full revalidation successes, and proper-subset failures. Universal minimality of those exact five coordinates is not claimed.

### Analytic generalization candidate

Let scientific standing depend on bridge obligations `b_i` connected by a directed dependency graph `D`. Let `Delta` be the set of coordinates directly changed by a scientific update.

Define the affected closure

`A(Delta) = {j : j=Delta or some dependency path from a changed coordinate reaches j}`.

Assume:

1. donor-native certificates remain valid when their native premises do not change;
2. bridge obligations outside `A(Delta)` are stable under the update;
3. every declared dependency has a separation witness showing that its violation can alter scientific standing.

Then the candidate theorem is:

- revalidating all obligations in `A(Delta)` is sufficient for the lift;
- any sound universal revalidation set must contain `A(Delta)` under the separation-witness assumption.

So the minimal sound revalidation object is a dependency closure, not “recheck everything” and not an arbitrary fixed list of coordinates.

### Strongest falsifier

A case where all obligations in the declared affected closure revalidate but scientific standing is still wrong demonstrates a missing coordinate or missing dependency edge.

### Minimum decisive proof/test

Generalize the current five-coordinate enumerator to arbitrary finite dependency DAGs, prove the sufficiency/necessity directions, and use the existing 25 one-coordinate separations as bounded witnesses rather than as the all-size proof.

This is optional analytical strengthening; ORION-16's current bounded submission should not wait for it.

---

## ORION-19 — Invariant and margin-separated causal diagnosis

### Candidate ID

`ORION19.INVARIANT_MARGIN_DIAGNOSIS.v1`

### Trigger

Two current adverse boundaries have the same logical shape:

1. a semantics-preserving symbol reminting broke the historical serialized representation margin, proving format-prior sensitivity;
2. one held-out accessibility threshold does not transport and remains `CANNOT_CHECK`.

The successor invariant-profile representation repairs the first bounded mechanism, but the frozen defeat remains authoritative.

### Part A — semantic-orbit invariance

Let a group/set of registered transformations `G` preserve the scientific semantics and gold label. A representation claim intended to be semantic should be evaluated on the orbit

`{g.x : g in G}`.

If representation `phi` is invariant (`phi(g.x)=phi(x)`) and the downstream decision rule is deterministic, the final decision is invariant on that orbit.

Conversely, if a claimed mechanism changes decisions under a registered semantics-preserving transformation, the observed margin contains representation/format prior and cannot by itself establish semantic superiority.

The existing reminting attack is exactly such a falsifier; the invariant-profile successor is a bounded constructive response.

### Part B — threshold transport robustness

Let a diagnostic score under transfer have a predeclared uncertainty/drift set `I(x)` and a threshold `tau`.

A positive/negative threshold terminal is robust only if `I(x)` lies wholly on one side of `tau`.

If

`inf I(x) < tau <= sup I(x)`

(or the symmetric boundary convention), then admissible transfer uncertainty changes the decision and the scientifically correct terminal is `CANNOT_CHECK` unless more information is collected.

Post-outcome widening of `I` or movement of `tau` cannot create authority.

### Strongest falsifiers

- an independently frozen semantics-preserving orbit on which the invariant-profile successor changes decisions;
- a predeclared transport interval wholly separated from the threshold where the registered diagnosis still fails.

### Minimum decisive successor

Build one common protocol that freezes:

- semantics-preserving transformation families;
- orbit-invariance endpoints;
- threshold and uncertainty construction;
- exact resource accounting;
- independent checker.

The current bounded causal-diagnosis paper does not need a broader LLM/agent claim to submit.

---

# Priority B — theory that guides the next prospective experiment

## ORION-12 — Route-exclusive relevant mass and the recall/cost frontier

### Candidate ID

`ORION12.ROUTE_EXCLUSIVE_MASS_FRONTIER.v1`

### Trigger

On the matched TREC-COVID study, the multi-route arm improves `nDCG@10` by `+0.1488` but does not earn the registered discovery-superiority gate: recall@100 difference is `-0.0177` with interval crossing the `-0.02` noninferiority margin, and reads increase by `+175.7%` instead of falling by the required amount. Two of five routes are unavailable and remain `CANNOT_CHECK`, not zero-yield routes.

### Counting theorem

Let `G` be the relevant-document gold set for a topic. Let baseline reachable set be `B`, and let the extra route family make documents in `U` reachable.

Define the **exclusive relevant mass**

`E = G intersect (U \ B)`.

No policy whose only additional information comes from `U` can improve recall over the baseline by more than

`|E| / |G|`.

This upper bound is algorithm-independent: documents already reachable through `B` cannot create additional recall merely by being rediscovered through another route.

Now define a route-exclusive yield curve `L(m)` = minimum number of additional reads required to recover `m` members of `E` under a frozen route/stopping policy class. Any simultaneous recall-and-read improvement must satisfy both the required recall gain and the read budget through some feasible `m`.

### Interpretation

Route diversity is valuable for recall only through **exclusive relevant mass**, not through route labels or provider count. A route may improve top-ranked ordering quality while adding too little exclusive tail relevance per read to improve recall efficiency.

The current nDCG/recall split is consistent with this theory, but does not prove it.

Unavailable CITATION/RESTRICTED routes have unknown `E`; their mass remains `CANNOT_CHECK`.

### Strongest falsifier

If the already available extra routes contain enough low-cost exclusive relevant mass to satisfy the frozen recall/cost gate, then the failure is attributable to the routing/stopping policy rather than an acquisition ceiling.

### Minimum decisive successor

Before another expensive external campaign:

1. compute per-route exclusive relevant-yield curves on the frozen TREC topics;
2. separate duplicate/reordered relevant documents from genuinely exclusive relevant mass;
3. calculate the best possible recall/read frontier under the frozen accessible routes;
4. if the gate is feasible, prospectively test a policy designed to approach that frontier;
5. if infeasible, state the acquisition ceiling and stop tuning the router.

This theory is optional if the paper retains only its current bounded methods/system-design claim.

---

## ORION-06 — Claim-preserving recovery and minimal causal repair

### Candidate ID

`ORION06.CLAIM_PRESERVING_RECOVERY.v1`

### Trigger

The recorded-negative revival now classifies seven historical negatives into `IMPROVED`, `CORRECT_SUBTRACTION`, and `RETAINED_NEGATIVE`, while the cross-domain comparative study remains `CANNOT_CHECK`. Several rows demonstrate that changing the evaluation object, resource projection, method language, or donor family can change the apparent result.

### Formal recovery identity

Represent a scientific test by

`P = (target T, domain D, comparator set C, metric M, admissible resources R, protocol chronology H)`.

A successor counts as a **repair of the original negative** only if the load-bearing components of `P` remain equivalent under transformations frozen before outcome access.

If `T`, `M`, `D`, or the comparator authority changes materially, the successor may be scientifically useful but it is a **claim substitution**, not a positive replay of the old claim.

### Minimal causal intervention theorem candidate

Let the terminal be a conjunction of stage predicates on a causal/dependency DAG. If failed predicate `p_s` is invariant under every intervention strictly downstream of stage `s`, then no downstream-only intervention can repair the terminal while preserving protocol identity.

Any claim-preserving repair set must hit an ancestor/control coordinate capable of changing each failed predicate. The smallest such intervention is a minimum hitting set over the violated predicates' admissible causal ancestors.

### What this would add

It would turn the current recovery doctrine into a falsifiable optimization object:

- target the minimal causal repair;
- measure repair cost;
- separately count false revivals caused by claim substitution;
- retain donor-absorbed and genuinely unsolved negatives.

### Strongest falsifier

In a prospective matched study, naive iteration or donor-stop performs as well as mechanism-targeted minimal repair on claim-preserving recovery rate, cost, and false-revival rate.

### Minimum decisive successor

Run the already frozen cross-domain comparison on at least the named non-quantum formal and computational/empirical programmes with matched workflow budgets and independent scoring. Freeze failure-stage diagnosis and admissible intervention sets before seeing recovery outcomes.

The single-programme case-study paper can submit without this general-method claim.

---

## ORION-08 — Binding sufficiency lattice

### Candidate ID

`ORION08.BINDING_SUFFICIENCY_LATTICE.v1`

### Trigger

The six exact-synthetic studies contain both value and no-value regimes; the N4-B scoped-vs-never interval crosses zero. The current paper correctly avoids claiming that more typed/scoped state always helps.

### Shared information theorem

Let binding `B(x)` partition world states into fibres, and let `A*(x)` be the set of optimal scientific decisions in world `x`.

A deterministic zero-regret policy using only `B` exists iff every binding fibre has a common optimal action:

`intersection_{x:B(x)=z} A*(x) != empty`

for every reachable `z`.

A refinement `B'` of `B` cannot worsen Bayes-optimal decision risk because every `B`-policy can be implemented after observing the richer binding. The refinement has strict decision value only when it separates a positive-mass `B` fibre whose worlds do not share an optimal action and the split permits better decisions.

This is generic decision-sufficiency/Blackwell-style donor theory. It should be implemented once across the programme rather than claimed independently by ORION-08 and ORION-22.

### ORION-specific use

Use the six frozen studies to classify each typed binding by:

- ambiguity removed;
- action disagreement removed;
- no-value refinement;
- donor-absorbed refinement.

The null N4-B regime is then a predicted no-value case, not an embarrassment to average away.

### Strongest falsifier

A binding refinement predicted to purify action fibres but showing no improvement under exact matched-information scoring indicates that the identified ambiguity was not decision-relevant or the action model is incomplete.

### Minimum decisive successor

Reanalyse existing exact-synthetic worlds at the fibre/action-set level. Only run the frozen real-domain transfer if the final manuscript wants a real-agent/scientific-discovery generalization claim.

---

## ORION-18 — Common-mode gold non-identifiability

### Candidate ID

`ORION18.COMMON_MODE_GOLD_NONIDENTIFIABILITY.v1`

### Trigger

ORION-18 has a strong internal formal calculus and 20 same-programme real-domain conformance cases, but correctly states that same-programme gold cannot establish independent external scientific adjudication.

### Identification theorem

Let a system decision `A(x)` and internal gold `G(x)` both be generated under a shared latent specification/ontology `S`.

Observing

`A(x)=G(x)`

for every tested `x` does not identify either with an external truth `T(x)`.

For any agreement-perfect dataset and any chosen subset `K` of cases, define an alternative truth process

`T'(x) != A(x)` for `x in K`,

while keeping `A` and `G` unchanged. The observed internal agreement is identical under `T` and `T'`.

Therefore internal agreement, deterministic replay, and an independent implementation of the **same specification** cannot by themselves identify external scientific correctness.

This is common-mode validation logic, not ORION novelty.

### Consequence

The external-adjudication blocker is not something more internal CI can “fix.” The missing variable is an evidence source whose scientific judgment is not derived solely from the same programme specification.

### Strongest alternative / discharge condition

Externally governed gold, or a separately justified objective verifier whose premises do not inherit the disputed scientific ontology, can add the missing identifying information.

### Minimum decisive successor

Keep the bounded calculus submission separate. If broader empirical validity is desired, prospectively freeze cases and collect independently governed adjudication or a real integrated authorization/evidence donor with matched information. Internal replay can remain a reproducibility check but not the external-validity endpoint.

---

# Existing theory responses — do not create new blockers

## ORION-14 — saturation already has a theory

The V4 manuscript already gives the right response to the historical saturated H3 axis: zero terminal error is attainable exactly when the target is constant on positive-mass representation fibres and the target is expressible in the output alphabet. It also records that an information-equivalent fully typed donor product ties ORION-14 exactly.

That is already the theory answer. The historical V2 H3 null/non-discrimination should remain visible; it does not require another revival theory.

**Do next:** finish the current TMLR submission lane. The prospective naturalistic/external panel is optional breadth unless the paper chooses to claim deployed/external generality.

---

## ORION-05 — sharp `kappa=2` is already the scientific object

The frozen R6M grammar already has an all-`n` support-`<=2` theorem and an exact support-one counterexample, so `kappa_R6M=2` is sharp.

Do not invent support-three necessity merely to make the story “bigger.” Broader objective-cone and cross-grammar classification work already has ownership elsewhere in the QG/regime-geometry programme and must not be back-ported as ORION-05 novelty.

**Do next:** independent proof/novelty audit and journal package. Any broader support theorem is optional successor science with explicit ownership.

---

## ORION-17 — closure-carrying theory already answers the old necessity failure

The current paper already moved past the older `MATCH_IS_NOT_NECESSARY`-type reading. It has closure-carrying transforms, exact bridge-binding composition logic, countermodels for bridge mismatch, and three real change classes where witness-aware transport succeeds while value-only/always-reopen controls fail in different ways.

A possible future analytical generalization is arbitrary finite-chain composition by induction, but that is not needed to make the current bounded paper coherent.

**Do next:** package the earned bounded closure-transport paper. Do not turn “universal transport” into a new mandatory experiment.

---

## ORION-23 — responsibility-relative transport already answers the historical self-scoring defect

P13A's self-scored zero-harm endpoint is permanently withheld. The later paper does not attempt to rehabilitate it: it moves to certificate-independent gold, real responsibility shift, verifier-backed semantic/epoch shift, donor-complete provenance controls, and a drift-bounded transport rule.

The current scientific object already states the right theory:

> validity/reuse is responsibility-relative, not provenance-relative.

A more abstract proof-dependency transport theorem could be a sequel, but it should not block the present cross-domain submission.

**Do next:** manuscript/package closure and only add new science if broader arbitrary-semantic-drift or real-agent claims are retained.

---

# Cross-paper theorem spine

Several Wave-1 negatives are different manifestations of the same generic information principle:

1. **Feature/binding sufficiency:** a decision can be exact only when the available representation does not merge states requiring incompatible decisions.
2. **Explanation sufficiency:** an exact numerical certificate may exist even when a restricted explanatory vocabulary merges structurally different cases.
3. **Agreement insufficiency:** agreement between instruments does not identify correctness without additional assumptions or deferred truth.
4. **Route sufficiency:** extra routes improve recall only through genuinely exclusive relevant mass, not through route count itself.
5. **Validation independence:** internal agreement under a shared specification does not identify external scientific truth.

This cross-paper spine is a research coordination device, not a novelty claim. Classic comparison-of-experiments/sufficient-information theory and latent-class/no-gold diagnostic-test theory are obvious donor areas and must be subtracted in any future manuscript treatment.

---

# Recommended execution order

## Cheapest exact theory first

1. **ORION-07** — write and independently check the sharp agreement/mean-accuracy bounds.
2. **ORION-13** — compute the exact minimum semantic separator basis on existing protected structured cases.
3. **ORION-09** — independently recompute fibre minority mass and define separator complexity.
4. **ORION-16** — generalize selective revalidation to dependency closure.
5. **ORION-19** — bind semantic transformation groups and predeclared threshold-transport uncertainty.
6. **ORION-10** — freeze an explanation grammar and test whether hybrid witnesses create a true information lower bound.

## Then empirical-successor gates only where worth the scope

7. **ORION-12** — measure exclusive-relevant-mass/read frontier before another external discovery campaign.
8. **ORION-08** — reanalyse existing exact-synthetic worlds through binding/action fibres; execute real transfer only for a broader headline.
9. **ORION-06** — run cross-domain claim-preserving recovery only for a general-method claim.
10. **ORION-18** — external adjudication cannot be replaced by more same-programme tests; collect it only if external-validity wording is retained.

## Submit rather than expand

- ORION-14
- ORION-05
- ORION-17
- ORION-23

These already have the scientific theory needed for their bounded paper. Their remaining work should primarily be hostile review, canonicalization, rendering, byte binding, venue fit, and filing.

---

# Authority boundary

Nothing in this note changes a result, negative, null, `CANNOT_CHECK`, claim ledger, manuscript, or submission terminal.

`scientific_authority_delta = NONE`

A theorem candidate becomes scientific authority only after an independent proof audit; an empirical candidate becomes authority only after a separately frozen prospective protocol and valid execution. Historical adverse evidence is never overwritten by a successor.
