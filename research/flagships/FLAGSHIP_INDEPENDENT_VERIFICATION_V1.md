# Flagship lane: independent verification of the materialized packet

Materialized from `orion_top_tier_promotion_bundle.zip`
(SHA-256 `fcca596d9c7a2b42e50358386b6fa076bac6ed676a09a24b2cc959fe67ed17f0`) and
verified file by file against the archive before anything was run:
**16 files, 0 differ.** Only `__pycache__` was dropped.

## Checker

`independent_checker/check_controls.py` → exit 0,
`CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN`,
digest `b56c6eb799f4b94bc8c67bdb0db7df225bcc6943283c85a713c0c7e41445f41c`.

`test_flagship.py` runs from the committed tree.

## Falsification

Flipping a single boolean in `CONTROL_RESULT.json` flips the checker to exit 1,
`CONTROL_PLANE_REJECTED`. The checker is sensitive to the outcomes it certifies
rather than merely re-reading them.

## What the terminal says, and what it does not

`CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN` is half a result and names
the missing half in its own text. Verified: a global adaptive false-promotion
theorem, noncompensatory fresh/retention/harm gates, a one-bit reusable-feedback
contract, an append-only negative history, fair baseline and resource contracts,
and independently reconstructed hostile receipts.

**Not claimed, per the packet's own disposition:** protected transfer,
frontier-agent superiority, any effect of negative history, and submission
readiness. The empirical campaign has not been run, so nothing here is evidence
about how the control plane performs — only that it is internally consistent and
that its controls are checkable.
