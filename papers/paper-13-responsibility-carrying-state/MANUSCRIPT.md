# Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse

**ORION-P13 · issue #666 · interface track #668**  
**Evidence freeze:** 2026-08-21  
**Submission status:** exact conditional core supported; `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`

**Current authority:** `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`. Historical
P13A execution and replay bytes remain unchanged; empirical safety–cost
superiority is not authorized.

## Abstract

A compact state is not simply “sufficient” or “insufficient”; sufficiency is
relative to the downstream responsibility. We formalize the exact conditional
notion and an RCS interface whose declared support controls reuse and reopening.
The paper retains an earlier frozen negative and an exactly reproducible P13A
benchmark. P13A reports zero RCS unsafe reuse, but a later hostile audit shows
that this endpoint is self-scored: RCS reuses exactly when its certificate says
`supported`, while harm is `REUSE and not supported` using that same certificate.
Across 3,840 enumerated points, certificate corruption moves the RCS action on
2,304 and the published harm on zero, leaving zero harm opportunities. Active
empirical superiority authority is therefore withheld. The exact
responsibility-relative support matrix and conditional interface invariant
remain supported; P13B must grade reuse against independently defined gold
support.

## 1. Introduction

Compression, abstraction and state reuse are normally evaluated against a named objective. Problems appear when a compact state is reused after the downstream responsibility changes. A summary that is sufficient to answer a factual question may omit provenance needed to authorize a scientific claim. A proof-state abstraction useful for next-tactic prediction may omit dependencies needed to diagnose or repair a failed proof. A control-state abstraction adequate for one policy may collapse distinctions needed for intervention or counterfactual analysis.

This is not merely an uncertainty problem. A system can be highly confident under its current compact state while the state omits a variable that becomes decisive under a new responsibility. Nor is it merely a provenance problem. Knowing exactly where a state came from does not establish what that state can safely support.

P13 asks:

> **Can a compact state carry a machine-checkable responsibility contract that says what it supports, what it omits, what changes invalidate reuse, and whether richer state can be reopened—without forcing every decision to reload raw evidence?**

The paper makes four contributions.

1. **Responsibility-relative sufficiency.** We define exact support as homogeneity of representation equivalence classes under a named downstream responsibility.
2. **A responsibility-carrying state interface.** RCS binds state identity to supported responsibilities, witnesses, omissions, recovery and reopen semantics without granting scientific self-authority.
3. **A permanent negative-result analysis.** The old P14A terminal remains negative; we identify why its finite-sample sentinel was a poor proxy for the exact responsibility question rather than silently weakening it.
4. **Outcome-contingency adjudication.** The protected benchmark is retained with
   a machine-readable audit showing its zero-harm endpoint cannot vary for RCS;
   provenance-only is also identified as a duplicate of unqualified reuse.

## 2. Donor boundary and novelty

### 2.1 Prior-owned concepts

Statistical sufficiency, state abstraction, bisimulation, predictive-state representations and causal abstractions already establish that different tasks can require different retained distinctions. Selective prediction and uncertainty gating already use confidence to decide when to abstain. Provenance and evidence-tracing systems already bind artifacts to their origin. Proof-carrying code and recent proof-carrying agent-action work already attach verifiable certificates to downstream actions. Memory-staleness work already asks when previously stored information ceases to be valid.

P13 claims none of these primitives.

### 2.2 Residual claim

P13 combines a different set of requirements into one operational object:

- sufficiency is keyed to a **named downstream responsibility**;
- the compact state lists unsupported/omitted distinctions;
- reuse is checked prospectively before protected failure;
- raw/richer recovery availability and cost are part of the contract;
- context changes can force `REOPEN_REQUIRED` or `CANNOT_CHECK`;
- evaluator/witness identity is distinct from the object's scientific authority;
- efficacy is measured on a safety–cost frontier against confidence, provenance and always-reopen controls.

