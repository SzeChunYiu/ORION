# ORION Frontier Hostile Review Matrix V1

Status: **FROZEN BEFORE FRONTIER OUTCOMES**

## Review principle

A positive mean score is insufficient. Every lane must survive the specific alternative explanation it is designed to rule out.

| Attack | Failure mode | Required defense | If defense fails |
|---|---|---|---|
| Extra-information attack | structured/support arm silently receives answer-bearing facts | exact fact-set/equivalence receipt or explicit information-added label | no same-information claim |
| Token-length attack | better arm is simply shorter/easier to fit | tokenizer/native-size accounting; pad/control where appropriate | length-confounded only |
| Compiler-answer leakage | compiled state encodes downstream answer/query identity | compile before query reveal; query-blind receipt | F3 invalid |
| Cost laundering | tool/retrieval/search calls omitted from budget | separate native resource ledger | no resource substitution claim |
| Hidden model change | support arm changes checkpoint/runtime | exact model/runtime digest | invalid comparison |
| Domain-label shortcut | state exposes dataset/domain identity | attacker classifier; opaque identifiers | domain-generalization claim blocked |
| Surface familiarity | known field names/symbols cue model | opaque renaming / order controls | canonical-schema-only claim |
| Heuristic summary rescue | lossy summary happens to work on sampled queries | exhaustive/frozen future-query certificate for `CERTIFIED` label | empirical compaction only |
| Certificate undercoverage | sufficiency verified only on favorable actions/horizon | declare complete action/horizon class before outcome | narrow certificate to checked class |
| Retrieval contamination | ground-truth premise/file identity leaks into query/index | frozen index/query construction; leakage scan | retrieval experiment invalid |
| Search-budget mismatch | one arm gets more verifier/compiler opportunities | matched node/tool-call caps | prover/search claim blocked |
| Persistence hidden refresh | cached state silently recomputed from full history | immutable snapshot digest and refresh counter | no replay-tax claim |
| Post-hoc cost weights | scalar cost model chosen to favor result | freeze weights before outcomes or report Pareto frontier only | scalar claim forbidden |
| Pooled-only success | effect comes from one domain/module | domain/module-stratified results and worst-block report | cross-domain claim blocked |
| Model-family cherry-pick | only favorable size/family reported | preregistered family/size set, all outcomes retained | replication only |
| Negative suppression | failed arm omitted | immutable result ledger | programme terminal blocked |
| Existing-work overclaim | nearest work already owns mechanism | explicit donor subtraction | narrow/retire claim |

## Lane-specific stop rules

### F1 Structural Support Frontier
Stop at `CONTROLLED_SUPPORT_PLACEMENT_ONLY` unless at least three support loci and two qualitatively distinct domains show a nontrivial frontier shift. Never infer a universal conservation law from one synthetic generator.

### F2 Certified State Compaction
`CERTIFIED` requires zero equivalence violations over the complete frozen finite action/query class or a formal proof accepted by the theory reviewer. Otherwise use `EMPIRICALLY_COMPACT`.

A smaller state that discards task-irrelevant variables may be called task-sufficient only for the declared task/horizon, never globally lossless.

### F3 Compile Once, Reason Many
The compiler must run before downstream query identity is revealed. The compiled state must support at least `m>=8` prospectively generated downstream queries per world/session. If state construction is refreshed per query, the claim collapses to ordinary prompting/tool use.

Primary success requires a quality-noninferior amortized crossover against repeated direct reasoning under native cost accounting. If only accuracy improves without cost crossover, report representation benefit only.

### F4 Observation-Time Scaling
Observation actions must add declared information; thinking actions must not. If the agent can infer hidden coordinates from prompt artifacts, invalidate the world. Primary claim requires a region where observation budget dominates extra thinking at matched cost or shifts the joint Pareto frontier.

### F5 Representation–Retrieval Duality
Same retrieval corpus and index snapshot across representation arms. If the structured query contains ground-truth document/premise identifiers unavailable to the raw arm, label it information-added and do not claim representation tax.

Primary promotion requires downstream solve/evidence quality, not retrieval metric alone.

### F6 Persistence–Reconstruction Tax
Persistence speedups that arise only from engineering cache reuse are credited to prior systems work. ORION's stronger claim requires a task-sufficient-state analysis plus cross-domain resource scaling. Quality must remain noninferior under matched action/search policy.

## Cross-programme contamination rules

1. Merged P9 and P10 results are immutable prior evidence.
2. #618 LLM/native-Lean outcomes cannot alter the frozen frontier thresholds after this file's commit.
3. Frontier controlled benchmarks must not tune generators to mimic favorable #618 outcomes.
4. A later #618 positive may instantiate a frontier lane but cannot retroactively become preregistration evidence.
5. A later #618 negative remains visible and may falsify a frontier generalization.

## Promotion authority

A result can enter a manuscript-level claim only when all four reviewer roles T/S/F/H have no unresolved material objection and the result ledger identifies every failed/negative secondary endpoint.
