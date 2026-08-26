# Certified Static Forecasting for Quantum Compilation: What Survives a Counterexample?

**ORION-ORION-10 Manuscript V2 — publication-synthesis draft**  
Publication cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER.md` + `PUBLICATION_FOUNDATION_V2.md`

## Abstract

Static quantum-resource forecasts are useful only if a reader can tell which parts are guaranteed and which are extrapolated. We study that distinction in a frozen shared-Tag TARE compilation family for which an unrestricted exact dynamic program supplies ground truth. The initial static forecaster computes the minimum cost over three explicit feasible subfamilies without calling the unrestricted DP. Its output combines four different epistemic layers: a constructive upper bound from feasible constructions, an all-`n` support-two theorem, a finite-domain closed-form exactness hypothesis, and forecast-only rows lacking an exact receipt. On 9,546 DP-compared instances, the initial forecaster is exact on 9,545 and fails on exactly one prospectively generated `n=3` instance: the true optimum is 10 while all three closed-form terms return 11. The counterexample does not invalidate the certified layers: `10 <= 11` preserves the upper bound, and the exact optimum still lies in the theorem-backed support-two family. Instead it localizes the failed component to an omitted out-of-target-support borrow configuration. A separately frozen successor enlarges the borrow family and uses the exact support-two family minimum `F2=C_D++`; the registered successor panels then reproduce zero forecast error while retaining the original refuting instance in the evidence record. Later companion work finds a further closed-form counterexample inside the same support-two world, again leaving the support theorem intact. The main result is therefore not a high accuracy rate. It is an authority decomposition for static compiler forecasts: proof-backed bounds, theorem-backed search restrictions, finite-domain equalities and unverified predictions must remain distinct so that a counterexample invalidates only the layer it actually refutes.

## 1. Introduction

Quantum cost estimation spans a broad stack. Analytical cost models can reason about program constructs before full low-level compilation; compilation-driven resource estimators translate circuits into logical or physical primitives; hardware-aware tools account for routing, error correction and architecture; verified optimizers combine semantic equivalence with explicit cost models. Recent examples include program-level T-complexity cost analysis, compilation-driven resource estimation, and formally verified cost-aware quantum optimization. Static prediction of a quantum cost is therefore not new by itself.

The harder issue is **authority**. A number emitted by a fast cost predictor may be a theorem, a safe upper bound, a value that happened to be exact on a benchmark, or an unverified extrapolation. These categories behave differently when the predictor encounters a counterexample. If they are collapsed into one accuracy score, an exact failure either appears to destroy the entire method or is hidden as a small error rate. Neither interpretation is scientifically satisfactory.

We study this problem in a deliberately exact setting. The frozen R6M shared-Tag TARE grammar has an unrestricted dynamic-programming referee and several explicit restricted compilation families. Companion work proves an all-`n` theorem: under the frozen raw support-count objective, an exact optimum always exists with frame support at most two, so the unrestricted optimum equals the minimum over the full support-two family `D++`. This gives us something rare for a forecasting study: an exact theorem-backed layer against which cheaper closed-form predictors can be separated.

The paper follows one complete scientific cycle. First, we define a cheap static forecaster `F` from three feasible subfamilies and state which properties are constructive, proved, or merely evidenced. Second, we test it on frozen domains. Third, a prospectively generated instance refutes the closed-form equality. Fourth, we show exactly which certificate components survive that failure. Fifth, the witness localizes the missing compilation mechanism, which is admitted only through a separately frozen successor. Finally, later companion counterexamples show why even the repaired closed form must remain distinct from the theorem-backed full support-two forecaster.

Our contribution is not that 9,545 predictions were correct. It is that the **one wrong prediction is more informative than the hit rate** because the forecaster exposes what was proved, what was conjectured, and what changed after the refutation.

## 2. Setting: exact compilation truth and restricted forecast families

### 2.1 Frozen compilation family

The scientific object is the R6M three-block shared-one-bit-Tag TARE grammar under the frozen raw support-count objective used throughout the ORION-Q R6 sequence. Six Pauli targets are grouped into three ordered blocks. Each block chooses an anticommuting frame pair, target assignment and central branch; a shared Tag imposes a common label relation; Restore strings map frame representatives to target Paulis. The unrestricted optimum `C_DP` is computed by the committed exact dynamic program with proof-carrying witness checks.

This paper does not claim that the objective is a physical end-to-end resource model. It is a structural compiler objective with fixed multipliers. Architecture-level resource estimates and gate/runtime models are separate research objects.

### 2.2 Restricted families

The forecast uses explicit feasible subsets of the unrestricted grammar.

- `R6L` / donor family: weight-one frame restrictions with the registered common-anchor/shared-Tag construction; cost `C_R6L`.
- `D+`: weight-one frames may split across anchors with the minimum compatible shared Tag; cost `C_Dplus`.
- `B`: a registered borrow construction using a weight-one Tag and a support-two frame at a cheap central branch; minimum cost `f_B`.
- `D++`: the full family whose frame Paulis have global support at most two; cost `C_Dxx`.

Because each named construction is feasible, its cost is an upper bound on the unrestricted optimum. The key distinction is that `D++` is not merely another heuristic family: companion theorem R6S proves `C_DP=C_Dxx` for every `n` and every instance of this frozen grammar/objective.

## 3. A typed forecast certificate

The initial static forecaster is

`F(t) = min(C_R6L(t), C_Dplus(t), f_B(t))`.

The forecast path never calls the unrestricted DP. But the expression should not be read as one indivisible theorem. We attach four authority classes.

### 3.1 Constructive layer

Every member of `R6L`, `D+`, and `B` is a feasible compiler configuration. Therefore

`C_DP <= F(t)`

is a constructive bound. A future counterexample to equality can still satisfy this inequality.

### 3.2 Theorem layer

The independent R6S theorem proves

`C_DP = C_Dxx`

for all `n` in the frozen R6M/raw-support setting. The theorem says the exact search can be restricted to support-two frames. It does **not** say that the three named closed-form families span all of `D++`.

### 3.3 Finite exactness / conjectural layer

Before the prospective counterexample, the identity

`C_DP = min(C_R6L, C_Dplus, f_B)`

held on the registered R6Q panels and was used as a closed-form characterization on those domains. Its authority was finite-domain evidence, not an all-`n` theorem.

### 3.4 Forecast-only layer

Some external library subjects can be evaluated by the static formulas but do not have a committed exact-DP receipt. Those rows are predictions only. They are kept separate from verification statistics.

This type discipline is the central methodological contract: a result is allowed to refute only a claim whose authority actually covers it.

## 4. Initial benchmark: 9,545 exact forecasts and one error

The QG5 benchmark compares the original forecaster with exact DP truth on 9,546 instances across the registered structured, chemistry/receipt-bound and fresh seeded domains. It reports 9,545 exact forecasts and exactly one nonzero error.

Reporting this as “99.99% accurate” would obscure the science. The panels are frozen constructions, not a random sample from a natural population of TARE instances, so the fraction is not a calibrated population error probability. More importantly, the single failure directly tests the proposed equality.

The exhaustive structured-`n=2` slice contains 9,261 instances, all forecast-exact. The registered chemistry rows are bound to committed exact receipts. The fresh seeded panel contains 240 instances across `n=2,3`; 239 are exact and one is not. No post-outcome extension of the panel is used to dilute or erase the mismatch.

## 5. Prospective refutation: `C_DP=10 < 11=F`

The refuting row occurs in the fresh panel at seed `20260826`, `n=3`, index 7. The frozen target pairs are

`[[[3,6],[7,3]], [[7,3],[3,4]], [[0,3],[2,2]]]`.

The exact referee gives

`C_DP = 10`.

Every term in the original closed-form forecaster gives 11:

`C_R6L = C_Dplus = f_B = 11`,

so `F=11` and the forecast error is exactly 1.

### 5.1 What failed

The equality layer failed. The original regime predicate labeled the row donor-exact even though the exact optimum is cheaper than the donor family. Therefore the finite predicate's extrapolation beyond its previously verified domains is refuted.

### 5.2 What did not fail

Two stronger pieces remain correct on the same row.

First, the constructive upper bound remains true:

`C_DP=10 <= 11=F`.

Second, the all-`n` support theorem remains true. A support-two witness has cost 10, so

`C_Dxx = C_DP = 10`.

The counterexample therefore does not say “the static theory was wrong.” It says **the exact optimum lies in the certified support-two universe but outside the cheaper closed-form subfamilies used by `F`**.

This is why authority typing matters. Had `C_DP<=F`, `C_DP=C_Dxx`, and `C_DP=F` been summarized as one empirical success claim, the counterexample would not tell us which scientific statement to repair.

## 6. Root-cause localization: an omitted borrow home

The exact support-two witness localizes the missing mechanism. One block uses a phantom support-two frame whose borrow home lies outside that block's own target support. The original `B` family restricted the borrow home too strongly and therefore could not instantiate the configuration.

This diagnosis is structural rather than statistical: the witness can be checked directly against the family definition and exact cost function. It creates a natural successor family, but the successor is not allowed to inherit authority retroactively.

## 7. Separately frozen successor: B′ and the theorem-backed forecaster

QG5b freezes an enlarged borrow family `B′` that allows the missing out-of-own-target-support borrow homes. The original refuting instance is retained in the successor receipt; `f_Bprime=10` on that row, matching exact truth.

More importantly, QG5b separates two notions of “fixed forecaster.”

### 7.1 Cheap enlarged closed form

`min(C_R6L, C_Dplus, f_Bprime)`

is cheaper and interpretable. It is exact on the registered QG5b finite panels, but the receipt explicitly says its all-`n` completeness remains a conjecture.

### 7.2 Theorem-backed exact static forecaster

`F2(t)=C_Dxx(t)`

enumerates the full theorem-sufficient support-two family without calling the unrestricted DP. Because R6S proves `C_DP=C_Dxx` all `n` in the frozen family/objective, `F2`'s exactness is theorem-backed rather than inferred from its finite zero-error benchmark.

This distinction prevents a common rhetorical mistake. A predictor can be *empirically zero-error on a panel* and still be conjectural; another computation can be *exact by theorem* even if benchmark evaluation is used only as an implementation consistency check.

## 8. A second lesson: closed forms can fail again

Later companion work deliberately attacks B′ and finds 64 exact fourth-regime witnesses for which

`C_Dxx < min(C_Dplus, f_Bprime)`.

The new witness shape combines a weight-two Tag with a phantom borrow. A separately frozen `B″` family closes the registered finite hostile panels, including 10,481 instances with no fifth-configuration candidates. Yet the all-`n` closed-form identity remains open because one consolidation link remains unproved in the current publication cut.

For ORION-10 this companion result has one role: it demonstrates that **repairing one failed closed form does not upgrade the repaired closed form to theorem status**. The support-two forecaster `F2=C_Dxx` remains exact because its authority comes from the theorem; the interpretability-oriented named-family minimum remains subject to further refutation.

The detailed fourth-regime mathematics belongs to companion ORION-09.

## 9. Verified forecasts versus forecast-only library rows

The forecaster can emit costs for public library subjects even when an unrestricted exact receipt has not been committed. Those predictions are useful for prioritization, but they do not become verification merely because the same program produced both forecasted and verified rows.

The result package therefore distinguishes statuses such as:

- `DP_RECEIPT_COMMITTED__FORECAST_BOUND` — an exact comparison exists;
- `UNVERIFIED_FORECAST__NO_DP_RECEIPT` — prediction only.

A final publication table should preserve this status column. Unverified rows must not enter an “accuracy” denominator or be described as confirmations.

## 10. Relation to quantum cost modeling and resource estimation

Static and analytical cost models are well established in quantum programming. Work on control-flow T-complexity derives program-level cost formulas that avoid repeatedly compiling large circuits. Compilation-driven resource-estimation systems translate logical programs through architecture assumptions to estimate fault-tolerant cost. Relationally verified optimizers combine semantic verification with multi-objective cost models. These systems solve broader or different problems than the narrow TARE structural objective studied here.

Accordingly, ORION-10 does not claim that predicting quantum cost without full compilation is new. The narrower contribution is the **authority decomposition of one exact compiler-family forecast and the scientific handling of its refutation**:

`feasible bound -> theorem-backed restriction -> finite/conjectural closed form -> prospective counterexample -> localized successor freeze`.

That sequence also distinguishes ORION-10 from generic machine-learning cost predictors. The central outcome is not predictive `R^2` or average error. It is a proof/refutation structure in which a single exact mismatch determines which formal statement survives.

## 11. Statistics and timing

The exact DP comparisons are deterministic properties of frozen instances. We therefore do not attach p-values or population confidence intervals to the 9,545/9,546 count. The panel was constructed under explicit generators; treating it as an iid sample from an undefined universe would create false precision.

Timing measurements are secondary. The existing receipts report speedups under specified cold/warm cache and runtime conditions, but timing is excluded from the canonical scientific stdout under the inherited convention. Any final timing figure must state hardware/software/cache conditions and is descriptive only. No timing result changes the exactness/certificate claims.

## 12. Reproducibility

The result-bearing artifacts are committed under:

- `research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`;
- `research/extensions/orion-qg/QG5B_EXACT_FORECASTER_RESULTS.json`;
- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`;
- companion QG7/QG7b receipts for the later closed-form boundary.

