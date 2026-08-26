# Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse

**ORION-ORION-23 · issue #666 · interface track #668**  
**Evidence freeze:** 2026-08-21  
**Submission status:** `P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED`; external validation open

**Current authority:** `P13_ACTIVE_CLAIM_AUTHORITY_V2.json`. Historical P13A
execution and its self-scored outcome failure remain unchanged; current authority
is limited to P13B's controlled finite-world certificate-corruption panel.
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
remain supported. A prospectively frozen P13B then grades against locally
authored certificate-independent gold. Across a 30-case state-task panel, all
four registered corruptions have 30 live mutation opportunities; authenticated
RCS makes zero unsafe reuses in every world and costs 0.6111 times always raw on
valid certificates. This is not external validation.
remain supported; P13B must grade reuse against independently defined gold
support.

## 1. Introduction

Compression, abstraction and state reuse are normally evaluated against a named objective. Problems appear when a compact state is reused after the downstream responsibility changes. A summary that is sufficient to answer a factual question may omit provenance needed to authorize a scientific claim. A proof-state abstraction useful for next-tactic prediction may omit dependencies needed to diagnose or repair a failed proof. A control-state abstraction adequate for one policy may collapse distinctions needed for intervention or counterfactual analysis.

This is not merely an uncertainty problem. A system can be highly confident under its current compact state while the state omits a variable that becomes decisive under a new responsibility. Nor is it merely a provenance problem. Knowing exactly where a state came from does not establish what that state can safely support.

ORION-23 asks:

> **Can a compact state carry a machine-checkable responsibility contract that says what it supports, what it omits, what changes invalidate reuse, and whether richer state can be reopened—without forcing every decision to reload raw evidence?**

The paper makes five contributions.

1. **Responsibility-relative sufficiency.** We define exact support as homogeneity of representation equivalence classes under a named downstream responsibility.
2. **A responsibility-carrying state interface.** RCS binds state identity to supported responsibilities, witnesses, omissions, recovery and reopen semantics without granting scientific self-authority.
3. **A permanent negative-result analysis.** The old P14A terminal remains negative; we identify why its finite-sample sentinel was a poor proxy for the exact responsibility question rather than silently weakening it.
4. **Outcome-contingency adjudication.** The protected benchmark is retained with
   a machine-readable audit showing its zero-harm endpoint cannot vary for RCS;
   provenance-only is also identified as a duplicate of unqualified reuse.
5. **Authenticated corruption successor.** P13B separates gold from the
   certificate, requires a live denominator in every corruption world, and
   tests fail-closed validation plus valid-panel cost.

## 2. Donor boundary and novelty

### 2.1 Prior-owned concepts

Statistical sufficiency, state abstraction, bisimulation, predictive-state representations and causal abstractions already establish that different tasks can require different retained distinctions. Selective prediction and uncertainty gating already use confidence to decide when to abstain. Provenance and evidence-tracing systems already bind artifacts to their origin. Proof-carrying code and recent proof-carrying agent-action work already attach verifiable certificates to downstream actions. Memory-staleness work already asks when previously stored information ceases to be valid.

ORION-23 claims none of these primitives.

### 2.2 Residual claim

ORION-23 combines a different set of requirements into one operational object:

- sufficiency is keyed to a **named downstream responsibility**;
- the compact state lists unsupported/omitted distinctions;
- reuse is checked prospectively before protected failure;
- raw/richer recovery availability and cost are part of the contract;
- context changes can force `REOPEN_REQUIRED` or `CANNOT_CHECK`;
- evaluator/witness identity is distinct from the object's scientific authority;
- efficacy is measured on a safety–cost frontier against confidence, provenance and always-reopen controls.

The novelty is therefore not “certified reuse” in the abstract. It is **responsibility-scoped certified reuse with explicit reopen semantics and exact support conditions**. The historical benchmark's action and cost profile is descriptive; `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` withholds empirical safety–cost superiority because the published harm endpoint had no reachable opportunities.

### 2.3 Ownership against the neighbouring ORION papers

Three papers in this programme reason about whether something survives a change,
and the words overlap enough that the boundaries are worth stating rather than
leaving to a reader to infer.

**ORION-17 and ORION-23 both say "transport", about different objects.** ORION-17 owns
closure-carrying transport: given a representation, responsibility/ontology or
objective change, does a previously established *closure* still hold, and can a
witness-aware policy tell when it does? Its unit is the closure and its failure
mode is a false closure. ORION-23 owns responsibility-scoped *reuse*: given a change
of responsibility, may a compact state or an issued support certificate be
relied on again, and what must be reopened when it may not? Its unit is the
support relation and its failure mode is unsupported reuse. A closure that
transports says nothing about whether the state behind it is sufficient for a
new responsibility, and the digits study here is precisely a case where a state
is current, provenanced and confident, and still inadequate.

