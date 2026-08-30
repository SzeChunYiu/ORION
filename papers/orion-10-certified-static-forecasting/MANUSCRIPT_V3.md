# Certified Static Forecasting for Quantum Compilation: What Survives a Counterexample?

**ORION-10 Manuscript V3 — donor-synchronized publication draft**  
Scientific cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER.md`, `PUBLICATION_FOUNDATION_V2.md`  
Certificate/reporting contract: `FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md`

## Abstract

Static quantum-cost analysis and resource estimation are established research areas; the contribution here is not the generic idea of predicting cost without running a full compiler. We study a narrower question in a frozen shared-Tag TARE compilation family with an unrestricted exact dynamic-programming referee: **when a static forecaster mixes proved bounds, theorem-backed exactness, finite-domain equalities and unverified predictions, which authority survives an exact counterexample?** The initial forecaster evaluates three explicit feasible subfamilies and never calls the unrestricted DP. On 9,546 registered DP-compared instances it matches exact truth on 9,545 and fails on exactly one prospectively generated `n=3` row, where the true optimum is 10 and all three closed-form terms return 11. The single mismatch is logically decisive for universal closed-form exactness, so we do not headline a 99.99% accuracy rate. Two stronger certificate layers survive: `10<=11` preserves the constructive upper bound, and an independent all-`n` theorem still places the exact optimum inside the full support-two family. The exact witness localizes the failed layer to an omitted out-of-own-target-support borrow. A separately frozen successor admits that configuration; in parallel, the theorem-backed static forecaster `F2=C_D++` computes the exact support-two family minimum without the unrestricted DP. Later companion counterexamples refine the smaller named-family taxonomy again without affecting `F2`'s theorem authority. A further vocabulary-level theorem sharpens the explanatory boundary: a vocabulary that must explain **every** possible cost function exactly can do so only if it induces the discrete partition of the abstract state space. This universal result does not settle the named practical vocabulary `B′`, because the available 64 rows were selected as gap witnesses and 676 of 740 evaluated instances were not serialized; the scoped fibre-constancy question therefore remains `CANNOT_CHECK`. We formalize the surviving distinctions as a **ForecastCertificate** reporting schema rather than as a new general static-analysis formalism. The result is a refutation/localization/repair study showing why feasible upper bounds, theorem-backed exact family minima, finite closed-form hypotheses, explanation vocabularies and forecast-only rows must remain different scientific objects.

## 1. Introduction

Quantum resource estimation already spans several mature approaches. Qualtran expresses and analyzes compositional algorithm resource requirements. Qet applies automated expected-cost analysis to mixed classical-quantum programs using expectation-transformer semantics. Compilation-driven estimators propagate circuits through architecture/error-correction assumptions. Other verified or cost-aware compiler systems combine semantic correctness with explicit resource objectives. ORION-10 therefore does **not** claim novelty for static quantum cost analysis, resource upper bounds, or forecasting without full execution.

The paper asks a different question: **what kind of statement is the forecast?**

A fast cost number may be:

- a value of an explicit feasible construction and therefore a certified upper bound;
- exact because a theorem proves the searched family is complete;
- exact only on a registered finite benchmark;
- a conjectural closed form extrapolated beyond that benchmark;
- or a prediction for which no exact receipt exists.

Those categories behave differently under refutation. If they are collapsed into one “accuracy” metric, a single counterexample is either dismissed as a tiny error rate or treated as if every underlying guarantee failed. Neither is correct.

We study the distinction in an exact compiler family. The frozen R6M shared-Tag TARE grammar has an unrestricted exact DP referee and a theorem-backed support-two family `D++`. An initial cheap forecaster uses three simpler feasible subfamilies. Its empirical story initially looks excellent; its universal closed-form story is false. Because the authority layers were recorded separately, the counterexample tells us exactly what to repair and what not to repair.

The scientific sequence is:

`feasible static bound -> finite closed-form success -> prospective exact counterexample -> authority localization -> separately frozen mechanism repair -> theorem-backed exact family forecaster -> explanation-vocabulary lower bound`.

The main result is not predictive dominance over current quantum cost-analysis tools. It is a **compiler-specific case study in authority-layered forecasting and falsification**, including a theorem-level separation between exact prediction and universally compact explanation.

## 2. Setting: exact truth and restricted forecast families

### 2.1 Frozen compiler family

We use the R6M three-block shared-one-bit-Tag TARE analysis grammar under the registered raw support-count objective. Six Pauli targets are grouped into three two-target blocks. Each block chooses an anticommuting frame pair, target assignment and central branch; a shared Tag imposes common labels; Restore strings map frame representatives to targets.

The unrestricted optimum `C_DP` is computed by a proof-carrying exact dynamic program. This structural objective is not a full hardware-resource model and is not directly comparable to physical qubit/runtime/T-count estimates without an additional mapping.

### 2.2 Feasible named subfamilies

The original fast forecaster uses:

- `R6L`: registered common-anchor/weight-one donor family;
- `D+`: weight-one frames with arbitrary anchors and minimum compatible spread Tag;
- `B`: a compact frame-for-Tag borrow family.

Each family contains only valid compiler configurations, so every family minimum is an upper bound on `C_DP`.

A fourth family is conceptually different:

- `D++`: the **full frame-support-≤2 family**.

R6S proves `C_DP=C_D++` for every `n` in the frozen R6M/raw-support setting. Thus `D++` is theorem-sufficient, not merely a heuristic search space.

## 3. ForecastCertificate: reporting authority, not a new general analyzer

We represent a forecast row by a reporting object with logically distinct fields:

```text
ForecastCertificate {
  forecast_value,
  construction_or_family,
  upper_bound_status,
  exactness_authority,
  support/search_authority,
  regime_label_authority,
  exact_referee_status,
  verification_scope,
  source_receipts
}
```

The schema is a manuscript/reproducibility contract. It does not claim invention of static program analysis.

### 3.1 Constructive upper-bound layer

The initial forecaster

`F(t)=min(C_R6L(t), C_Dplus(t), f_B(t))`

returns the cost of a feasible member of the frozen grammar. Therefore

`C_DP <= F(t)`

is constructively valid regardless of whether equality holds.

### 3.2 Theorem-backed support/exact-family layer

R6S proves

`C_DP=C_Dxx`

all `n` for the frozen grammar/objective. Hence a static computation of the exact `D++` family minimum is an exact optimum computation by theorem, even if it avoids the unrestricted DP implementation.

### 3.3 Finite/conjectural closed-form layer

Before the later hostile row, the simpler identity

`C_DP = min(C_R6L, C_Dplus, f_B)`

held on the registered R6Q panels. Its authority was finite-domain evidence. It was never the same kind of claim as the support-two theorem.

### 3.4 Forecast-only layer

Some library rows can be scored statically without an exact committed referee result. Those rows are predictions only and must never enter verification denominators.

## 4. Registered benchmark: one error among 9,546 comparisons

The initial QG5 benchmark contains 9,546 exact DP comparisons across the registered structured, receipt-bound chemistry and fresh seeded panels. The forecaster matches exact truth on 9,545 and differs on one row.

This is a deterministic benchmark statement, not an IID population estimate. The exhaustive structured `n=2` slice contains 9,261/9,261 exact forecasts. The fresh seeded `n=2–3` panel contains 239/240 exact forecasts.

The correct headline is not “99.99% accurate.” A universal equality is defeated by one valid exact counterexample regardless of its frequency.

## 5. The decisive prospective counterexample

The refuting instance is in the fresh seeded panel (`seed=20260826`, `n=3`, index 7). The frozen target pairs are stored verbatim in the receipt.

The unrestricted exact referee returns

`C_DP = 10`.

Every term in the original closed-form forecaster returns 11:

`C_R6L = C_Dplus = f_B = 11`.

Therefore

`C_DP=10 < 11=F`.

### 5.1 Failed authority

The closed-form equality fails on this instance. The associated finite-domain regime predicate also becomes a false positive when extrapolated to the row.

### 5.2 Surviving authority

The feasible-bound layer remains true:

`10 <= 11`.

The theorem layer also remains true: an exact support-two configuration has cost 10, so

`C_DP=C_Dxx=10`.

The failure therefore lies **inside the theorem-backed support-two universe**. It refutes the compact subfamily decomposition, not the support theorem or the feasibility of the static forecasted construction.

## 6. Witness localization: omitted borrow support

The exact support-two witness reveals why the simple borrow family failed. One phantom support-two frame uses a borrow home outside that block's own target support, a configuration disallowed by the frozen `B` definition.

This is an exact structural diagnosis: the witness can be checked against the family predicate and the cost function. No statistical model is needed to identify the missing degree of freedom.

The diagnosis licenses a successor question but does not retroactively edit `B`.

## 7. Separately frozen repair and theorem-backed forecaster

QG5b freezes `B′`, enlarging the borrow-home domain only after the failure is known. The original refuting instance remains in the new receipt and now satisfies `f_Bprime=10`.

The successor separates two forecasting objects.

### 7.1 Compact B′ closed form

`min(C_R6L, C_Dplus, f_Bprime)`

is interpretable and exact on the registered QG5b finite panels. Its all-`n` completeness is not proved.

### 7.2 Exact static family forecaster

`F2(t)=C_Dxx(t)`

computes the minimum over the theorem-sufficient support-two family. Because R6S supplies the family-completeness theorem, `F2` exactness does not depend on observing zero benchmark error.

The benchmark remains useful as an implementation consistency check and as a source of explicit witnesses, not as the theorem's logical basis.

## 8. Later closed-form refutation is not a theorem refutation

QG7 later finds 64 exact instances with

`C_Dxx < min(C_Dplus, f_Bprime)`.

A separately frozen B″ family repairs those registered finite witnesses. This later result reinforces the authority hierarchy:

- the full `D++` support-two family remains exact all `n` by theorem;
- smaller named explanatory families remain refutable until their completeness is separately proved.

ORION-10 does not need the detailed fourth-regime classification; that belongs to ORION-09. Here it functions as a second falsification test of the same scientific discipline.

## 9. Universal exact explanation requires the discrete partition

The later vocabulary-minimality analysis asks a stronger question than whether one named compact family happens to predict the registered costs. Let a vocabulary `Psi` induce a partition of the abstract state space into fibres. A `Psi`-only exact explanation exists for a given cost function exactly when the cost is constant on every fibre.

The universal quantifier changes the problem. If one fibre contains two distinct states, choose a cost function that assigns them different costs; no `Psi`-only explanation can then be exact. Therefore a vocabulary that is exact for **every possible cost function** must separate every state from every other state: its partition is discrete. Conversely, the discrete partition is sufficient. Universal exact explanation therefore has no nontrivial coarse vocabulary.

The enumeration for `n=2..6` independently recovers the Bell-number partition counts `2, 5, 15, 52, 203`, and every coarsening is accompanied by a witness pair. A separate brute-force cost-function route agrees with the constructive witness test throughout that finite regression. These checks corroborate the implementation; the all-size result follows from the witness construction rather than from finite enumeration.

This theorem does **not** settle the named `B′` vocabulary on the real evaluated instance space. The 64 serialized QG7 rows are selected precisely because they satisfy a gap criterion. Among 740 evaluated instances, the other 676 per-instance `B′`/cost values were not serialized. Observed fibre constancy on the 64 selected witnesses would therefore be selection-conditioned and cannot establish global sufficiency or insufficiency. The scoped `B′` fibre-constancy question remains `CANNOT_CHECK` until all evaluated rows are emitted or a separately frozen replacement study supplies an unselected test.

The combined lesson is stronger than either result alone: exact cost prediction can be theorem-backed while compact mechanistic explanation remains refutable, and universal explanatory compression is impossible without restricting the cost family.

## 10. Forecast-only rows and external subjects

A static forecaster can return a number for a public library subject even when exact truth has not been computed. We preserve statuses such as:

- `DP_RECEIPT_COMMITTED__FORECAST_BOUND`;
- `UNVERIFIED_FORECAST__NO_DP_RECEIPT`.

Only the former contributes to verified comparison counts.

When discussing chemistry transfer, the **subject** is the relevant external scientific case; 15 within-subject matchings are dependent combinatorial views, not 15 independent Hamiltonian systems.

## 11. Relation to current static quantum cost analysis

ORION-10 is adjacent to but narrower than current static-analysis/resource-estimation work.

- **Qualtran** provides compositional quantum-algorithm resource analysis.
- **Qet** automates expected-cost analysis for mixed classical-quantum programs using expectation-transformer semantics and can produce certified upper bounds without repeatedly compiling a full low-level workflow.
- compilation-driven estimators and hardware-aware tools map programs/circuits to logical or physical resource assumptions.

ORION-10 therefore gives zero novelty credit to “static quantum cost analysis,” “certified upper bounds” or “resource prediction without full compilation” as generic ideas.

Its residual is the exact **authority decomposition and refutation behavior** inside one compiler family:

- a feasible upper bound can survive;
- an all-`n` family theorem can survive;
- a compact equality can fail;
- a regime label can fail;
- the exact witness can localize the omitted family member;
- the repair can be frozen separately rather than backdated;
- universal exact explanatory compression can itself be ruled out without turning that universal theorem into evidence for a selected named vocabulary.

This structure could inform future static-analysis interfaces, but the current paper does not claim a general program-analysis framework.

## 12. Statistics and timing

The 9,545/9,546 comparison count is deterministic evidence over registered panels. It is not reported with a population confidence interval or a significance test.

Timing is secondary engineering evidence. Final timing displays must state:

- runner/hardware environment;
- software versions;
- cold versus warm cache definition;
- number of timing observations and whether they are repeated measurements or distinct instances;
- medians/quantiles and raw values where retained.

Forecast speedups never provide theorem authority and must not compare a cold forecast to a warm DP baseline.

## 13. Reproducibility

Load-bearing artifacts are:

- `research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`;
- `research/extensions/orion-qg/QG5B_EXACT_FORECASTER_RESULTS.json`;
- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`;
- named QG7/QG7b receipts used only for the later closed-form boundary;
- `papers/orion-10-certified-static-forecasting/theory/vocabulary-minimality-v1/` for the universal explanation-vocabulary theorem and its independent regression.

