# R24 comparator `CANNOT_CHECK` interpretation retraction — V1

**Correction date:** 2026-08-31  
**Affected historical interpretation:** commit `662267cee6999086570c26f7519e963708953b35`, including `CLAIM_LEDGER_V3.md` V3-E7/V3-X4 and the corresponding manuscript and package prose  
**Frozen scientific terminal:** `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` — unchanged

## Historical statement preserved and retracted

The publication-closure draft stated that the frozen R24 result serialized only the aggregate strict-violation counts (20 for the geometry primary and 14 for the matched lexical control), so a paired comparison could not be reconstructed. That interpretation is preserved here for provenance but is **retracted as false**.

## Defect

The committed `folds` object contains, for every held-out dataset, a Boolean `violation_strict` field under every evaluated arm for both `R24_ARM_CONDITIONAL_BOUNDARY_FIBRES` and `R24_LEXICAL_GOOD_BOUNDARY_NEGATIVE_CONTROL`. Each geometry fold also serializes its selected `primary` arm. Matching that geometry-selected arm into both policy maps and pairing rows by dataset therefore reconstructs the comparator without rerunning an experiment or inventing missing data.

## Deterministic correction

`verify_r24_strict_violation_comparator.py` binds the frozen result bytes, checks identical fold and dataset membership, rejects missing or non-Boolean flags, enforces unique held-out rows and agrees with both serialized aggregate summaries. It obtains:

- geometry primary: 20/44 strict violations (0.454545...);
- matched lexical control: 14/44 strict violations (0.318181...);
- paired contingency `(both, geometry-only, control-only, neither) = (14, 6, 0, 24)`;
- exact two-sided McNemar `p = 0.03125`.

Both rates remain above the frozen maximum of 0.10. Thus both certificates are adverse. The paired endpoint supplies no geometry-superiority result; on this frozen strict-violation endpoint, geometry has six additional failures and no fewer. Because this corrective comparison is bounded to one outcome-exposed pinned-corpus study whose two policies are both invalid, it does not establish broad lexical superiority, transfer, deployment value, external independence, or a positive paper claim.

## Authority disposition

This correction repairs a real scientific-record defect and changes no raw result, protocol, comparator, tolerance, terminal, or earlier negative result. The former `CANNOT_CHECK` interpretation must remain visible only as retracted provenance and must not appear as current authority.
