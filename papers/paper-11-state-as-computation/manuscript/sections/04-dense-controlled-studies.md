# Dense controlled studies

The confirmatory experiment compares raw linear input, a fixed universal parity bank, and query-conditioned compiled state over a frozen train-size grid.

| `d` | `s` | universal dims | compiled dims | universal/compiled | compiled `n` at 0.90 | universal `n` at 0.90 |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | 2 | 91 | 1 | 91× | 32 | 128 |
| 16 | 4 | 1820 | 1 | 1820× | 32 | `NOT_REACHED` by 1024 |
| 18 | 3 | 816 | 1 | 816× | 32 | 1024 |
| 20 | 3 | 1140 | 1 | 1140× | 32 | 1024 |

At `n=1024`, compiled accuracy is 1.0 in every cell. Raw linear remains near chance. The result is consistent with a structural-search interpretation: decisive coordinates exist in the universal bank, but a bounded dense decoder must identify them among many irrelevant candidates.

## No-answer-content-leakage control

P11B exposes only the `r` active parity components selected by a query, with `r` in `{5,7}`. The downstream logistic learner must still infer an odd-cardinality majority target; no compiled component equals or negates the final label.

| `d` | `s` | `r` | universal dims | universal `n` at 0.95 | compiled `n` at 0.95 |
|---:|---:|---:|---:|---:|---:|
| 15 | 3 | 5 | 455 | 2048 | 64 |
| 17 | 3 | 5 | 680 | 2048 | 64 |
| 17 | 4 | 5 | 2380 | `NOT_REACHED` by 2048 | 64 |
| 19 | 3 | 7 | 969 | `NOT_REACHED` by 2048 | 64 |

The high-dimensional cells therefore exhibit at least 32× threshold separation under the registered dense decoder without answer-content leakage.