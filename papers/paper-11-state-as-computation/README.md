# P11 — State as Computation

**Stable ID:** ORION-P11  
**Paper issue:** #471  
**Shared tracks:** #664 accessibility-work accounting · #667 state optionality  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript. It supersedes the stale `papers/candidates/paper-11-state-as-computation/MANUSCRIPT.md` path on draft PR #715; that older file remains historical input and is not the canonical submission surface.

## Current evidence status

`PEER_REVIEW_PACKAGE_READY / CONTROLLED_AND_THEORY_CLAIMS_SUPPORTED / SPARSE_ATTACK_PARTIAL_NEGATIVE`

Earned evidence includes:

- exact query-family rank lower bound for fixed linear-accessible state;
- 91×–1820× registered universal/compiled representation ratios;
- 4× to >32× dense-decoder sample-threshold gains;
- no-answer-laundering P11B result;
- exact compile/cache/recover/materialize optionality laws;
- P11D hostile sparse-decoder result: **negative against the preregistered ≥4×-in-both-cells gate**, but with retained 2×/4× threshold residual and +0.2903/+0.3840 low-sample accuracy advantage.

The P11D negative and its replay defect are first-class artifacts:

- `P11D_NEGATIVE_ROOT_CAUSE_V1.md`
- `P11D_SPARSE_DECODER_RESULT_RECEIPT_V1.json`

P11C's stronger ExtraTrees attack remains `CANNOT_CHECK`: the frozen run emitted no authoritative terminal inside the available execution window, so the manuscript makes no claim from it.

## Strongest paper-level claim

> Query-conditioned state construction can externalize structural search from a bounded downstream decoder. In controlled query families this yields exact accessible-rank savings and large finite-sample gains under weak access; a frozen sparse universal decoder buys part of the advantage back but leaves a 2×–4× threshold residual in the registered hostile cells. The architectural choice also incurs calculable future-query option debt unless raw, cached or universal state is retained.

## Peer-review artifacts

- `MANUSCRIPT.md` — full paper
- `CLAIM_EVIDENCE_LEDGER.md` — claim authority and donor subtraction
- `PEER_REVIEW_READINESS.md` — five-lens hostile review/checklist
- P11/P11B/P11C/P11D protocols and harnesses — reproducibility surface

## Not authorized

No universal nonlinear lower bound, transformer/agent superiority, free preprocessing claim, or broad statement that compiled state always dominates universal state. A future real-system claim must charge compiler work and beat strong state/search/decoder baselines under a common resource boundary.
