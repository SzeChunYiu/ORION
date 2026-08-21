# Receipt-churn hazard: in-place re-runs silently invalidate digest bindings

Date: 2026-08-21. Branch: `claude/orion-harness-verification-b17qdj`.
Authority: development record. Lowers no scientific claim; names a process defect.

## What happened

`research/extensions/orion-qg/QG7D_LAST_LINK_RESULTS.json` was rewritten **in place**
at least twice after other artifacts had already bound its `result_digest`. Three
distinct digests exist for what is nominally the same lane result:

| digest | provenance | still exists? |
|---|---|---|
| `f80deba7d276…` | verified and bound by `run_qg7_family_dual_harness.py` (Lane A re-derivation) | **no** |
| `8f7cf34cca0b…` | committed at `e7177826` | in git history only |
| `cdca51a19c2f…` | produced by the post-receipt extended script (`t4b_failing_cells`, `census_state_dispatch`) | on disk |

The lane terminal `QG7D_PARTIAL__P1_RESIDUE_OPEN` is **identical across all three**, so
no scientific claim changes and nothing needs retracting. What broke is narrower and
still serious: two artifacts now assert a digest for a file that no longer has it.

## Why it is a real defect and not bookkeeping

The programme's evidence chain rests on a receipt being a stable, digest-addressable
object. Two consumers had already bound this one:

- `artifacts/orion-qg-qg7-family-dual-admission.json` — Lane A re-derived `f80deba7…`
  from the file and recorded the match as custody evidence.
- The wave-2 closure adjudication (`closure-adjudication-wave2/`) — bound QG-7d as a
  lane with a replay-verified receipt.

Both statements were true when made and are now unverifiable against the working tree.
A reader re-deriving the digest today finds a mismatch and cannot tell, from the
artifacts alone, whether the lane was re-run innocently or the result was altered.
That is exactly the failure mode receipts exist to prevent — and it is the same shape
as the two harness defects found today (silent timeout truncation; silently ignored
payload keys): **an artifact quietly ceasing to mean what it says, while still looking
valid.**

## Rule adopted

1. A receipt file is **frozen once any other artifact binds its digest**. Re-runs that
   are expected to reproduce it may verify against it; they may not overwrite it.
2. Continued work on a lane after its receipt is bound requires its **own pre-outcome
   freeze and its own receipt path** (`*_V2_*` or a new lane id). It may not be
   reported under the already-bound terminal.
3. Any lane script edited after its receipt was committed carries a provenance note in
   the commit that changes it (done for `qg7d_last_link.py` at `14212f6e`), because a
   replay of the current script is no longer expected to reproduce the committed
   receipt.

## Disposition here

The QG-7d terminal stands: `QG7D_PARTIAL__P1_RESIDUE_OPEN`, the comm-s2 pinned sector
open at QG-7d's own P1 residue, carried as wave-3 residual W1. The stale digest
bindings are recorded here rather than repaired by re-running the custody runner
against a moving file; re-binding happens once the lane is genuinely quiescent, and
the custody artifact is then regenerated as a whole rather than patched.

The QG-7d agent has been instructed to stop writing to that path.
