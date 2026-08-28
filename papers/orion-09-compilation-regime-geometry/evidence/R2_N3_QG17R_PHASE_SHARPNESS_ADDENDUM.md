# R2 revival addendum — N3 (no support-2 phase witness)

Operator mandate 2026-08-28: every recorded negative gets a genuine revival attempt before any
freeze is final. Frozen files are untouched; this addendum is the amendment vehicle.

## Claim row amended

- orion-09 CLAIM_LEDGER V2 family (QG-17 lane): "no support-2 phase witness exists in the frozen
  V5 domain" — originally recorded with an open artifact-risk caveat about the shared-Tag
  frame-pair cap-1 semantics (infeasible cells were being counted as ties).

## Old verdict

NEGATIVE with artifact risk: 211,248 candidates enumerated, 0 strict witnesses under any
objective (O0, O_nc_out, O_restore_out, O_tag_out), but near-miss ties concentrated at O_nc_out
left open the possibility that the cap-1 semantic (skip vs penalize infeasible shared-Tag
frame-pair cells) was manufacturing the absence.

## Failure attribution (ONE stage)

Statistic stage, not enumeration stage: the enumeration was complete (211,248 candidates, digest
30338474f41c5e1362d4c44ff455b3e5b8496b0210e61945bf7ee9668c6a60cd, run 32529563653, both checkers
ACCEPT_BOUNDED_NEGATIVE); the doubt lived entirely in how the corrected cap-1 minimum treated
infeasible cells.

## Lever applied (by the committed QG17R reopen lane; re-read and re-verified here)

Corrected statistic: cap-1 semantics = "infeasible shared-Tag frame-pair cells skipped; exact
minimum over feasible cells". Re-test vs strongest parent on the same frozen V5 domain.

## New verdict

**NEGATIVE STANDS — CORRECTED-STATISTIC CONFIRMED (revival attempted; negative upgraded from
artifact-risk to robust).** Under the corrected semantics the terminal is
QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN with strict_count 0 under ALL four objectives and
an empty outside-objective witness list; global_phase_boundary_complete stays false (domain-bounded
claim only, no promotion). The absence is not an artifact of the tie-handling: the corrected
exact minimum over feasible cells still admits no strict witness.

## Residual (recorded, not hidden)

The negative is domain-bounded: it holds in the frozen V5 domain only. A witness outside that
grammar/domain remains logically possible; claiming one would be new work, not a revival of this
row. Authority ceiling NOT_R6 unchanged.

## Evidence

- research/extensions/orion-qg/QG17R_CORRECTED_PHASE_SHARPNESS_RESULTS.json (terminal, objectives,
  candidate_count 211248, result_digest 30338474f41c5e1362d4c44ff455b3e5b8496b0210e61945bf7ee9668c6a60cd,
  head_sha aa03a3c064c419c164a5d38e17c4e8f7ea55f993, both generic_orion and native_orion_q
  decisions ACCEPT_BOUNDED_NEGATIVE).
- Adjudication context: development/orion-qg-regime-geometry/QG_WAVE23_CLOSURE_PACKET.md (N3 was
  an adjudication prediction "right outright").
