# P9 final claim-to-citation map V1

Purpose: prevent final manuscript prose from drifting beyond the post-result novelty disposition. Every broad principle must be credited to prior work; only the exact P9 study design/results may be described as the paper's contribution.

## Required body citations

| Manuscript statement / concept | Required donor citation(s) | Allowed P9 wording |
|---|---|---|
| graph/relational inductive biases can matter for structured reasoning | `ying2021graphormer`, `hu2020hgt`, `rampasek2022gps` | prior-work motivation only |
| local vector spaces / relation maps / consistency are established objects | `gebhart2021knowledge`, `bodnar2022sheaf` | P9 may use analogous coordinates but not claim sheaf novelty |
| neural algorithmic reasoners and language+structured-reasoner hybrids exist | `velickovic2022clrs`, `bounsi2024transnar` | P9's escalation discipline is not a new NAR architecture |
| learned reusable modules/libraries/mechanics are prior art | `ellis2020dreamcoder`, `grand2023lilo` | P9 D0 mechanic tasks are diagnostic only |
| non-language latent reasoning exists | `hao2024coconut` | latent branch is deferred/not load-bearing |
| reusable rule/entity binding is prior art | `goyal2021nps` | no P9 binding novelty |
| mechanism-centric scientific representations are prior art | `posner2026mwm` | no P9 causal/mechanistic discovery claim |
| preserving the same underlying structured content in a different serialization can change model performance | `lo2026serialization` | P9 D1's same-information control is an application-specific discriminator, not discovery of serialization friction |
| representation/perception failure can be isolated from reasoning/computation failure in neuro-symbolic systems | `liem2026temporal` | P9's contribution is its exact frozen diagnostic study, not the general distinction |
| deterministic benchmarks plus symbolic/neural oracle controls can isolate algorithmic/iterative computation failure | `anonymous2026chokepoints` | A5/M1 decomposition must be presented as a bounded instance, not a new general methodology principle |
| reasoning tasks may be underspecified and require information acquisition / explicit uncertainty | `li2025questbench` | P9's `UNRESOLVED` hostile cases are part of its exact benchmark, not novelty for missing-information evaluation |

## P9-specific claims that cite P9 evidence, not external novelty parents

### C1 — exact view-collision diagnostics

Allowed:

> On the frozen P9 world set, grouping instances by exact model-visible fingerprints exposes representation views in which different protected targets are observationally indistinguishable to a deterministic predictor.

Boundary: describe the resulting ceiling as **empirical deterministic accounting over the frozen equivalence classes**, not a new theorem about Bayes error, sufficient statistics, aliasing or POMDP observability.

Evidence: D0 information lattice / M0 task harness.

### C2 — M1 computation residual

Allowed:

> In M1, the semantic view contains sufficient information for protected affine gluing under the exact sample ceiling, but the frozen generic classical learner grid remains near chance; therefore the observed residual is computational rather than an information deficit on this benchmark.

Evidence: `M1_RESULT_V1_5.json` + `M1_INDEPENDENT_VERIFICATION_V1_5.json`.

Must cite `liem2026temporal` and `anonymous2026chokepoints` in the surrounding related-work/discussion text to credit the broader diagnostic principle.

### C3 — explicit computation closes M1's D0 residual

Allowed:

> A prospectively frozen payload-only exact affine-composition procedure closes the same D0 operation once the local map values are visible; the bounded experiment therefore does not justify neural architecture escalation for this atom.

Evidence: A5 bounded-verified result + M1.

Boundary: no claim that symbolic fallback or neuro-symbolic decomposition is new.

### C4 — relation semantics and failure history are load-bearing D0 coordinates

Allowed:

> TYPED relation semantics separate the A2 hostile pair, and admitted SEMANTIC failure history separates the A4 hostile pair; explicit payload-only selectors are sufficient on those atoms.

Evidence: `A2_A4_D0_EXPLICIT_RESULT_V1_1.json` + verification receipt.

### C5 — D1 protected whole-domain transfer

Allowed:

> On the prospectively frozen D1 study, a classical model over explicit typed relational comparisons reaches 1.0 protected accuracy on a whole held-out procedural domain, compared with 0.90625 for untyped pair structure, 0.5 for a same-information typed serialization, and 0.25 for reminted transcript features; it also retains 1.0 on protected double corruptions and `UNRESOLVED`.

Evidence: `D1_RESULT_V1_2.json` + `D1_INDEPENDENT_VERIFICATION_V1_2.json`.

Must cite `lo2026serialization` around the interpretation. The general statement that native structured organization can outperform serialization is donor-owned.

### C6 — final complexity-escalation conclusion

Allowed:

> Across the bounded P9 atoms, the surviving information coordinates are exploitable by simple classical or exact explicit procedures, and no prospectively frozen residual remains that requires a neural graph/sheaf/NAR/latent architecture.

Boundary: this is a **study-scope stop decision**, not evidence that richer architectures are generally useless.

## Prohibited uncited/overbroad phrases

Do not write any of the following as P9 novelty:

- "we introduce relational inductive bias";
- "we discover that serialization loses structure";
- "we are the first to separate representation from reasoning failure";
- "we introduce symbolic fallback/oracle reasoning";
- "we solve compositional generalization";
- "we establish that explicit structure is superior to latent reasoning";
- "we introduce uncertainty/UNRESOLVED for underspecified tasks";
- "we learn reusable scientific mechanics";
- "we provide a new sheaf/graph/neuro-symbolic architecture".

## Final audit rule

Before PDF freeze, search the manuscript for every broad concept above and verify that:

1. the donor citation is present in the same paragraph or an immediately linked related-work paragraph;
2. the P9 wording is bounded to the actual frozen experiment;
3. result numbers come only from `OFFICIAL_EVIDENCE_SUMMARY_V1.json` / generated tables;
4. no sibling ORION paper's archival claim is republished as a P9 contribution.
