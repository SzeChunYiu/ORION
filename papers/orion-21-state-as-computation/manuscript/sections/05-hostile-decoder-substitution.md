# Hostile decoder substitution

The central alternative explanation is that the universal representation is penalized only because the downstream decoder has the wrong inductive bias. If so, stronger decoder-side search should buy back the compilation advantage. ORION-21 treats that prediction as a mechanism test.

## P11D sparse decoder — permanent negative

P11D preregistered a strong hostile gate: an L1 sparse universal decoder should still leave at least a 4× sample-threshold advantage for compiled state in both high-dimensional cells. It did not.

| cell `(d,s,r)` | sparse `n` at 0.95 | comp. `n` at 0.95 | ratio | comp. - sparse at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | 128 | 64 | 2× | +0.2903 |
| (19,3,7) | 256 | 64 | 4× | +0.3840 |

The terminal `P11D_SPARSE_DECODER_GAP_NOT_MET` remains permanently negative. P11D also exposed an unseeded `liblinear` replay defect; that defect is retained.

## P11E deterministic sparse replication

P11E uses a fresh data seed and explicit estimator seeds. It reproduces thresholds 128/64 and 256/64 with low-sample compiled-minus-sparse advantages +0.2912 and +0.3307. Two fresh executions produce one canonical SHA-256. Its two hexadecimal halves, concatenated without a separator, are:

`1097d94bef1132d4dfa5d01176a9fcfc`

and

`febc46de8113e7cb2e57da1e579a4536`.

## P11C/P11F/P11G nonlinear sequence

P11C's first execution attempt exceeded the available window; after an amendment that vectorized only its parity-bank evaluation, `P11C_EXECUTION_RECEIPT_V1.md` records the frozen protocol run to completion twice at `P11C_STRONGER_DECODER_GAP_SUPPORTED`, with its pooled ≥4× gate passing at exactly the boundary and a twenty-seed sweep putting that boundary at 11 of 20 draws. It settles nothing and carries no claim authority; what it does establish is that its pooled combination rule was applied inside its own protocol. P11F produced positive numerical separation but is non-authoritative because hostile review found `n_jobs=-1` violated the frozen otherwise-default tree contract. P11G was frozen separately with `n_jobs=1`, explicit random states, and two fresh subprocess replays in the terminal decision path.

| cell | tree `n` at 0.95 | comp. `n` at 0.95 | tree acc. at `n=1024` | comp. - tree at `n=64` |
|---|---:|---:|---:|---:|
| (17,4,5) | `NOT_REACHED` | 64 | 0.8248 | +0.4624 |
| (19,3,7) | `NOT_REACHED` | 64 | 0.7828 | +0.3942 |

P11G's terminal is `P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED`; both fresh scientific payloads have one SHA-256. Its two hexadecimal halves, concatenated without a separator, are:

`a2b0c33ce3c39e54ca1aa400a2b7d52d`

and

`019fc4503f6cd5eb726c7b8bbe79a7cc`.

## What P11G's terminal is a statement about

The programme registered three universal-state arms in P11C — `UNIVERSAL_L2`, `UNIVERSAL_L1` and `UNIVERSAL_EXTRA_TREES` — and P11G's receipt publishes curves for one. Replaying P11G's own frozen data stream with only the decoder swapped, and reading P11G's own four scientific gates on each arm:

| universal arm | 0.95 thresholds (censored at 256) | P11G gate result |
|---|---|---|
| `UNIVERSAL_L2` | ≥256, ≥256 | supported |
| `UNIVERSAL_L1` | **128**, ≥256 | not met |
| `UNIVERSAL_EXTRA_TREES` (reported) | ≥256, ≥256 | supported |

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
## P11H pooled successor — the survival was not predetermined, and it did not hold

The arm-scoping above is the smaller finding. The larger one, from `orion.study.p11.attack_audit`, is that all four of P11G's scientific gates hold in **every world its own freeze admits**, so its survival was fixed before its seed was drawn. P11H re-asks the question under a protocol whose attack can win, editing nothing of P11G.

