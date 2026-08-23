# P11B No-Answer-Laundering — Confirmatory Result Receipt V1

Terminal: `P11B_QUERY_COMPONENT_COMPILATION_SUPPORTED`

Protocol: `P11B_NO_ANSWER_LAUNDERING_PROTOCOL_V1.md`
Master seed: `914337`
Canonical two-replay SHA-256:

`6f0260d84c5aba236c247960feef837428f2aa7806782c0698bb49073243abf6`

Two full fresh-process canonical executions were byte-identical.

## Protected results

| d | s | active components r | universal dims | compiled dims | universal 0.95 threshold | compiled 0.95 threshold | ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 3 | 5 | 455 | 5 | 2048 | 64 | 32x |
| 17 | 3 | 5 | 680 | 5 | 2048 | 64 | 32x |
| 17 | 4 | 5 | 2380 | 5 | not reached by 2048 | 64 | >32x (sentinel 33x) |
| 19 | 3 | 7 | 969 | 7 | not reached by 2048 | 64 | >32x (sentinel 33x) |

At n=2048:
- `(15,3,5)`: raw `0.50493`, universal `0.99716`, compiled `1.0`;
- `(17,3,5)`: raw `0.50205`, universal `0.96549`, compiled `1.0`;
- `(17,4,5)`: raw `0.49985`, universal `0.76221`, compiled `1.0`;
- `(19,3,7)`: raw `0.50024`, universal `0.87140`, compiled `1.0`.

At n=64, compiled-minus-universal gaps in the three >=600-dimensional cells are approximately:
- `+0.40714` for 680 dims;
- `+0.45847` for 2380 dims;
- `+0.43184` for 969 dims.

## Answer-laundering hostile control

For every protected test query, no individual compiled component is identically equal to the signed final label and none is identically its negation. The representation contains only the r active parity components. The final target is computed as their odd-cardinality majority after representation construction and is learned by the same logistic downstream learner.

Laundering failures: `0`.

## Gate disposition

All frozen gates pass:
- target computed after representation;
- zero answer-equivalent components;
- compiled >=0.995 from n=128 onward in every cell;
- raw <=0.60 at n=2048;
- high-dimensional n=64 compiled-minus-universal >=+0.20;
- high-dimensional universal/compiled 0.95 threshold ratio >=8;
- deterministic canonical replay;
- outcome-independent query/example generation.

## Strongest bounded claim

> In a frozen multi-component query family, query-conditioned state compilation removes hundreds to thousands of irrelevant but potentially useful universal coordinates while leaving a nontrivial downstream majority decision to the same learner; this reduces the observed 95%-accuracy sample threshold by 32x or more in the high-dimensional cells without answer laundering.

This is a controlled linear-model result, not a universal nonlinear lower bound or LLM/agent result.
