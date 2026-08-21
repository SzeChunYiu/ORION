# P11 — State as Computation

**Stable ID:** ORION-P11  
**Paper issue:** #471  
**Shared tracks:** #664 accessibility-work accounting · #667 state optionality  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript. It supersedes the stale `papers/candidates/paper-11-state-as-computation/MANUSCRIPT.md` path on draft PR #715; that older file remains historical input and is not the canonical submission surface.

## Current evidence status

`PEER_REVIEW_PACKAGE_READY / CONTROLLED_THEORY_SYSTEMS_SUPERIORITY_SUPPORTED`

Earned evidence includes:

- exact query-family rank lower bound for fixed linear-accessible state;
- 91×–1820× registered universal/compiled representation ratios;
- 4× to >32× dense-decoder sample-threshold gains;
- no-answer-laundering P11B result;
- exact compile/cache/recover/materialize optionality laws;
- P11D hostile sparse-decoder result: **permanently negative** against the preregistered ≥4×-in-both-cells gate, but retaining 2×/4× threshold gaps;
- P11E fresh deterministic replication of the sparse residual: sparse/compiled thresholds `128/64` and `256/64`, with +0.2912/+0.3307 accuracy gaps at `n=64` and byte-identical two-run payload SHA `1097d94b…a4536`;
- P11F historical nonlinear output, now **non-authoritative** because hostile PR review found a protocol mismatch (`n_jobs=-1` despite an otherwise-default frozen contract);
- P11G fresh deterministic nonlinear successor: `n_jobs=1`, explicit random states, replay enforced inside the terminal path; universal ExtraTrees remains `NOT_REACHED` at 0.95 through `n=1024` in both cells while compiled state reaches `n=64`, with +0.4624/+0.3942 gaps at `n=64`; two fresh subprocess scientific payloads share SHA `a2b0c33c…79a7cc`.

Historical failures remain first-class artifacts. P11D is never relabelled positive, P11C remains `CANNOT_CHECK`, and P11F is not used as claim authority. P11E and P11G are independent successor protocols, not edits to those outcomes.

## Strongest paper-level claim

> **State is a computational placement decision.** In controlled query families, query-conditioned state construction externalizes structural search from a bounded downstream access mechanism. This yields exact accessible-rank savings and large dense-decoder sample gains; a sparse universal decoder recovers part of the advantage but leaves a fresh deterministic 2×–4× threshold residual, while a replay-gated deterministic nonlinear tree successor remains below the target through `n=1024` where compiled state succeeds at `n=64`. The same specialization incurs calculable future-query option debt unless raw, cached or universal state is retained.

## Peer-review artifacts

- `MANUSCRIPT.md` — full paper
- `CLAIM_EVIDENCE_LEDGER.md` — claim authority and donor subtraction
- `PEER_REVIEW_READINESS.md` — five-lens hostile review/checklist
- `REVIEWER_SUMMARY.md` and `PR_SCOPE.md`
- P11/P11B/P11C/P11D/P11E/P11F/P11G protocols and harnesses — full evidence history
- P11D negative, P11E replicated sparse and P11G authoritative nonlinear receipts

## Not authorized

No universal nonlinear lower bound, transformer/agent superiority, free preprocessing claim, or broad statement that compiled state always dominates universal state. A future real-system claim must charge compiler work and beat strong state/search/decoder baselines under a common resource boundary.