P11H registers all three universal arms and freezes the best-of-arms rule inside its own positive gate; carries P11G's `0.95` and `0.20` thresholds over unedited; and draws two protected regimes by its fresh seed from a frozen 2×3 ladder of state widths `r ∈ {3, 7}` crossed with complete parity banks of 91, 364 and 969 columns. Before execution, the recorded preflight reports both hypothesis gates `BOTH_OUTCOMES_REACHABLE` — supports `[0.8808, 1.0000]` against `0.95` and `[0.0000, 0.2482]` against `0.20` — and two reachable terminals over 15 admissible draws, 3 of which clear every gate.

The seed drew `(14,2,3)` and `(19,3,3)`. Every precondition held, replay was byte-identical, and both hypothesis gates failed: `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`.

| rung | universal bank | pooled 0.95 threshold | `delta64` |
|---|---:|---:|---:|
| (14,2,3) | 91 | **128** | +0.1482 |
| (14,3,3) | 364 | **128** | +0.0992 |
| (19,3,3) | 969 | **128** | +0.0506 |
| (14,2,7) | 91 | ≥256 | +0.2350 |
| (14,3,7) | 364 | ≥256 | +0.3172 |
| (19,3,7) | 969 | ≥256 | +0.3175 |

The pool reaches the target by `n=128` at every `r=3` rung and at no `r=7` rung, while the complete bank moves 91 → 969 columns inside each half without changing a verdict. The advantage is governed by the width of the compiled state, not by the size of the universal representation.

And the decomposition sharpens in the opposite direction: at the drawn regimes the decoder-family half of the `n=64` gap is exactly `+0.0000`, so **100%** of it is the change of state — against 86.7% and 55.4% above — and the gap is still only `+0.0506`. Attribution and magnitude are different questions.

Three of the fifteen admissible draws would have printed the positive terminal and the seed did not draw one, so the `r=7` rungs carry no terminal and no claim authority. The `r=5` boundary was excluded before execution for verdict instability across three preflight seeds, in both directions, and remains open.

## P11I wide high-width replication

P11I prospectively freezes the narrower regime P11H located rather than
relabeling P11H. It evaluates the complete cross of three fresh execution seeds
and three fixed bank-geometry strata at `r=7`, with a matched `r=3` control in
every cell. The independent random unit is the execution seed (`n=3`); geometry
is a fixed within-seed stratum and five query repeats are technical repeats
within each cell. One failed cell still defeats the conjunction.

All nine high-width units pass. Compiled accuracy at `n=64` ranges
0.9690–0.9981; the pooled attack's best accuracy below `n=256` ranges
0.8489–0.9421 against the strict `<0.95` gate; and `delta64` ranges
+0.2463–+0.3543 against `>=+0.20`. The same pooled attack reaches 1.0000 in all
nine matched `r=3` controls. Two fresh subprocess payloads are byte-identical at
SHA-256 `b50ace30…e0ce`.

The P11I terminal is
`P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL`. It licenses a
width-conditioned result only: the pooled attack wins in the narrow regime and
the compiled-state advantage replicates in the registered high-width regime.
A fresh two-subprocess revalidation under
`P11I_REPLICATION_UNIT_AMENDMENT_V1_1.md` reproduces every cell byte-identically
while recording `n=3`, not nine. P11D and P11H remain adverse historical results.

## Ten-responsibility digits boundary

The separately frozen query-family phase study asks whether the learned
16-of-64 compiler is quality-supported across ten digit responsibilities. With
the registered inclusive tolerance of `-0.02`, support is **3/10** under LINEAR
access and **5/10** under each of RBF and KNN, below the preregistered **8/10**
family gate. Its terminal is `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET`; the
thresholds were not retuned after observing the result.

Both implementations nevertheless agree on every registered resource row:
compiled state is no larger than the 64-float universal state exactly when
`U<=4`, the LINEAR break-even horizon grows from 1,917 to 19,169 service steps,
and a newly arriving responsibility has positive specialization cost. This is
a negative boundary on family-scale quality, not a positive rescue by resource
accounting. Under this frozen digits/resource model, retain raw state unless
the family is small, every member is individually compile-tolerant, and the
service horizon exceeds the charged break-even.
