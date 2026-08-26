# Hostile decoder substitution

The central alternative explanation is that the universal representation is penalized only because the downstream decoder has the wrong inductive bias. If so, stronger decoder-side search should buy back the compilation advantage. ORION-21 treats that prediction as a mechanism test.

## P11D sparse decoder — permanent negative

P11D preregistered a strong hostile gate: an L1 sparse universal decoder should still leave at least a 4× sample-threshold advantage for compiled state in both high-dimensional cells. It did not.

| cell `(d,s,r)` | sparse universal `n` at 0.95 | compiled `n` at 0.95 | ratio | compiled - sparse at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | 128 | 64 | 2× | +0.2903 |
| (19,3,7) | 256 | 64 | 4× | +0.3840 |

The terminal `P11D_SPARSE_DECODER_GAP_NOT_MET` remains permanently negative. P11D also exposed an unseeded `liblinear` replay defect; that defect is retained.

## P11E deterministic sparse replication

P11E uses a fresh data seed and explicit estimator seeds. It reproduces thresholds 128/64 and 256/64 with low-sample compiled-minus-sparse advantages +0.2912 and +0.3307. Two fresh executions produce canonical SHA-256 `1097d94bef1132d4dfa5d01176a9fcfcfebc46de8113e7cb2e57da1e579a4536`.

## P11C/P11F/P11G nonlinear sequence

P11C emitted no authoritative terminal and remains `CANNOT_CHECK`. P11F produced positive numerical separation but is non-authoritative because hostile review found `n_jobs=-1` violated the frozen otherwise-default tree contract. P11G was frozen separately with `n_jobs=1`, explicit random states, and two fresh subprocess replays in the terminal decision path.

| cell | deterministic tree universal `n` at 0.95 | compiled `n` at 0.95 | tree accuracy at `n=1024` | compiled - tree at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | `NOT_REACHED` | 64 | 0.8248 | +0.4624 |
| (19,3,7) | `NOT_REACHED` | 64 | 0.7828 | +0.3942 |

P11G's terminal is `P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED`; both fresh scientific payloads have SHA-256 `a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`.

The sequence supports the interpretation that **compilation and decoder inductive bias are alternative locations for structural search**. Stronger downstream structure discovery should shrink the upstream advantage; the sparse negative is therefore part of the mechanism evidence, not an inconvenient result to erase.