# Five-paper nearest-work / falsifier saturation ledger

Saturation here means **bounded stability of the current candidate claims under declared heterogeneous challenges**, never proof that all relevant work has been found or that the papers are externally novel.

## Frozen nearest-work round

Starting framework for the nearest-work programme: `SzeChunYiu/ORION@c7376b952b2a33505e6fbc6644f6c9772c156190`.

### Challenge families executed

1. exact nearest-work / named autonomous-research systems;
2. function-only and parent-discipline search;
3. historical precursor search (systems engineering, literature-based discovery, capture-recapture, data integration);
4. implementation analogues (RAG, schema matching, program search, self-improving coding systems);
5. adversarial "already solved elsewhere" comparison;
6. benchmark/evaluation literature to identify what would falsify the ORION delta;
7. local known-world/hostile falsifier execution for all five papers.

### Material changes during the nearest-work round

- Paper I dropped autonomous/iterative science, multi-agent evolution, tree search and structured-world-model claims from the novelty boundary.
- Paper II became a separate paper because open-world discovery has its own nearest work, metrics and falsifiers.
- Paper III narrowed from cross-domain synthesis to projection-preserving semantic/identity/context/measurement alignment, obstruction and recoverability.
- Paper IV narrowed from provenance/fact checking to non-escalating scientific authority with checker/evaluator governance.
- Paper V dropped self-editing/evolutionary-agent novelty claims and narrowed to failure-governed, cause-attributed, independently assured method evolution.

## Flagship falsifier V1

Local suite commit: `8a8a7feed588363f8e2cd820d3399a33b7af3074`  
CI run: `31933432314` — success.

The falsifier round was **not flat** in formulation/mechanic space because it changed ORION:

- Paper I negative control exposed false local reframing of pure `EVIDENCE`/`EXECUTION` failures; the local reframe license was narrowed.
- Paper III exact atlas worlds exposed an implicit source-text → scientific-meaning boundary; `ScientificMeaningProjection.v1` was added.
- Paper V nearest-work/falsifier work absorbed ADIAS-style persistent issue state as `DevelopmentIssue.v1`; persistent issue identity is removed from the ORION novelty boundary.

These are retained as evidence that a falsifier can reconstruct the framework rather than merely produce a score.

## Current local flatness statement

After the above repairs, the registered deterministic local suite reports PASS for:

- Paper I hidden-domain / hidden-representation / missing-evidence / execution negative controls;
- Paper II complete-gold retrieval + route/coverage refusal attacks;
- Paper III semantic identity/measurement/modality/attribution/bridge/recoverability attacks;
- Paper IV evidence substitution / weak checker / same-lane / chronology attacks;
- Paper V recurrence-not-cause / discriminator / negative intervention / fresh-transfer / reward-hacking attacks.

This is a **local falsifier result only**. It licenses neither open-world completeness nor publication novelty.

## External routes deliberately still open

### Paper I
- fresh hidden-representation/search-universe tasks;
- matched static-workflow and agent/tree-search baselines;
- responsibility/domain labels hidden from the candidate;
- resource-matched root success and unnecessary-reframe rates.

### Paper II
- ResearchArena/AutoResearchBench/MetaSyn-compatible complete-gold runs;
- matched lexical and one-pass baselines;
- frozen provider/search trajectories;
- stage-attributed recall/screening errors.

### Paper III
- real cases spanning at least three domains;
- source-projection and representation/identity mapping gold;
- long-context, RAG/translation and flat-schema baselines;
- semantic-coordinate ablations.

### Paper IV
- source-aware claim/attribution benchmark;
- search-time contamination audit;
- evaluator locking and held-out access telemetry;
- matched nearest-work verifier baselines;
- false-authority-promotion tradeoff. Issue #59 owns this programme.

### Paper V
- matched direct-self-edit and ADAS/DGM-style baselines;
- prospectively hidden failure causes;
- fresh task/domain/model transfer;
- evaluator chronology/access telemetry;
- negative-history/harmful-transfer accounting.

## Current bounded terminal

```
LOCAL_FLAGSHIP_FALSIFIERS = PASS
PAPER_I_EXTERNAL = CANNOT_CHECK
PAPER_II_EXTERNAL = CANNOT_CHECK
PAPER_III_EXTERNAL = CANNOT_CHECK
PAPER_IV_EXTERNAL = CANNOT_CHECK
PAPER_V_EXTERNAL = CANNOT_CHECK
PUBLICATION_READY = false
```

Any new nearest work, external benchmark result, representation change or failure class reopens the affected paper claim.