The novelty is therefore not “certified reuse” in the abstract. It is **responsibility-scoped certified reuse with explicit reopen semantics and exact support conditions**. The historical benchmark's action and cost profile is descriptive; `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` withholds empirical safety–cost superiority because the published harm endpoint had no reachable opportunities.

## 3. Responsibility-relative sufficiency

Let raw world `X` induce correct output `g_rho(X)` for responsibility `rho`, and let compact representation be `Z=T(X)`.

### Definition 1 — exact responsibility sufficiency

`Z` is sufficient for responsibility `rho` over world set `Omega` if there exists `h_rho` such that

`g_rho(x)=h_rho(T(x))`

for every `x` in `Omega`.

Equivalently, every equivalence class induced by `T` must be homogeneous under `g_rho`: whenever `T(x)=T(x')`, then `g_rho(x)=g_rho(x')`.

### Definition 2 — responsibility-shift witness

A pair `(x,x')` witnesses insufficiency after a shift `rho_L -> rho_H` when

- `T(x)=T(x')`;
- `g_{rho_L}(x)=g_{rho_L}(x')`;
- `g_{rho_H}(x) != g_{rho_H}(x')`.

No learner is needed to establish such a witness. It is a property of the state abstraction and responsibility.

### Operational sufficiency debt

For empirical systems, define a benchmark debt for a transition `rho_L -> rho_H` as the verified higher-responsibility performance gap between richer and compact state, conditional on a prospectively frozen lower-responsibility equivalence/noninferiority requirement. It is an operational benchmark quantity, not a universal information measure.

## 4. Permanent negative history: the original P14A terminal

The historical experiment predates the grouped publication remap. It constructed independent binary latent variables `(x,m,r)` and responsibilities

- `PREDICT=x`;
- `DECIDE=x`;
- `INTERVENE=x*m`;
- `VERIFY=x*m`;
- `REPAIR=r`.

Representations were `Z1=(x)`, `Z2=(x,m)` and `Z3=(x,m,r)`. Exact enumeration produced the intended responsibility ladder: all representations were perfect for prediction/decision; `Z1` was exactly 0.5 on intervene/verify while `Z2/Z3` were 1.0; `Z2` was 0.5 on repair while `Z3` was 1.0. Exact upward debts were therefore +0.50.

However, the protocol also required the maximum deviation among 100 finite-sample sanity replicates of `n=1024` to be ≤0.05. The observed maximum was

`0.0556640625`

at replicate 92. The combined terminal is permanently

`P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET`.

### 4.1 Root-cause analysis

The harness function called `bayes_acc` grouped a finite sample by compact state, selected the majority target value **from that same sample**, and credited that majority on the same observations. It then compared this resubstitution estimate with the population values and maximized deviation over 100 replicates. The statistic therefore combines within-sample majority optimism with an extreme-value operation. Under the intended generator, exceeding a fixed 0.05 maximum-deviation sentinel is not rare.

The correct response is not to change `0.05` after seeing `0.0556640625`. The old terminal remains negative. The successor changes the scientific estimand: exact support is evaluated by exhaustive equivalence classes, while empirical efficacy is evaluated on a fresh independent safety–cost benchmark.

## 5. ResponsibilityCarryingState contract

An RCS contains compact state plus a fail-closed contract binding:

- raw/source evidence identity;
- compiler/transform identity and version;
- exact supported responsibility set;
- independent witness/certificate identity;
- intentionally omitted coordinates/information classes;
- required-same context coordinates;
- reopen-on-change coordinates;
- raw recovery/reconstruction availability and freshness;
- recovery/reopen cost;
- resource envelope under which support was established;
- evaluator identity;
- authority owner, distinct where required;
- explicit declaration that the object grants no scientific/novelty self-authority.

At reuse time the contract returns:

- `USE_COMPILED` when requested responsibility is supported and all bound conditions hold;
- `REOPEN_REQUIRED` when support does not hold but richer state can be recovered;
- `CANNOT_CHECK` when support is absent and recovery/verification cannot establish a safe route.

`CANNOT_CHECK` is a correct scientific disposition, not an error to be hidden.

