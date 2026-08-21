# Frontier F1 — Structural Support Frontier Protocol V1

Status: **FROZEN BEFORE F1 OUTCOMES**

Frozen: 2026-08-20

## 1. Question

For a fixed task and fixed latent information, what changes when the useful structure is placed in a different part of the reasoning system?

The support loci are:

- generic model capacity;
- explicit representation;
- architecture/inductive bias;
- exact tool;
- compiled/persistent state;
- retrieval support;
- constrained search/verifier support.

The primary object is the non-dominated resource frontier, not a single accuracy leaderboard.

## 2. Controlled base family

Use the relational alignment family already mathematically understood by ORION, but generate fresh seeds/worlds not used by #618 outcomes.

For odd `k in {9,17,33}`:

- `x,c in {-1,+1}^k` iid uniform;
- relational coordinate `r=x*c` elementwise;
- target `Y=1[sum_i r_i > 0]`.

The flat `(x,c)` and relational `(x,r)` forms are bijectively information-equivalent.

The F1 controlled experiment may reuse *the mathematical family* but must use new seeds and a new support-placement question. Existing #618 representation/architecture results are prior evidence, not F1 outcomes.

## 3. Support placements

### G — GENERIC_FLAT
Input `(x,c)`. Generic degree-2 bilinear feature family contains all `x_i*c_j`; learner must discover the diagonal structure.

### R — EXPLICIT_RELATION
Input `(x,r)`. Fixed linear learner.

### A — DIAGONAL_ARCHITECTURE
Input `(x,c)`, but architecture exposes only diagonal products `x_i*c_i` to the fixed head. This arm is expected to be functionally aligned with R and serves as a structure-location control.

### T — EXACT_TOOL
Input `(x,c)` to a fixed linear head, with one counted exact tool call that returns `r=x*c`. Model/head weights are identical to R after tool output.

### P — PERSISTED_STATE
A world/session contains one `(x,c)` pair reused for multiple downstream signed-majority queries. Compute `r` once, persist it, and reuse the frozen state across queries. State-construction cost is counted once.

### K — RETRIEVAL_SUPPORT
In the multi-query extension, each `r_i` is stored as a content-addressed relation record. The raw query identifies the needed relation subset by opaque entity pairs; a structured query exposes the relation role but not its value. Retrieval calls/candidate depth are counted. This arm belongs to F1 only after the F5 exact query-equivalence checker exists.

### V — SEARCH/VERIFIER_SUPPORT
Optional controlled search task where the flat model proposes candidate relation assignments and a frozen verifier rejects inconsistent candidates. Node/verifier-call budgets are counted. This arm is secondary until a clean search generator is frozen.

## 4. Native resource vector

For every arm report:

- trainable parameter count;
- exposed feature count;
- training examples;
- input bytes/features;
- exact tool calls;
- persisted state bytes and construction operations;
- retrieval candidate depth/calls;
- search nodes/verifier calls;
- inference operations/wall time.

No universal scalar cost conversion is primary.

## 5. Target qualities

`q in {0.80,0.90,0.95}` protected accuracy.

For each native resource `a` where a monotone threshold is meaningful, estimate `a*(q)` over the frozen grid and report `ESR_a` between support placements.

## 6. Primary frontier test

F1 earns

`CONTROLLED_STRUCTURAL_SUPPORT_FRONTIER_SUPPORTED`

only if:

1. fresh-seed R and A reach >=0.95 at all three k values;
2. R and A predictions differ on <=0.1% of protected cases when their equivalent feature values are supplied;
3. T matches R prediction-for-prediction after the exact tool output, with exactly one counted tool call per independent world state;
4. G pays a strictly larger observed sample or feature threshold than R at `k>=17` for q=0.90;
5. in the multi-query P arm, amortized state-construction operations per query decrease monotonically with reuse count `m in {1,2,4,8,16,32}`;
6. at least three support loci occupy distinct non-dominated points in the native resource space at one q>=0.90;
7. no same-information arm adds answer-bearing facts.

This is a **controlled** support frontier only. It cannot authorize a real-LLM/system-level law.

## 7. Real-domain promotion

A system-level support-frontier claim requires independent replication in at least two domains chosen before their outcomes:

1. formal Lean proving/retrieval/search;
2. an agent/code/search domain;
3. merged P9 procedural tasks may be used as an additional domain but not as the sole real-domain evidence.

Each domain may instantiate only a subset of support loci, but at least three loci total must survive across the programme.

## 8. Attribution rule

When a support arm improves performance, report the gain as belonging to the complete system configuration.

Examples:

- tool-assisted model success is not raw model capability;
- retrieval-assisted proof success is not premise-free theorem-prover capability;
- persistent-state speedup is not model inference speedup;
- representation improvement is not a parameter-count change.

## 9. Strongest allowed claim

If controlled + real-domain promotion succeeds:

> Reasoning quality lies on a structural-support frontier: for fixed task information, useful structure can be supplied at different system loci, and moving it outside generic model capacity shifts the model/compute/retrieval/search resources required to reach a fixed quality.

Forbidden:

- `intelligence is conserved`;
- `weights do not matter`;
- `all support loci are interchangeable`;
- universal cost exchange rates without prospective multi-domain evidence.
