# P14B Protocol-Conformance Correction V1

**Status:** `P14B_NON_AUTHORITATIVE_PROTOCOL_MISMATCH`  
**Recorded:** 2026-08-21 after hostile PR review  
**Protected historical files remain unchanged.**

## Finding

The frozen P14B protocol required nuisance booleans to be randomly reminted within each stratum without changing the protected disposition. The realized `run_p14b_balanced_governance_v1.py` generator did not instantiate that requirement across all strata: several strata retained fixed/default nuisance coordinates except for a limited subset of explicitly varied fields.

Therefore the reported P14B numerical separation is **not a protocol-conforming protected result**.

## Scientific disposition

P14B was already downgraded for a separate, stronger circularity concern: the `ORION_RSE_FULL` arm reused the same adjudication function that generated protected gold. This correction adds a second reason that P14B cannot carry external claim authority.

The P14B files and terminal are retained as development/diagnostic history. They are never used as the primary evidence for ORION-24.

## Successor

P14C was frozen after the circularity finding and separates:

1. a static adjudication specification (`P14C_ADJUDICATION_CASES_V1.json`), and
2. independently implemented policy functions that receive facts only, with gold/rationale/case identity stripped before every call.

P14C does not inherit P14B's nuisance-reminting promise; instead the frozen case table explicitly enumerates nuisance combinations and precedence cases. Its protocol authority is adjudicated separately in `P14C_PROTOCOL_ADJUDICATION_V2.json`, including the originally omitted replay gate.

## Claim rule

Any manuscript, README, claim ledger, PR description, or reviewer summary that mentions P14B must label it as **diagnostic/non-authoritative**. The strongest controlled ORION-24 result is P14C specification-separated governance-contract conformance.