The protocols under `development/orion-qg-regime-geometry/` bind the forecast definitions, generators, seeds, outcome branches and hostile checks. Exact counterexamples are serialized rather than summarized only by aggregate counts. The final package should expose deterministic regeneration commands and content digests, and it should not invent a DOI/archive identifier until a real deposit exists.

## 13. Limitations

**Frozen structural objective.** The exact theorem and forecasts concern the registered R6M raw support-count objective, not a physical hardware cost. ORION-10 does not estimate full fault-tolerant runtime, qubit footprint or error rate.

**Compiler family.** Results do not transfer automatically to other TARE grammars, Tag ranks or compiler families.

**Closed-form incompleteness.** Named interpretable subfamilies have been refuted more than once. The current publication cut does not contain an all-`n` proof that the latest small union of subfamilies is complete.

**Panel interpretation.** Zero error on a frozen panel is not a theorem or a population probability. Exactness authority must come from theorem/receipt type, not from a large denominator.

**Forecast-only rows.** Predictions without exact receipts remain unverified.

**No physical advantage claim.** A smaller structural objective in this grammar is not by itself evidence of end-to-end quantum advantage.

## 14. Discussion

The most useful feature of a certified predictor may be its behavior when it is wrong. In QG5, one counterexample among thousands did not force us to choose between “ignore the outlier” and “discard the method.” Instead, the certificate hierarchy made the scientific disposition mechanical:

