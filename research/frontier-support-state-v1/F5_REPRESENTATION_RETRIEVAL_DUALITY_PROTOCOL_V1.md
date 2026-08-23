# Frontier F5 — Representation–Retrieval Duality Protocol V1

Status: **FROZEN BEFORE OUTCOMES**

Frozen: 2026-08-20

## 1. Question

Can better task coordinates substitute for retrieval depth, reranker capacity, or iterative search when the underlying external knowledge corpus is held fixed?

The target claim is not `RAG helps`. It is:

> Some reasoning-intensive retrieval cost may be a representation tax on the query/state supplied to the retriever.

## 2. Resource variables

For frozen corpus/index `D` and representation `R`, vary:

- candidate depth `k in {5,10,20,50,100}`;
- reranker class/scale `S_r`;
- retrieval iterations `j in {1,2,4}`;
- downstream solver/search budget held fixed within each comparison.

Define `k*(q,R)` as the smallest observed candidate depth reaching evidence/solve quality q under the frozen reranker.

Where both thresholds exist,

`RetrievalTax_q(R_flat,R_structured) = log(k*_flat / k*_structured)`.

## 3. Controlled corpus phase

Generate deterministic multi-hop relational corpora. Each world contains:

- 256 atomic fact documents;
- 32 distractor clusters with lexically plausible but semantically irrelevant facts;
- 16 answer-bearing relation chains of lengths 2–4;
- opaque entity aliases independent of train/test split.

For each query create two representations from the exact same query semantics:

### QF — FLAT_QUERY
Canonical natural/linear serialization of entities, constraints, and requested relation.

### QS — STRUCTURED_QUERY
Typed entities, relation slots, constraint roles, and known/unknown coordinates. It may reorganize but not add facts.

An exact fact-set checker must establish semantic identity between QF and QS before retrieval.

## 4. Retrieval arms

Primary classical retrievers:

- BM25;
- TF-IDF cosine;
- frozen small embedding retriever if a reproducible model is available.

Primary reranking conditions:

- no reranker;
- fixed lightweight cross-encoder / lexical structural reranker;
- larger LLM reranker only in a separately frozen runtime amendment.

The index is byte-identical across QF/QS. No structured arm may use a different corpus graph/index unless explicitly labeled an information/structure-added experiment.

## 5. Formal-math phase

After P10 native-state receipts are available, freeze one Mathlib corpus/index and compare query state built from:

- theorem statement only;
- raw native proof-state text;
- canonical typed proof state;
- typed state + dependency coordinates.

Ground-truth evidence is the prospectively frozen premise set / proof-used declarations for eligible theorems. Direct declaration IDs occurring in ground truth must not be injected into a structured query unless they are already visible in the compared raw state.

Primary formal endpoint is downstream proof success under a fixed prover loop, not nDCG alone.

## 6. Code/agent phase

Optional third-domain replication uses a fixed repository snapshot and answer-bearing files/locations. Structured queries may contain program entities/dependencies mechanically derived from visible task/repository state, but never ground-truth file paths from the evaluator.

## 7. Primary controlled endpoints

- Recall@k of all answer-bearing documents;
- nDCG@10;
- exact multi-hop evidence-set recovery;
- downstream answer accuracy with a fixed solver;
- retrieval calls and candidate tokens.

Report per-chain-length and distractor-cluster strata.

## 8. Frozen success gate

Controlled terminal

`STRUCTURED_QUERY_REDUCES_RETRIEVAL_RESOURCE_FRONTIER`

requires:

1. exact QF/QS semantic fact-set equivalence with zero failures;
2. QS evidence recall >= QF at every `k` for at least two primary retrievers;
3. at one target evidence quality `q>=0.80`, both thresholds observed and `k*_QS <= 0.5*k*_QF` for at least one retriever;
4. downstream fixed-solver accuracy improves by >=0.05 at one matched candidate budget;
5. opaque-symbol/order controls do not erase the direction of effect;
6. no query leakage or index difference.

If retrieval metrics improve but downstream solver accuracy does not, terminal is

`RETRIEVAL_ACCESS_IMPROVED__NO_DOWNSTREAM_REASONING_GAIN`.

## 9. Formal promotion gate

A formal-math claim requires, on a preregistered theorem set:

- lower `k*` or reranker scale for typed/native state;
- positive proof-success effect under matched Lean-call/search budgets;
- exact source/index/model receipts;
- premise leakage zero;
- module-stratified result.

Without downstream proof success, do not call it theorem-proving improvement.

## 10. Strongest allowed claim

If controlled + one real domain replicate:

> Exposing task relations in the query/state can shift the retrieval frontier: the same external knowledge becomes recoverable with a smaller candidate pool or weaker reranking, and the retrieval saving propagates to downstream task quality under a matched solver.

Forbidden:

- `retrieval and reasoning are the same thing`;
- `structured RAG is universally superior`;
- any comparison with different answer-bearing corpora presented as same-information.
