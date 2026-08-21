# ORION-QN S1A classical query-ceiling amendment v1

Status: **PRE-OUTCOME FAIRNESS CORRECTION / ADDITIVE AMENDMENT**  
Programme: `SzeChunYiu/ORION#734`

Parents retained unchanged:
- `S1A_ACCESS_MODEL_AMENDMENT_V1.md`
- `S1A_BENCHMARK_DEPENDENCE_AMENDMENT_V1.md`

This amendment was frozen before any result-bearing S1A outcome.

## 1. Fairness defect

The first hidden-uniform comparator required the classical route to have found and predicate-verified the marked item within `K` oracle queries, giving success `K/N`.

That is not the strongest classical query-model comparator when quantum output correctness is scored externally after the query algorithm terminates.

After `K` distinct failed classical queries, the algorithm knows the marked item is among the `N-K` unqueried locations and may output one of them as a final **free guess**. The evaluator can score that output exactly as it scores the quantum measurement outcome. Any later scientific/predicate verification is a separate resource coordinate for both routes.

Therefore the optimal classical success ceiling after `K` distinct oracle queries is:

```text
p_c(K) = K/N + (N-K)/N * 1/(N-K)
       = (K+1)/N
```

for `0 <= K < N`, with success 1 at `K=N-1` already because only one location remains unqueried.

## 2. Corrected matching budget

For quantum single-run analytic success `p_q`, the minimum classical query budget that can match or exceed it is:

```text
K_match = max(0, ceil(p_q * N) - 1)
```

capped at `N-1`.

The expected number of actual predicate queries used by a fixed no-replacement query order that stops when it finds the marked item or reaches `K_match` remains:

```text
E_C = K_match - K_match*(K_match-1)/(2*N)
```

The final guess, when needed, is not an oracle query.

## 3. External verification separation

S1A must now record:

```text
classical_free_final_guess_allowed = true
external_output_verification_is_separate_resource = true
```

The query-only terminal compares quantum coherent-oracle query budget `r` against the corrected classical `K_match` and `E_C`.

The harness's candidate predicate checks remain execution/verification telemetry and do not redefine either query complexity model.

## 4. P4 obligations

Independent reconstruction must use the corrected `(K+1)/N` classical ceiling and reject the prior `K/N` rule.

For the current n=3..10 ladder, this changes the matching budget from `N` to `N-1` while preserving a large gap versus the frozen Grover query counts.

## 5. Scientific consequence

This amendment makes the classical comparator strictly stronger. It does not weaken any quantum success requirement and was introduced before protected outcome access.

No physical or end-to-end advantage is licensed.
