# ORION Frontier Support/State Claim Ledger V1

Status: **CONTROLLED RESULTS ONLY — NO PROGRAMME-LEVEL REAL-DOMAIN CLAIM YET**

## Current evidence

### E0 — merged ORION donors
- P9 bounded representation/accessibility evidence: prior, merged to main.
- P10 bounded Mathlib recurrence evidence: prior, merged to main.
- #618 controlled structural-accessibility results: separate research branch, not evidence of this frontier programme unless explicitly grafted after its own final receipts.

### E1 — F2 exact certificate only
Status: `SUPPORTED_CERTIFICATE_ONLY`.

Receipt: `results/F2_CERTIFICATE_RECEIPT_V1.json`.

Supported:
- 1024 finite states checked;
- 343 future action sequences checked per state;
- 32 five-bit quotient classes have zero future-reward-signature violations;
- all 16 four-bit hostile quotient classes contain counterexamples.

Not supported yet:
- learner/sample-efficiency advantage;
- LLM utility;
- state minimality;
- open-world losslessness.

### E2 — F6 controlled persistence/replay tax
Status: `SUPPORTED_CONTROLLED__CI_REPLAY_PENDING`.

Receipt: `results/F6_RESULT_RECEIPT_V1.json`.

Frozen-protocol deterministic execution across `L={8,16,32,64}` and `b={2,4,8,16}` found:
- zero full-state persistence mismatches against transcript replay;
- zero certified five-bit persistence mismatches against transcript replay;
- 110,656 branch-outcome mismatches for the deliberately lossy last-four-actions control;
- exact operation ReplayTax rises monotonically with branch count and, for `b>=4`, history length;
- exact ReplayTax at `L=64,b=16` is `1072/112 = 9.571428571428571`;
- certified state stores 5 task-relevant bits versus 10 bits for full state.

Terminal: `PERSISTENT_SUFFICIENT_STATE_REDUCES_REPLAY_SCALING`.

Boundary: finite deterministic controlled environment only. This is not a Lean snapshotting result, LLM result, universal replay-tax law, or claim of first persistence/caching.

## Frontier claims

### C1 — Controlled structural support placement
Required: F1 positive terminal.
Current: `PROSPECTIVE_NOT_CLAIMED`.

Allowed if earned:
> The same task-relevant structure can occupy different support loci, producing distinct non-dominated resource configurations under fixed task information.

### C2 — Certified state compaction accessibility
Required: F2 learner terminal `CERTIFIED_STATE_COMPACTION_ACCESSIBILITY_SUPPORTED`.
Current: `CERTIFICATE_SUPPORTED__LEARNER_PENDING`.

### C3 — Compile-once reasoning amortization
Required: F3 positive terminal and observed query-count crossover.
Current: `PROSPECTIVE_NOT_CLAIMED`.

### C4 — Observation-time scaling
Required: F4 positive terminal with observation/computation mechanistic controls and adaptive frontier dominance.
Current: `PROSPECTIVE_NOT_CLAIMED`.

### C5 — Representation reduces retrieval resource
Required: F5 controlled positive plus downstream solver effect.
Current: `PROSPECTIVE_NOT_CLAIMED`.

### C6 — Persistence reduces replay scaling
Required: F6 controlled positive with exact branch correctness.
Current: `SUPPORTED_CONTROLLED`.

Allowed claim:
> In the frozen finite branch-search environment, persisting a task-sufficient state eliminates repeated prefix reconstruction without changing branch outcomes, producing an exact replay-operation tax that grows with history length and branch count and reaches 9.57x at the largest preregistered cell.

### C7 — Cross-domain structural support frontier
Required:
- at least two real domains of different classes;
- at least three support loci across programme;
- domain-stratified positive direction;
- native resource accounting;
- hostile review clear.

Current: `BLOCKED_ON_REAL_DOMAIN_EXECUTION`.

### C8 — System-level support law
Required:
- C7;
- prospectively frozen functional form or nonparametric law criterion;
- confirmatory domains not used to select the law;
- nearest-work refresh.

Current: `NOT_AUTHORIZED`.

## Explicitly forbidden current claims

- `Intelligence can always be moved out of weights.`
- `Representation replaces scale.`
- `Certified compaction is lossless in open-world agents.`
- `Retrieval cost is caused by bad representation.`
- `Lean proof search benefits from ORION native state.`
- `The frontier is universal or conserved.`
- `ORION invented proof-state snapshotting.`

## Promotion rule

Every claim promotion must cite an immutable result receipt and must leave this ledger's earlier negative/pending states visible in history. No outcome may be promoted solely from manuscript prose or PR description.