**ORION-23 and ORION-25 both say "certificate", at different layers.** ORION-25 owns the
admission boundary above execution records: an attestation chain can verify
perfectly and still authorize no scientific claim, which is why its
full-key-compromise result is reported as a negative. ORION-23 sits above the object
rather than the record: it asks whether the *content* a certificate vouches for
still supports the responsibility now being asked of it. The two failure modes
are independent -- ORION-25's holds with the content valid and the custody
unobserved; ORION-23's holds with the signature perfect and the responsibility
changed -- which is why neither result substitutes for the other.

ORION-24's relation is different again and is not a boundary but a consolidation:
under issue #1086 decision D7, ORION-23 and ORION-24 are consolidated into one
machine-verifiable lifecycle-contract safety scope, recorded in §8.1.


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

Historical P13A protected terminal:
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

Always reopening has zero historical unsafe compact reuse, roughly twice the mean RCS cost and unnecessary reopen on 57.44% of all episodes. Those are descriptive P13A rates. P13A cannot establish the safety coordinate because its scorer had no reachable opportunities; P13B below uses a different certificate-independent gold estimand.

### 7.4 Prospectively frozen P13B

P13B defines gold support from task requirements and state variables without
reading the certificate. The complete panel contains six state forms and five
tasks. Omitted, overbroad, forged and stale-epoch corruption worlds each have 30
live mutation opportunities before scoring. Authenticated RCS rejects every
mutated certificate and makes zero gold-scored unsafe reuses in every world;
unverified RCS has 0, 5, 5 and 16 unsafe reuses in the omitted, overbroad, forged
and stale worlds, respectively. On valid certificates, authenticated RCS is exactly
correct and costs 0.6111 times always raw. Two fresh subprocess payloads are
byte-identical. Terminal:
`P13B_AUTHENTICATED_CERTIFICATE_SAFETY_COST_SUPPORTED_FINITE_WORLD`.
Always reopening has zero historical unsafe compact reuse, roughly twice the mean RCS cost and unnecessary reopen on 57.44% of all episodes. Those are descriptive P13A rates. Whether RCS occupies a valid interior safety–cost frontier remains a P13B question because P13A's self-scored harm coordinate had no reachable opportunities.

### 7.5 Composed safety–efficacy (P13C)

P13C composes the two successors on one registered benchmark: the P13B
authenticated-certificate machinery (imported unchanged from
`src/orion/study/p13/authenticated_successor.py`, parameterized by the frozen
`P13C_COMPOSED_GOLD_SPEC_V1.json`) is transplanted onto the P13A randomized
efficacy design (24 families x 512 episodes = 12,288 episodes, seed
`2026082113`, six-form certificate class), with the four-world corruption
register interleaved at a frozen 1-in-5 schedule (2,457 scheduled corrupted
episodes). Protocol, gold spec and runner were committed before first
execution, and two fresh-subprocess replays are byte-identical
(SHA-256 `645961cf01afe15f1b5976244b76b846c31d3c6119af4fbbc031e4b2a3611e57`).

All eleven frozen gates are green; terminal
`P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED` (result
`P13C_COMPOSED_RESULT_V1.json`, receipt
`P13C_COMPOSED_RESULT_RECEIPT_V1.md`). Within the registered composed finite
world:

| arm | unsafe reuse | verified correct | mean cost |
|---|---:|---:|---:|
| authenticated RCS | **0** (0/12,288) | 0.97933 | 3.0921 |
| unverified RCS | 330 (0.0269) | 0.98063 | 2.3282 |
| confidence only | 1,789 (0.1456) | 0.97412 | 1.7170 |
| unqualified | 3,649 (0.2970) | 0.93660 | 1.0000 |
| always raw | 0 | 0.95247 | 5.7386 |

Authenticated RCS rejects every scheduled corruption (2,457/2,457), makes zero
unnecessary reopens on the 9,831 valid-certificate episodes, remains exactly
`CANNOT_CHECK` on the 254 certificate-declared unsupported cases, and costs
0.539 times always-raw overall (0.498 on the 3,322-episode parent-form
subpanel, reproducing the P13A economy). The strongest trusting comparator,
unverified RCS, is noninferior in verified correctness (0.98063 vs 0.97933)
but commits 330 unsafe reuses (FORGED 66, OVERBROAD 87, STALE 177) plus 123
adversary-induced unnecessary reopens under omitted support, and forces 2,349
adversary-induced reopens on authenticated episodes overall. Authority
boundary: registered composed finite world only — no external validation,
real-agent safety, population generalization, certificate-authority
independence or deployment authority is claimed. Active authority:
`P13_ACTIVE_CLAIM_AUTHORITY_V3.json`.

