# P11B No-Answer-Laundering Query Compiler — Confirmatory Protocol V1

Status: **FROZEN AFTER SEPARATE PILOT, BEFORE P11B CONFIRMATORY OUTCOMES**
Frozen: 2026-08-20

## Motivation

P11 direct specialization uses a compiler that can emit the active parity itself. That is valid resource transfer, but a reviewer can reasonably argue that the compiler is solving the queried subproblem. P11B removes that ambiguity.

The compiler is forbidden to emit the final label or any scalar deterministically equal to it. It may expose only the latent component features named by the query. A separate learned downstream classifier must still combine those components to decide the label.

## Pilot disclosure

A non-authorizing pilot used `(d,s,r)=(14,3,5),(16,3,5),(16,4,5),(18,3,7)` at n=256. It suggested raw linear near chance, compiled component state near perfect, and a substantial universal-bank nuisance penalty. No pilot cell or seed is reused below.

## Fresh confirmatory cells

Each query Q is a set of r distinct size-s parity basis functions. For input x, let `z_j=f_{q_j}(x)` for q_j in Q. The target is

`Y = 1[sum_{j=1}^r z_j > 0]`.

r is odd, so ties are impossible.

Frozen cells:
- `(d=15,s=3,r=5)`, universal basis size `455`;
- `(d=17,s=3,r=5)`, universal basis size `680`;
- `(d=17,s=4,r=5)`, universal basis size `2380`;
- `(d=19,s=3,r=7)`, universal basis size `969`.

Master seed: `914337`.

Per cell:
- 10 query sets sampled without replacement from the basis family;
- train sizes `64,128,256,512,1024,2048`;
- fixed test set n=`8192`.

## Arms

1. `RAW_LINEAR`: raw d-dimensional x.
2. `UNIVERSAL_BANK`: all size-s parity basis coordinates.
3. `QUERY_COMPILED_COMPONENTS`: only the r active parity coordinates named by Q.

The active r coordinates are byte-identical between universal and compiled arms. The compiler does not emit Y, the sign/majority, model logits, or any label-derived metadata.

## Fixed learner

`LogisticRegression(C=1.0, solver='liblinear', max_iter=1000)` with no tuning.

## Protected positive gates

`P11B_QUERY_COMPONENT_COMPILATION_SUPPORTED` requires ALL:

1. generator verifies the target is computed from the r active components after representation construction;
2. no compiled feature equals Y or `2Y-1` on the protected test population for every query;
3. compiled mean accuracy >=0.995 in every cell by n=128 and remains >=0.995 thereafter;
4. raw mean accuracy <=0.60 at n=2048 in every cell;
5. for cells with universal basis size >=600, compiled-minus-universal mean accuracy at n=64 >=+0.20;
6. for those cells, the universal/compiled 0.95 sample-threshold ratio >=8, with not-reached counted as strictly beyond the maximum tested ratio;
7. deterministic canonical replay byte-identical;
8. query selection and examples are generated independently of learner outcomes.

Failure terminal: `P11B_QUERY_COMPONENT_COMPILATION_GATE_NOT_MET`.

## Strongest allowed claim

A positive result may support:

> In a frozen multi-component query family, query-conditioned state compilation can remove hundreds to thousands of irrelevant but potentially useful universal coordinates while leaving a nontrivial downstream decision to the same learner; this materially reduces sample burden without answer laundering.

It does not establish a universal nonlinear lower bound, LLM result, or optimal compiler.