- the feasible upper bound survived;
- the all-`n` support theorem survived;
- the closed-form equality failed;
- the regime label failed;
- the witness localized a missing feasible configuration;
- the successor was frozen after that diagnosis.

This is a stronger scientific object than an accuracy number. It turns refutation into localization.

The later B′/B″ sequence also shows why theorem authority and model convenience should remain separate. Small named families are attractive because they are interpretable and cheap. But whenever their completeness is not proved, a fresh counterexample must remain a legitimate outcome. The full theorem-sufficient family can provide exactness even while the search for a simpler closed form continues.

A broader implication is that resource-estimation systems may benefit from reporting **why** a number is trustworthy, not only the number itself. In a general compiler this could mean separating semantic invariants, safe upper bounds, calibrated empirical models and unverified extrapolations. ORION-10 demonstrates that principle only in one narrow exact family; extending it is future work.

## 15. Conclusion

A static compiler forecaster should not be treated as a single claim. In the frozen shared-Tag TARE setting, the original forecaster combined constructively safe bounds, an exact all-`n` support theorem, a finite-domain closed-form identity and unverified predictions. A prospectively generated instance refuted the identity at `10 < 11` while satisfying the proven components exactly. The resulting witness exposed the missing mechanism and motivated a separately frozen successor. Later counterexamples again refine the cheap closed form without threatening the theorem-backed support-two forecaster.

The durable result is therefore an epistemic one as much as a compiler result: **when prediction layers carry explicit authority, a counterexample can invalidate precisely what failed and preserve what was actually proved.**