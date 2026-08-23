# P12 Claim–Evidence Ledger

**Stable ID:** ORION-P12  
**Issue:** #665  
**Accounting owner:** #664

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| state construction and reasoning can have different marginal value across tasks | SUPPORTED / EXISTENCE + CONTROLLED | formal construction + P12A | controlled heterogeneous resource worlds |
| joint allocation beats fixed `(1,1)` under identical two-unit budget | SUPPORTED | P12A + V2 adjudication | +0.342651 mean success gain |
| joint allocation beats both one-axis adaptive policies because it reads both signals | **AUTHORITY WITHHELD / CANNOT_CHECK** | `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` | baselines' action-set ceilings are below the winner; no causal superiority wording |
| historical gain is positive in every held-out family | DESCRIPTIVE HISTORY ONLY | P12A | does not repair the capability confound |
| joint policy gets more compute | FALSE | budget audit | every action satisfies `c+r<=2` |
| protected signals use outcomes | FALSE | construction/protocol | pre-outcome noisy requirements only |
| V1 runner alone satisfied every protocol gate | **FALSE / CORRECTED** | PR hostile review | replay was omitted from the V1 terminal path |
| exact frozen runner is byte-identical across two fresh executions | **SUPPORTED / REPLAY-ADJUDICATED** | V2 adjudicator | both SHA-256 = `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947` |
| adaptive test-time compute is novel to P12 | FALSE / DONOR-OWNED | current literature | do not claim |
| dynamic state/context selection is novel to P12 | FALSE / DONOR-OWNED | retrieval/memory/state literature | do not claim |
| two-axis state–reasoning allocation has controlled superiority under matched total compute | **NOT AUTHORIZED** | `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` | identical budget did not mean identical action capability |
| two signals improve exact allocation when all arms share the same four actions | **SUPPORTED / CONTROLLED P12B** | `P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1_1.json` | mean gain 0.253906 across 32 family RNG blocks; stratified 95% CI [0.251221, 0.256653]; locked CPython 3.12.13 / NumPy 2.5.2 replay |
| real LLM/prover superiority | OPEN | no real-system result | not authorized |

## Evidence correction

The historical P12A terminal remains `P12A_SUPERIORITY_AUTHORITY_WITHHELD` in
`P12_ACTIVE_CLAIM_AUTHORITY_V1.json`. Current bounded authority is
`P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED` in
`P12_ACTIVE_CLAIM_AUTHORITY_V3.json`.

The V1 P12B receipt is preserved unchanged. Its scientific counts and estimates
reconstruct under the repository lock, but strict whole-core replay rejects its
NumPy 2.3.5 environment field. The append-only V1.1 result binds `uv.lock`,
CPython 3.12.13 and NumPy 2.5.2 and passes two fresh byte-identical subprocesses.

The original P12A executable evaluated seven frozen scientific gates but did not put the protocol's byte-identical replay requirement into its own terminal decision. That is an evidence-adjudication defect, not a change in the scientific comparison. The V1 runner terminal is therefore **non-authoritative alone**.

`verify_p12a_protocol_adjudication_v2.py` executes the unchanged V1 runner twice in fresh subprocess directories, hashes the complete canonical JSON, checks every original scientific gate, and only then emits the authoritative terminal. Both executions reproduce the committed scientific payload exactly with SHA-256 `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`. No policy, seed, threshold, budget, metric, comparator, family, or outcome was changed.

## Donor subtraction

- Strategic/bandit test-time compute allocation owns adaptive reasoning-budget allocation across inputs.
- Constrained-policy test-time allocation owns accuracy-under-average-compute optimization and learned allocation policies.
- Adaptive in-context demonstration/generation and current “when to think” work own difficulty-conditioned reasoning allocation and adaptive inference effort.
- Retrieval, compression and query-conditioned state systems own adaptive state/context construction as a primitive.

## Residual novelty

P12's residual is not “adaptive inference.” It is the **resource-locus problem**.
P12A motivates that problem but confounds signal count with action capability.
P12B resolves that controlled comparison by holding the four actions fixed; the
real-system resource-locus claim remains open.

## Strongest authorized headline

> P12A's apparent superiority is historically retained but confounded by action
> capability. In prospectively frozen P12B, all arms share four exact actions and
> the two-signal policy gains 0.253906 over the stronger one-signal policy across
> 32 independent family RNG blocks.
