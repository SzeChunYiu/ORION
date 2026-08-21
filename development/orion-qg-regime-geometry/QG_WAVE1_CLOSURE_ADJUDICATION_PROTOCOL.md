# QG wave-1 closure adjudication — frozen protocol

Date: 2026-08-21
Branch: `claude/orion-harness-verification-b17qdj`
Status: FROZEN BEFORE THE ADJUDICATION RUN EXISTS.
Authority: development/adjudication record only; the harness terminal grants no
scientific or novelty authority — it decides only whether the wave-1 packet may move to
CLOSED and what the wave-2 residual ledger contains.

## Question (posed verbatim, single problem)

> Given the five committed wave-1 lane receipts (QG-1 theorem B=5; QG-2 mixed
> objective-dependence; QG-3 positive prospective confirmations; QG-4 template
> transferred to SixLCU; QG-5 completeness identity refuted with mechanism localized),
> is ORION-QG wave 1 scientifically closed under the charter's stop rules, and what
> does wave 2 inherit as its residual ledger?

## Instrument

Generic ORION harness (host-driven), same mechanics as dual-harness benchmark V0
Lane A: `orion-harness init` workspace; recursive solve (default mode,
`--max-iterations 3`); this session services capabilities ONLY with evidence drawn
from committed repository receipts (file paths cited in every evidence item; no
external web). The reconstruct summary and terminal constitute the adjudication
answer and are recorded verbatim in the packet.

## Decision space (all valid)

- CLOSED — every lane bound by theorem, receipted saturation, confirmed prospective
  test, first-class refutation, or cannot-check; residual ledger enumerated for wave 2.
- NOT CLOSED — at least one lane's stop rule is unmet; the blocking obligation is named.

## Constraints

- No gate weakening post-outcome; refutations (QG-5) and mixed verdicts (QG-2) are
  first-class closure modes, not blockers, per the charter.
- The protected stretched-N2 subject remains sealed and is not adjudication evidence.
- All harness receipts are archived under
  `development/orion-qg-regime-geometry/closure-adjudication/`.
