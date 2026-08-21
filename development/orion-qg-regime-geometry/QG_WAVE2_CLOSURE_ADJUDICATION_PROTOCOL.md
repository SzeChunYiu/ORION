# QG wave-2 closure adjudication — frozen protocol

Date: 2026-08-21. Branch: `claude/orion-harness-verification-b17qdj`.
Status: FROZEN BEFORE THE ADJUDICATION RUN EXISTS.
Authority: development/adjudication record only. The harness terminal grants no
scientific or novelty authority; it decides only whether wave 2 may be recorded as
closed and what wave 3 inherits.

## Question (posed verbatim, single problem)

> Given the committed wave-2 receipts — QG-5b, QG-6, QG-7, QG-7b, QG-7c, QG-7d, QG-8,
> the QG-9 ladder (V2–V6), QG-12, QG-13 V1, QG-15, QG-15b, QG-16, QG-17, QG-18 — is
> ORION-QG wave 2 scientifically closed under the charter's stop rules, and what does
> wave 3 inherit as its residual ledger?

## Instrument

Generic ORION harness, host-driven, same mechanics as the wave-1 adjudication:
`orion-harness init`; recursive `solve` (default mode); this session services every
capability request **personally**, with evidence drawn only from committed repository
receipts (file path cited in every evidence item; no external web). The reconstruct
summary and terminal constitute the adjudication answer and are recorded verbatim.

## Decision space (all valid)

- **CLOSED** — every wave-2 lane terminates in a charter-listed closure mode
  (theorem, donor absorption, receipted saturation, confirmed prospective test,
  first-class refutation, honest bounded negative, or cannot-check), with a
  receipt-localized residual ledger enumerated for wave 3.
- **NOT CLOSED** — at least one lane's stop rule is unmet; the blocking obligation is
  named.

## Constraints

- No gate weakening post-outcome. Partial terminals (QG-7c, QG-7d), bounded negatives
  (QG-17, QG-9 V5) and mixed verdicts (QG-2) are first-class closure modes per the
  charter — a partial is *not* a failure, but it also may not be reported as a theorem.
- The unclosed TARE all-n classification (comm-s2 pinned sector, open at QG-7d's P1
  residue) must be carried into the wave-3 ledger explicitly, not elided.
- `QG_EXTERNAL_DONOR_REGISTER_V1.md` is in scope: the adjudication must account for the
  fact that the lanes' novelty freezes were written without literature access, and that
  the first real external check found five previously unnamed donors.
- The protected stretched-N2 subject remains sealed and is not adjudication evidence.
- All harness receipts are archived under
  `development/orion-qg-regime-geometry/closure-adjudication-wave2/`.

## Honesty obligations specific to this adjudication

The wave-1 adjudication returned `CANNOT_CHECK` twice before `SOLVED_VERIFIED`, and its
fail-closed verifier rejected two host evidence items. Those negative records were
retained. The same applies here: any `CANNOT_CHECK`, any rejected evidence item, and any
resource-bound truncation is recorded verbatim rather than retried into silence.
