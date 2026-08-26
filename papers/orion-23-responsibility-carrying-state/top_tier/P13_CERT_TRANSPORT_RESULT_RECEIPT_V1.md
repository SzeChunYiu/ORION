# P13 drift-bounded certificate transport result receipt V1

**Programme:** #977 · **PR:** #992 · **State:** `EXECUTED_BOUND_ON_GREEN`

## Execution binding (exact)

| item | value |
|---|---|
| protocol (pre-outcome freeze) | `papers/paper-13-responsibility-carrying-state/top_tier/P13_CERT_TRANSPORT_PROTOCOL_V1.md` @ `16f33a9e` |
| cases (pre-outcome freeze, gold dispositions frozen) | `p13_cert_transport_cases_v1.json` @ `46ae7209` (62164 bytes, 60 cases) |
| runner / checker | @ `a6789c12` / @ `24d199a2` |
| CI run | `32661218622` (`p13-cert-transport-v1`), **conclusion=success** |
| artifact | id `9498859199`, size 2824 B, ZIP SHA-256 `eb1d784294cfbefe075bda43d24fd2ace66feb43cb2f98727892f171a19691d2` |
| primary terminal | `P13_CERT_TRANSPORT_V1_SUPPORTED` (receipt_sha256 `691b4b93…`) |
| independent terminal | `P13_CERT_TRANSPORT_SECOND_INDEPENDENT_CHECKER_GREEN` (receipt_sha256 `52191379…`), 0 invariant failures |
| agreement | `P13_CERT_TRANSPORT_TWO_IMPLEMENTATIONS_AGREE` asserted in-workflow; artifact JSONs byte-identical to local execution |

## Outcomes (60 cases; 20 per stratum)

| arm | verifier-correct | unsound transport | needless re-issue | mean literal reads |
|---|---|---|---|---|
| UNCONDITIONAL | 40/60 | 40 | 0 | 6.0 |
| SIGNATURE_ONLY | 60/60 | 0 | 20 | 11.333 |
| CONDITIONAL_DRIFT_BOUNDED | 60/60 | 0 | 0 | 10.0 |
| ALWAYS_RE_ISSUE | 60/60 | 0 | 20 | 11.333 |

REDUNDANT-stratum cost: ALWAYS_RE_ISSUE 12.0 > CONDITIONAL_DRIFT_BOUNDED 8.0 (payload accounting identical across arms: 6 per served certificate; arms differ only in verification reads).

All four frozen gates hold. UNCONDITIONAL's 40 unsound transports decompose as 20 CONFLICTING (content-invalid: stored model violates shifted formula) + 20 MIXED (protocol-level: justification set changed / non-monotone mixture, content may still satisfy). The MIXED half is unsound by the frozen transport predicate, not by content invalidity — both runner and independent checker apply the same frozen definition.

## What this earns

At bounded verifier-backed CNF scope: (i) unconditional certificate transport is unsound under conflicting drift (20/20 content-invalid serves); (ii) signature-equality transport refuses all 20 sound redundant-drift transports (missed-efficiency witness); (iii) a clause-diff drift bound with local added-clause verification is exactly correct on this grid (0 unsound, 0 needless, 60/60 verifier-correct) and cheaper than re-issue on the REDUNDANT stratum (8.0 vs 12.0 mean literal reads).

## What this does NOT earn (authority boundary)

- Transport beyond CNF clause-add/drop/strengthen drift classes; adversarially chosen drift; non-monotone formula rewrites.
- Real agent-workflow transport; research-agent-scope external authority gate.
- Any claim that the frozen predicate is the UNIQUE correct transport policy — only that it is exact on this grid and that its two named failure-mode competitors fail in the predicted directions.