`FORECAST_CERTIFICATE_AND_BENCHMARK_MAP_V2.md` specifies the reporting fields, theorem/executable bindings and benchmark decomposition required for the final package. The final repository release should add a permanent archive and explicit reuse licence before the manuscript calls code/data open or reusable.

## 14. Limitations

**Structural objective.** The forecast targets one frozen compiler objective, not full physical resource cost.

**Family scope.** Results do not automatically transfer to other TARE grammars, Tag ranks or compiler systems.

**No novelty in static analysis itself.** Current static quantum cost-analysis/resource-estimation work is donor territory.

**Closed-form families remain refutable.** Only the full support-two family has all-`n` exactness authority on this cut.

**Universal vocabulary theorem is not a `B′` verdict.** The theorem quantifies over arbitrary cost functions; the practical `B′` fibre question remains `CANNOT_CHECK` because the available 64 rows are selected witnesses and 676 evaluated rows were not serialized.

**Frozen panels are not a population sample.** Benchmark success fractions are descriptive properties of registered instances/generators.

**Forecast-only rows remain unverified.** A computed number without an exact receipt cannot be called confirmed.

**Timing is descriptive.** Runtime conditions can change independently of theorem validity.

**No physical quantum-advantage claim.** A smaller structural cost in this grammar is not an end-to-end advantage result.