### 7.6 Primary real-data result: the 17,970-episode responsibility shift

The results above are exact and verifier-backed, which is also their limit: they
are constructed worlds. The paper's primary *real-data* evidence is a
responsibility change on non-synthetic handwritten digits, where a compact state
learned for a parity responsibility is later reused under an exact digit-identity
responsibility. Across **17,970 episodes**:

| arm | exact-digit accuracy | unsupported exact-digit reuse |
|---|---|---|
| RCS | 0.9699 | **0** |
| confidence-only | 0.3957 | 0.7774 |
| provenance-only / unqualified | 0.2376 | 1.0 |

RCS reads **33** floats per episode against always-raw's **64**, a
**48.4375%** reduction in raw reads, while matching always-raw's task accuracies
exactly -- combined 0.9435, exact-digit 0.9699, parity 0.9171. The saving is
therefore not bought with accuracy.

This is the paper's claim in its sharpest real-data form. A compact
representation can be current, provenanced and highly confident with respect to
the old responsibility while being structurally inadequate for the stronger one.
Confidence continuity and provenance continuity each fail here in the direction
the contract predicts: provenance-only reuses without support in *every*
episode, and confidence-only in more than three quarters of them.

### 7.7 Donor-complete baseline: the D2 comparison

The relevant question is not whether RCS beats a weak baseline but whether the
responsibility-registration axis reduces to the provenance/grounding axis a
donor-complete memory already has. The D2 study answers it on 48 episodes
(4 cells x 12), protocol and gold dispositions frozen before the runner, with an
independent checker reporting zero invariant failures.

| arm | verifier-correct | unsupported reuse | mean literal reads | solver calls |
|---|---|---|---|---|
| `D2_CORE` | 36/48 | 12 | 6.25 | 12 |
| `D2_PLUS` | 36/48 | 12 | 6.25 | 12 |
| `RCS` | **48/48** | **0** | 5.0 | 24 |
| `COMPOSED` | **48/48** | **0** | 5.0 | 24 |
| `ALWAYS_RAW` | 48/48 | 0 | 5.5 | 24 |

Both donor arms -- including `D2_PLUS`, the strongest demand-graded form --
commit **12** unsupported reuses on `B_CHANGED_CURRENT`: they carry provenance
continuity across a responsibility change and reuse on the strength of it. RCS
and `COMPOSED` are perfect on the same episodes, and `COMPOSED` is also cheaper
than either donor arm on reads, 5.0 against 6.25.

That is the load-bearing comparison for the residual claim in §2.2:
responsibility registration is not reducible to provenance. The scope is
bounded -- five variables, a frozen episode family, seed 20261307 -- and the
result is that the two axes come apart inside it, not that they must come apart
in general.


## 8. Certificate transport, invalidation and authority

Responsibility support is conditional on evidence identity, transform version, required context, witness identity and resource envelope. A semantic change can therefore require preserve, reopen, revoke or `CANNOT_CHECK` behavior.

The RCS object does not certify its own scientific authority. An evaluator can establish an operational support contract without granting novelty, publication or safety-critical deployment authority. This separation is especially important in scientific workflows, where a compact summary may support question answering but not claim promotion.

### 8.1 Scope binding — machine-verifiable lifecycle contracts

Under issue #1086 decision D7 (portfolio disposition
`papers/ISSUE_1086_PORTFOLIO_DISPOSITION_V1.json`, binding artifact
`P13_P14_CONSOLIDATION_SCOPE_BINDING_V1.json`), ORION-23 and ORION-24 are consolidated
as one machine-verifiable lifecycle-contract safety scope. The supported scope
of this manuscript is exactly the machine-verifiable layer: certificate
validation, responsibility-scoped reuse decisions, reopen semantics,
corruption rejection and their registered benchmark gates. Broader
correct-governance or social-responsibility claims — that retaining or
reopening state is the *correct* governance decision for real organizations —
remain **CANNOT_CHECK**: they require two independent experts plus a
tie-break/custodian, which no artifact in this repository provides. On the
present evidence ORION-24 is not a separate paper at the 75+ bar; any external
lifecycle-contract campaign must derive gold only from the objective facts
enumerated in `P13_P14_LIFECYCLE_GOLD_DERIVATION_RULE_V1.md` and must never
use ORION itself as an external subject.

