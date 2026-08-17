# SAGE short-form hit@50 BASELINE_AHEAD diagnostic

## Hypothesis

**Candidate-pool-size confound**: The governed multiroute system splits its 3 requests per task across OpenAIRE, DBLP, and Crossref backends. Many routes return EMPTY or SERVICE_ERROR responses, yielding smaller candidate pools than the single backend system, which concentrates all 3 requests on Crossref and consistently receives more results per task.

## Hypothesis Status

**CONFIRMED PARTIAL** — The pool-size confound explains a significant portion of the BASELINE_AHEAD gap, but not all of it. Even when restricted to tasks where both systems have >=50 candidates, the single backend maintains a 1-hit advantage.

## Evidence

### Full sample (385 tasks)

| System | Mean pool | Median pool | Min | Max | Tasks <50 | Tasks >=50 |
|--------|-----------|--------------|-----|-----|-----------|-------------|
| sage_governed_multiroute | 55.84 | 49 | 20 | 100 | **205 (53%)** | 180 |
| sage_single_backend | 126.66 | 130 | 71 | 149 | **0** | 385 |

**Key observation**: 53% of governed tasks have candidate pools <50, meaning hit@50 is mechanically capped for those tasks regardless of retrieval quality.

### Restricted sample (180 tasks where BOTH pools >=50)

#### Strict hit@50
- sage_governed_multiroute: 3/180 (0.016667)
- sage_single_backend: 4/180 (0.022222)
- Single backend advantage: **1 hit** (margin narrows from 12 hits at full 385)

#### Relaxed hit@50
- sage_governed_multiroute: 3/180 (0.016667)
- sage_single_backend: 4/180 (0.022222)
- Single backend advantage: **1 hit**

## Interpretation

The BASELINE_AHEAD verdict at hit@50 is partly an artifact of unequal candidate pools. The governed multiroute's smaller pools (due to EMPTY/SERVICE_ERROR responses across multiple backends) mechanically cap its performance at fixed-k cutoffs like hit@50.

However, the 1-hit advantage that persists in the restricted analysis suggests a genuine retrieval quality difference, not purely a pool-size confound. This may reflect:
- Crossref's index quality vs. OpenAIRE/DBLP for this task type
- Deduplication effects across multiple backends
- Ranking depth differences

## Recommendation

Future head-to-head comparisons should either:
1. **Equalize candidate pools** before scoring (sample down to the smaller pool)
2. **Use ranking metrics insensitive to absolute pool size** (MRR, precision-recall curves, rather than fixed-k cutoffs)
3. **Report pool-size distributions** alongside any fixed-k comparison

## Method

- Used landed evidence at `papers/paper-02-open-world-scientific-discovery/evidence/offline_results/SAGE_SHORTFORM_EXTERNAL_V1/`
- Analyzed candidate pool sizes from `out/candidates_*.jsonl`
- Applied strict/relaxed matchers per `run_sage_shortform.py`
- Restricted to tasks where both systems had >=50 candidates
- Recomputed hit@50 on the restricted task set

## Generated

2026-08-17 (post-PR #237)
Analysis by Claude Opus 5 (1M context)
