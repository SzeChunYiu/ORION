# Hostile decoder substitution

The central alternative explanation is that the universal representation is penalized only because the downstream decoder has the wrong inductive bias. If so, stronger decoder-side search should buy back the compilation advantage. P11 treats that prediction as a mechanism test.

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

P11C's first execution attempt exceeded the available window; after an amendment that vectorized only its parity-bank evaluation, `P11C_EXECUTION_RECEIPT_V1.md` records the frozen protocol run to completion twice at `P11C_STRONGER_DECODER_GAP_SUPPORTED`, with its pooled ≥4× gate passing at exactly the boundary and a twenty-seed sweep putting that boundary at 11 of 20 draws. It settles nothing and carries no claim authority; what it does establish is that its pooled combination rule was applied inside its own protocol. P11F produced positive numerical separation but is non-authoritative because hostile review found `n_jobs=-1` violated the frozen otherwise-default tree contract. P11G was frozen separately with `n_jobs=1`, explicit random states, and two fresh subprocess replays in the terminal decision path.

| cell | deterministic tree universal `n` at 0.95 | compiled `n` at 0.95 | tree accuracy at `n=1024` | compiled - tree at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | `NOT_REACHED` | 64 | 0.8248 | +0.4624 |
| (19,3,7) | `NOT_REACHED` | 64 | 0.7828 | +0.3942 |

P11G's terminal is `P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED`; both fresh scientific payloads have SHA-256 `a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`.

## What P11G's terminal is a statement about

The programme registered three universal-state arms in P11C — `UNIVERSAL_L2`, `UNIVERSAL_L1` and `UNIVERSAL_EXTRA_TREES` — and P11G's receipt publishes curves for one. Replaying P11G's own frozen data stream with only the decoder swapped, and reading P11G's own four scientific gates on each arm:

| universal arm | 0.95 threshold per cell, censored at 256 | terminal P11G's own gates print |
|---|---|---|
| `UNIVERSAL_L2` | ≥256, ≥256 | `..._GAP_SUPPORTED` |
| `UNIVERSAL_L1` | **128**, ≥256 | `..._GAP_NOT_MET` |
| `UNIVERSAL_EXTRA_TREES` (reported) | ≥256, ≥256 | `..._GAP_SUPPORTED` |

Two of three comparable pairs change the verdict, so the arm axis is not inert, and the flip is entirely the threshold gate: 128 is not ≥256. This is the same sparse threshold P11D reports as a permanent negative and P11E replicates; what is new is that placing it in P11G's gate, on P11G's own bytes, prints `NOT_MET`. `NOT_REACHED` through `n=1024` is therefore not a stronger reading than 128 — an arm that reaches nothing anywhere gives the same gate reading in every world.

P11G's terminal is retained exactly as frozen and is evidence about the decoder its own claim-authority sentence names. `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` carries the adjudication, including the finding — read off the two freezes — that P11C's pooled combination rule governs P11C and does not bind P11G.

## Decomposing a gap that moves two things at once

P11G compares L2 logistic regression on `r` compiled columns against a 96-tree ensemble on the complete bank. Holding the decoder at ExtraTrees and moving only the representation separates them.

| cell | published gap at `n=64` | decoder-family half | state half | state share |
|---|---:|---:|---:|---:|
| (17,4,5) | +0.4624 | +0.0614 | +0.4010 | 86.7% |
| (19,3,7) | +0.3942 | +0.1757 | +0.2185 | 55.4% |

It cuts both ways and is reported both ways. It narrows the terminal: 13.3% and 44.6% of the published gaps are the change of decoder family, not of state. It supports the placement claim: with the decoder held fixed the state half is the majority in both cells, and being measured at a fixed decoder it is unaffected by which universal arm sits in the gate.

The sequence supports the interpretation that **compilation and decoder inductive bias are alternative locations for structural search**. Stronger downstream structure discovery should shrink the upstream advantage; the sparse negative is therefore part of the mechanism evidence, not an inconvenient result to erase. Each verdict in it is scoped to the arm that produced it.