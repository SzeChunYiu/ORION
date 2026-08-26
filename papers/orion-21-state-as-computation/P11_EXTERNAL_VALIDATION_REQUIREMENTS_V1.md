# ORION-21 external validation — exact requirements for the open issue #1086 boxes

**Status:** CANNOT_CHECK (all three open boxes). This file records, per box, the
verbatim requirement, why it cannot be checked in the current executing
environment, and exactly what would satisfy it. It confers no result and no authority;
`P11_ACTIVE_CLAIM_AUTHORITY_V2.json` remains the sole active authority
and is unchanged by this artifact.

## Box 2 — comparator breadth

> "Compare compiled state against strongest retrieval/full-context arms across
> >=3 model families."

- **Why CANNOT_CHECK now:** the executing environment has no external model
  access — no hosted-model API credentials or egress, and no local model
  weights in the repository. The repo's `papers/orion-21-state-as-computation/
  evidence/` tree contains audits and receipts, not cached raw LongMemEval
  model transcripts. The LongMemEval dataset and its model-generated session
  histories are a multi-gigabyte download, beyond this lane's stated limits
  (no downloads >50 MB; disk headroom guarded at ~1.2 G free).
- **What satisfies it:** run compiled state, the strongest retrieval arm
  (hybrid dense+BM25 with reranking, tuned on a dev split) and the full-context
  arm on LongMemEval (and LongMemEval-V2 where its license verification
  passes), on >=3 distinct model families (e.g. one GPT-class, one Claude-class
  or Gemini-class, one open-weight family), with arm order randomized per
  session and the same harness for every family.
- **Reporting requirement:** per-model-family and pooled tables, with each
  family's arm deltas shown separately before any pooled claim.

## Box 3 — resource matching

> "Match tokens, latency, memory and embedding/compilation calls."

- **Why CANNOT_CHECK now:** no arm can be executed at all (see Box 2), so no
  resource vector can be measured; fabricating a matched-accounting table
  without executions would violate the paper's no-invented-evidence rule.
- **What satisfies it:** for every arm×family cell, record the full shared
  resource vector under the #664-style accounting — prompt+completion tokens,
  wall-clock latency, peak memory, embedding calls, compilation calls — and
  demonstrate budget parity within a declared tolerance (e.g. each arm's total
  charge within 10% of the strongest arm's, or the difference reported as a
  priced sensitivity). The compilation cost of the compiled-state arm must be
  charged, not amortized away.

## Box 4 — optionality and held-out robustness

> "Add future-query/optionality and leave-one-benchmark-out tests."

- **Why CANNOT_CHECK now:** these are derived analyses over executed runs;
  with zero executed runs there is no data to hold out.
- **What satisfies it:** (a) a future-query/optionality test — evaluate state
  compiled before the query set is known, then score against both the realized
  and a fresh disjoint query set, showing the compiled state's benefit is not
  query-specific overfitting; (b) leave-one-benchmark-out — freeze the
  allocation/compilation rule on all benchmarks but one, then evaluate on the
  held-out one, repeated for each benchmark.

## Pass gate (verbatim from issue #1086)

> "block-bootstrap lower CI >0 for quality, or >=2x resource saving with <=2 pp
> noninferiority; no benchmark loss >5 pp; direction stable across models and
> benchmarks."

Blocks for the bootstrap are sessions/queries as declared in the campaign
prereg — never generated rows or individual cached turns.

## Boundary

Even a full pass validates external utility of query-conditioned state
construction on these benchmarks and model families. It does not convert the
controlled-theory boundary results (P11D/P11H/ORION-21-query-family negatives) into
positives, and it does not license any universal compression claim. The
responsibility-conditioned negative remains binding on any successor.