## 6. Independent protected benchmark

### 6.1 Exact support world

The successor retains the same interpretable world but evaluates support exactly:

- `Z1` supports `{PREDICT, DECIDE}`;
- `Z2` supports `{PREDICT, DECIDE, INTERVENE, VERIFY}`;
- `Z3` supports all five responsibilities.

The exact equivalence-class matrix is checked directly and matches the registered support sets.

### 6.2 Held-out families and episodes

Protected seed: `2026082113`.  
Families: **24**.  
Episodes per family: **512**.  
Total protected episodes: **12,288**.

Family probabilities for hidden variables `m` and `r` vary independently over `[0.65,0.95]`. Compact state is `Z1` or `Z2` with equal probability; requested responsibility is uniform over the five tasks. Raw recovery is independently available with probability `0.95`.

When a compact state lacks a needed coordinate, an unqualified decoder uses the family MAP value. This deliberately creates cases that can be *high confidence yet structurally unsupported*.

### 6.3 Baselines

1. `UNQUALIFIED`: always reuse compact state.
2. `CONFIDENCE_ONLY`: reuse if estimated task accuracy is at least `0.80`; otherwise reopen when possible.
3. `PROVENANCE_ONLY`: valid lineage is present, so provenance alone permits reuse.
4. `RCS`: reuse only when exact responsibility support holds; otherwise reopen if raw is recoverable, else `CANNOT_CHECK`.
5. `ALWAYS_RAW`: reopen raw state whenever possible.

Fixed resource units are `REUSE=1`, `REOPEN=6`, `CANNOT_CHECK=0.5`.

Baselines 1 and 3 are the same policy on this corpus, and the list should be
read as four distinct policies rather than five. Every episode supplies valid
lineage by construction, so the provenance check never refuses and
`PROVENANCE_ONLY` reduces to "always reuse" — which is `UNQUALIFIED`. Their
measured rates agree to the last digit on every metric reported: unsafe reuse
`0.3961588541666667`, verified correctness `0.9248046875`, mean cost `1.0`.
Nothing here is a defect in the run; it follows from the construction stated
above. But it means beating provenance-only and beating unqualified are one
result reported twice, and it means this benchmark does not test whether a
provenance check helps — the check is never exercised. A corpus containing
episodes with absent or broken lineage would be needed for that, and it does not
exist here.

## 7. Results

Historical protected terminal:

`P13A_RCS_SAFETY_COST_SUPERIORITY_SUPPORTED`.

| arm | unsafe reuse | verified correctness | unnecessary reopen | mean cost |
|---|---:|---:|---:|---:|
| **RCS** | **0.0000** | **0.9807** | **0.0000** | **2.8747** |
| confidence only | 0.2156 | 0.9657 | lower than RCS | 1.8582 |
| provenance only | 0.3962 | 0.9248 | 0 | 1.0000 |
| unqualified compact | 0.3962 | 0.9248 | 0 | 1.0000 |
| always raw | 0.0000 | 0.9513 | 0.5744 | 5.7319 |

RCS emits `CANNOT_CHECK` for all **237** certificate-declared
unsupported/nonrecoverable cases and for no other protected case. Those action,
cost and replay values remain descriptive. They do not establish empirical harm
avoidance because the endpoint has zero reachable opportunities. Current
terminal: `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`, from
`P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json`.

Two fresh executions are byte-identical with SHA-256:

`ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`.

### 7.1 Why confidence fails

The hidden omitted coordinate is biased within a family, so the MAP decoder can be highly accurate on average and exceed the 0.80 confidence threshold. But high expected accuracy does not turn an unsupported equivalence class into a sufficient state. Confidence answers “how often am I right under this distribution?”; RCS answers “does this state retain the distinctions required by this responsibility?” Those are different questions.

### 7.2 Why provenance fails

Every compact state has valid source lineage. Provenance therefore verifies origin but says nothing about whether `m` or `r` was retained. Provenance-only reuse is structurally unsafe on 39.62% of protected episodes.

