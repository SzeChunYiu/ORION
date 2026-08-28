# Data, code, and reproducibility — ORION-10

## Data availability

| Artifact | Supports | SHA-256 |
|---|---|---|
| `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` | The all-`n` cost theorem the certificate rests on | `b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875` |
| `research/extensions/orion-qg/QG5B_EXACT_FORECASTER_RESULTS.json` | The theorem-backed static evaluator and the enlarged-borrow repair: zero error over 9,547 compared instances | `7701d4fb708a0a235493a0e4da72076d5d8b77a3e19fa9997ab6a5de51997f16` |
| `research/extensions/orion-qg/QG7B_HYBRID_FAMILY_RESULTS.json` | The hostile explanation stress test that refutes the repaired explanation, with 64 witnesses over 10,481 compared instances | `70cee5a5f80482d84e89a92365286e1043cf3e5cf9f847a204fa84d3abcab530` |
| `papers/orion-10-certified-static-forecasting/CLAIM_LEDGER_V2.md` | The claim ceiling this manuscript is written to | `5a8403cd2608311a9f24fff7d0407e4bccd43590951f9a871498b306a9254887` |

The primary chain is committed under `research/extensions/orion-qg/` with frozen
protocols under `development/orion-qg-regime-geometry/`. The founding all-`n`
cost theorem binds to receipts under `research/extensions/orion-q/`.

## Code availability

`research/extensions/orion-qg/qg5b_exact_forecaster.py` produces the evaluator
result and `qg7b_hybrid_family.py` the hostile stress test. Both are
deterministic under their recorded seeds; the fresh-panel seed is `20260826`.

## Reproducibility statement

A reproduction of this paper must preserve the chronology, because the paper's
claim is about the layering and not about the final number.

1. Re-establish the original forecast failure. The first regime formula was
   refuted on a fresh instance; a reproduction that starts after that point
   cannot see what the layering is for.
2. Verify the theorem-backed evaluator result against the unrestricted dynamic
   program: zero error across 9,547 compared instances, with no unrestricted
   call in the forecast path.
3. Independently reproduce the later refutation of the repaired explanation,
   including all 64 witnesses.

Collapsing these three stages into a final zero-error table would erase the
evidence the certificate separation exists to expose. That table would be
literally true and would misrepresent the paper.

## Scope of the digests

The digests bind an exact cost certificate under one frozen grammar and
objective, together with the refutation of one explanation layered above it.
They do not bind the explanation itself, which remains open: the paper's claim
hierarchy puts theorem above finite benchmark above unresolved explanation, and
the refutation is retained rather than repaired away.
