# ORION-P3 Public-Reference Atlas — zero-budget build path

**Protocol:** `P3.public-reference-mapping.v1`  
**Goal:** produce a real, externally grounded mapping atlas without paying for a new annotation campaign.

## Inputs

The source registry freezes four reusable upstream authorities:

| source | use | gold authority |
|---|---|---|
| MUSE | expert source spans, conceptual coreference, problem/solution/rationale relations | `UPSTREAM_EXPERT` |
| SciSchema | expert multidisciplinary process/measurement schemas and conditions | `UPSTREAM_EXPERT` |
| SciFact | expert SUPPORT/CONTRADICT labels and evidence sentence indices | `UPSTREAM_EXPERT` |
| SciER | manual full-text scientific entity/relation annotations | `UPSTREAM_HUMAN` |

Raw text is not copied by default. Cases bind upstream revision, locator and content hash.

## Build stages

### A. Candidate extraction

Adapters may read upstream datasets and emit **candidate** cases. Candidate extraction is allowed to be permissive because it carries no scientific authority by itself.

Examples:

- MUSE conceptual-coreference edges → candidate different-name/same-referent pairs;
- SciFact SUPPORT/CONTRADICT evidence → candidate aligned/contradictory claim pairs;
- SciSchema field/quantity definitions → candidate measurement/context mapping cases;
- SciER entity/relation records → candidate referent/relation cases.

### B. Authority projection

Each candidate is converted into ORION coordinates only when the relation is directly represented by the upstream annotation or is a deterministic consequence of a frozen standard.

Every scored expected relation records:

- authority kind;
- upstream evidence locator(s);
- deterministic derivation rule, if any;
- input hashes.

Anything else stays `UNRESOLVED`.

### C. Deterministic sampling

The publication sample must be selected before running ORION or baselines.

Target when upstream coverage permits:

- 32 cases;
- at least 3 source disciplines;
- balance across positive merge and obstruction/non-merge outcomes;
- round-robin sampling across every available authoritative upstream pool so no pool is silently preferred;
- deterministic lexical/file ordering recorded by the builder (no outcome-dependent selector).

If the available authoritative pool cannot satisfy those conditions, the build returns `CANNOT_CHECK` instead of weakening the rule.

### D. Freeze

The build emits:

- `cases.jsonl`;
- `BUILD_REPORT.json` with the case-set SHA-256, coverage, authority kinds and explicit blockers;
- the separately versioned `PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json` fixes upstream revisions/licence modes.

The final execution-freeze step may wrap these in a run manifest, but it must not alter case selection.

The publication run must use the exact frozen hashes.

### E. Evaluation

The initial zero-budget study is deterministic:

- full ORION semantic comparator (`compare_meaning` / `bridge_compatible`);
- flat-predicate canonicalization baseline;
- exact-coordinate conservative baseline;
- coordinate ablations as separately implemented.

No provider key or GPU is needed for the primary mapping-layer run.

### F. Statistics and artifacts

Report:

- relation accuracy;
- false-merge rate;
- false-split rate;
- abstention rate;
- Wilson intervals for standalone rates;
- paired case-level differences;
- discipline/upstream strata;
- coordinate-ablation deltas.

Any end-to-end raw-text/model result remains a secondary `CANNOT_CHECK` lane unless later resources are available.

## Failure rules

The build fails closed when:

- an upstream revision is not pinned;
- a required record changed hash;
- a case uses LLM/proxy/simulated gold;
- source licensing cannot support the chosen storage mode;
- the sample cannot meet frozen coverage;
- output selection depends on system predictions.

## What the owner must provide

Nothing beyond the repository and ordinary GitHub Actions/local Python for this route.

A future stronger end-to-end paper may still commission experts, but this public-reference mapping study is designed not to require that budget.