### 7.3 Why always raw is not the answer

Always reopening has zero historical unsafe compact reuse, roughly twice the mean RCS cost and unnecessary reopen on 57.44% of all episodes. Those are descriptive P13A rates. Whether RCS occupies a valid interior safety–cost frontier remains a P13B question because P13A's self-scored harm coordinate had no reachable opportunities.

## 8. Certificate transport, invalidation and authority

Responsibility support is conditional on evidence identity, transform version, required context, witness identity and resource envelope. A semantic change can therefore require preserve, reopen, revoke or `CANNOT_CHECK` behavior.

The RCS object does not certify its own scientific authority. An evaluator can establish an operational support contract without granting novelty, publication or safety-critical deployment authority. This separation is especially important in scientific workflows, where a compact summary may support question answering but not claim promotion.

## 9. Relation to certified reuse and proof-carrying agents

Recent proof-carrying agent-action work attaches model-agnostic certificates to agent actions and runtime governance. Provenance systems trace evidence and execution. Memory-staleness systems detect that stored state is no longer valid. These donors make it insufficient to claim that “state should carry a certificate.”

P13's discriminating contribution is the **responsibility key** plus **reopen semantics**: a state may be current, well-provenanced and high-confidence yet still be insufficient for a different downstream responsibility. The protected benchmark is designed exactly around that distinction.

## 10. Statistical and reproducibility notes

The responsibility-support matrix is deterministic and exact. The historical P14A terminal is reported exactly as frozen and is not reanalysed into a positive result. The independent P13A benchmark uses fresh seed/families and a different primary estimand.

Because the current P13A endpoint is a controlled finite benchmark with exact known support, the paper reports protected rates and deterministic replay rather than inventing post-hoc inferential tests. A real-system extension should define task/domain as the unit of generalization, use paired comparisons on matched episodes and report family/domain-block uncertainty.

## 11. Limitations and strongest remaining attacks

1. Responsibilities are discrete and known in the controlled world; real systems may have ambiguous or compositional responsibilities.
2. Exact sufficiency is strong. Approximate responsibility support needs frozen tolerances and calibrated external witnesses.
3. The RCS contract is only as reliable as its external witness and recovery metadata.
4. Resource costs are controlled units rather than measured real latency/tokens/IO.
5. A very high-risk domain may rationally choose always-raw despite higher cost; P13 does not claim universal reuse dominance.
6. The paper has not yet demonstrated verifier-backed Lean repair/diagnosis or a blinded scientific-workflow responsibility shift.
7. Certificate transport/revocation under real semantic version changes needs separate external validation.

## 12. Conclusion

Sufficiency is a contract over future responsibility, not an intrinsic property
of a compact representation. P13 makes that exact conditional boundary explicit
and preserves both historical failures and reproducible descriptive evidence.
It does not yet show that RCS prevents unsafe reuse under wrong, stale, forged or
overbroad certificates. That requires P13B with independently defined gold
support and a live harm denominator. **A compact state's declared authority must
be scoped to a named responsibility; whether the declaration is correct must be
tested independently.**

## References

- Classical statistical sufficiency, state-abstraction, bisimulation, predictive-state and causal-abstraction literatures are donor-owned foundations.
- Wang, Z. *Proof-Carrying Agent Actions: Model-Agnostic Runtime Governance for Heterogeneous Agent Systems.* arXiv:2606.04104, 2026.
- Chao, H., Bai, Y., Sheng, R., Li, T. & Sun, Y. *STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?* arXiv:2605.06527, 2026.
- Wang, Y. et al. *From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents.* arXiv:2606.04990, 2026.
- Doyle, J. *A Truth Maintenance System.* Artificial Intelligence 12(3):231–272, 1979.
- de Kleer, J. *An Assumption-Based TMS.* Artificial Intelligence 28(2):127–162, 1986.
- Park, J. & Sandhu, R. *The UCONABC Usage Control Model.* ACM TISSEC 7(1):128–174, 2004.