### 8.2 Drift-bounded transport: the 60-case result

Section 8 argues that support is conditional on evidence identity and that a
semantic change may require preserve, reopen, revoke or `CANNOT_CHECK`. That
argument is tested on a prospectively frozen 60-case grid (20 per stratum;
protocol and gold dispositions frozen before execution, two independent
implementations agreeing byte-for-byte on the result JSON).

| arm | verifier-correct | unsound transport | needless re-issue | mean literal reads |
|---|---|---|---|---|
| `UNCONDITIONAL` | 40/60 | 40 | 0 | 6.0 |
| `SIGNATURE_ONLY` | 60/60 | 0 | 20 | 11.333 |
| `CONDITIONAL_DRIFT_BOUNDED` | 60/60 | 0 | 0 | 10.0 |
| `ALWAYS_RE_ISSUE` | 60/60 | 0 | 20 | 11.333 |

The two failure modes are opposite and both are real. `UNCONDITIONAL` transports
40 certificates it has not earned; those decompose as 20 `CONFLICTING` cases,
where the stored model violates the shifted formula and the served certificate is
content-invalid, and 20 `MIXED` cases, which are unsound under the frozen
transport predicate because the justification set changed, though the content may
still satisfy. That decomposition is why verifier-correct is 40/60 rather than
20/60: half the unsound transports are unsound as protocol, not as content.
`SIGNATURE_ONLY` fails in the other direction, refusing all 20 sound redundant
transports -- a missed-efficiency witness, not a safety failure.

`CONDITIONAL_DRIFT_BOUNDED` is exact on this grid, with zero unsound transports,
zero needless re-issues and 60/60 verifier-correct, and on the redundant stratum
it is cheaper than always re-issuing (8.0 against 12.0 mean literal reads, with
payload accounting held identical at six reads per served certificate so the arms
differ only in verification).

What this does not earn is stated with the result. It is bounded to CNF
clause-add, clause-drop and strengthening drift: it says nothing about
adversarially chosen drift or non-monotone formula rewrites, nothing about
transport in real agent workflows, and it does not establish that the frozen
predicate is the *unique* correct transport policy. What it establishes is that
the predicate is exact on this grid and that its two named competitors fail in
the directions predicted for them in advance.


## 9. Relation to certified reuse and proof-carrying agents

Recent proof-carrying agent-action work attaches model-agnostic certificates to agent actions and runtime governance. Provenance systems trace evidence and execution. Memory-staleness systems detect that stored state is no longer valid. These donors make it insufficient to claim that “state should carry a certificate.”

ORION-23's discriminating contribution is the **responsibility key** plus **reopen semantics**: a state may be current, well-provenanced and high-confidence yet still be insufficient for a different downstream responsibility. The protected benchmark is designed exactly around that distinction.

## 10. Statistical and reproducibility notes

The responsibility-support matrix is deterministic and exact. The historical P14A terminal is reported exactly as frozen and is not reanalysed into a positive result. The independent P13A benchmark uses fresh seed/families and a different primary estimand.

P13B is a complete registered 30-case finite panel, not a population sample, so
it reports exact counts rather than a post-hoc inferential interval. Every
corruption world must have a nonzero opportunity denominator before zero
violations can be interpreted. A real-system extension should define task/domain
as the unit of generalization, use paired comparisons on matched episodes and
report family/domain-block uncertainty.

## 11. Limitations and strongest remaining attacks

1. Responsibilities are discrete and known in the controlled world; real systems may have ambiguous or compositional responsibilities.
2. Exact sufficiency is strong. Approximate responsibility support needs frozen tolerances and calibrated external witnesses.
3. The RCS contract is only as reliable as its external witness and recovery metadata.
4. Resource costs are controlled units rather than measured real latency/tokens/IO.
5. A very high-risk domain may rationally choose always-raw despite higher cost; ORION-23 does not claim universal reuse dominance.
6. The paper has not yet demonstrated verifier-backed Lean repair/diagnosis or a blinded scientific-workflow responsibility shift.
7. Certificate transport/revocation under real semantic version changes needs separate external validation.

## 12. Conclusion

Sufficiency is a contract over future responsibility, not an intrinsic property
of a compact representation. ORION-23 makes that exact conditional boundary explicit
and preserves both historical failures and reproducible descriptive evidence.
P13B shows that the authenticated policy rejects the four registered corruptions
without unsafe reuse in its locally authored finite panel. It does not establish
external witness correctness, real-agent safety or population generalization.
**A compact state's declared authority must be scoped to a named responsibility;
whether that declaration remains correct outside the registered world must be
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
