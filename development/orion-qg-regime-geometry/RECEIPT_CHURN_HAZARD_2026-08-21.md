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

## The deeper finding: digest custody verifies integrity, not correctness

The lane has since reported what those three digests actually were, and it changes the
lesson:

- `f80deba7…` was a **defective run**. A menu-reduction bug let a later tag choice
  clobber a cheaper configuration; it contradicted the receipt-bound T4a lemma on the
  unpinned sector and reported a residue of **6,481**.
- `8f7cf34c…` is the bug-fixed lemma (residue **12**) with class-level census dispatch.
- `cdca51a1…` is the same lemma outcome plus the protocol-required *per-pattern,
  state-level* census dispatch (5,216 → 135,604 dispatched closed). Terminal and residue
  are identical to the previous version; only dispatch granularity changed.

So the churn was not sloppiness — each rewrite was a genuine correction. But note what
this means for the custody runner built earlier the same day
(`run_qg7_family_dual_harness.py`): **Lane A re-derived `f80deba7…` from the file,
matched it, and recorded ACCEPT_PARTIAL_CHAIN; Lane B agreed; the verdict was AGREE — on
a scientifically defective receipt.**

That is not a bug in the runner. It is the exact scope of what digest custody can do:

> Re-deriving a receipt's declared digest proves the artifact is **intact and
> self-consistent**. It proves nothing about whether the computation inside was
> **correct**. A buggy analyzer produces a receipt that is perfectly digest-valid.

Only two mechanisms caught the defect, and neither was custody: the lane's own
cross-check against the receipt-bound T4a lemma (an internal consistency obligation
between independent results), and the independent generic verifier that re-derives the
science from primitives rather than re-reading the receipt. Both survive the bug; digest
custody does not.

Consequence for how the programme should read its own custody artifacts: an AGREE verdict
from the dual-harness runner is evidence of **provenance**, not of **truth**, and must
never be cited as scientific corroboration. Where corroboration is claimed, the citation
must be to a from-primitives verifier or to a cross-lemma consistency check. Nothing here
is retracted — the defective artifact was gitignored and never entered the permanent
record — but the wording of custody claims must not overreach.

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