## 15. Discussion

The most useful property of a certified forecast may be what happens when it fails.

One exact 10-versus-11 counterexample is enough to destroy the proposed universal closed form. Yet the same row simultaneously confirms two stronger pieces of structure: the forecasted construction is still a valid upper bound and the true optimum still lies inside the all-`n` support-two family. The certificate therefore turns a binary “right/wrong” event into a localized scientific update.

The successor sequence matters too. B′ is frozen only after the witness reveals its missing borrow coordinate. QG7 later refutes B′ with a different support-two shape. Those refutations are not embarrassment to be averaged away; they are the mechanism by which the compact explanatory model becomes more accurate while the theorem-backed exact family remains stable.

The vocabulary theorem explains why this process cannot terminate in a universally exact coarse explanation unless the scientific question restricts the admissible cost family. Exact prediction and compact explanation are different objectives. The selected QG7 witnesses are insufficient to decide the scoped `B′` question, so the manuscript preserves that limitation instead of converting a universal impossibility theorem into a post-hoc practical result.

This is the distinction ORION-10 contributes to static compiler forecasting: **bound, theorem, closed form, explanation vocabulary, regime label and forecast-only prediction should be carried as separate authority fields rather than compressed into one confidence score.**

## 16. Conclusion

In a frozen shared-Tag TARE compiler family, an initial static closed-form forecaster agrees with 9,545 of 9,546 exact comparisons but is nevertheless universally false: one prospectively generated row has exact cost 10 while the closed form returns 11. Because the forecast is authority-typed, the counterexample does not erase everything. The feasible upper bound survives, the all-`n` support-two theorem survives, the closed-form equality and regime label fail, and the exact witness identifies the missing configuration that a separately frozen successor then admits.

A second theorem-level boundary addresses explanation rather than prediction. Universal exact explanation admits no nontrivial coarse vocabulary: any vocabulary that must explain every cost function exactly must induce the discrete partition. That result is deliberately kept separate from the named `B′` question, which remains `CANNOT_CHECK` on the selected serialized evidence.

ORION-10 therefore does not claim a new generic static quantum cost analyzer. It demonstrates a narrower scientific principle in an exact compiler setting: **a static forecast is more useful when it reports which part is proved, which part is only evidenced, which part explains, and which part remains falsifiable.**