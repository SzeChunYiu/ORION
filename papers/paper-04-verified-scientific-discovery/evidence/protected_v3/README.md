# P4 protected battery V3 — promoted evidence

The four files beside this one are byte-identical copies of
`research/campaigns/2026-08-21-p4-battery-v3-identifiable/`, promoted into the
paper on 2026-08-22 so that P4's H3 claim cites evidence the paper's own content
binding covers. A claim whose artifact lives outside `papers/paper-04-…/` is
named by `journal_package/MANIFEST.json` and hashed by nothing:
`journal_package/SHA256SUMS` derives what it hashes from `required_files`, and
`required_files` paths resolve against the paper root.

| file | what it is | digest at promotion |
| --- | --- | --- |
| `FREEZE.md` | the protocol, written 2026-08-21 before the construction was repaired and before any panel outcome was observed | `32f6dd9bbcfe4b1db5410f43500e1f883a5818e0e5c153a8dfe3d3580bb83eea` |
| `IDENTIFIABILITY_V3.json` | every probe's confusion matrix and informedness, for constructions v1/v2/v3, three terminals, thirteen seeds — written *before* the panel ran | `037febe67f7a9d58730df51ff3b7541c9b6df0d929cc4003208c0eef9aeda392` |
| `PANEL_V3.json` | the frozen panel's output on the V3 battery: H1/H2/H3 and the per-system rates | `b196190c5cb6b063c93ae3371612f68569d7d2f637fb000f733ee94229b1918d` |
| `RESULT.md` | the report | `f27324376b7aa7daf24cc0c12338525acd035474a79bd992ea597374872bd655` |

Copies, not moves. The campaign directory keeps the run scripts
(`run_identifiability.py`, `run_panel.sh`, `collect_panel.py`) and is the path
`orion.programme.panel_resolution.PUBLISHED_PANELS` and
`evidence/audit/P4_PANEL_RESOLUTION_2026-08-22.json` already name; repointing
those at a second copy would rewrite a record to accommodate a filing decision.
`tests/unit/p4/test_p4_h3_v3_promotion.py` asserts the two copies are equal
byte-for-byte, so the duplication cannot become a divergence in silence.

`FREEZE.md` is a frozen protocol and is not edited here or anywhere.

## What the promoted numbers say

H3 is `SUPPORTED` at 1.0, CI95 [1.0, 1.0], against the pre-registered threshold
`ci95_low > 0.0`. ORION selects the correct `CANNOT_CHECK` terminal on 30/30 gold
cases with 0/360 false promotions. The comparator is
`provenai-citation-fidelity-influence`, selected by **H1** — lowest
false-promotion rate — exactly as the frozen evaluator selects it; it scores
0/30, which is where the 1.0 comes from.
**`deepsciverify-abstract-to-full-escalation` scores 15/30 and is not the
comparator; against it the margin is 0.5.** Both numbers belong in any sentence
about H3.

What it measures, fixed in `FREEZE.md` §5 before the panel ran: **terminal
expressiveness under a non-compensatory gate lattice — the ability to report an
inability — not a finer-grained scientific judgement.** Nine of the ten
comparators score 0 because they cannot emit `CANNOT_CHECK` at all once the
empty-evidence case is gone. A panel of eleven systems in which ten are
two-valued cannot separate "better at knowing when it cannot check" from "the
only one that can say so", and this battery does not.

The score is quotable only because the identifiability register clears: fourteen
probes at informedness 0.0 on the `CANNOT_CHECK` axis, on all thirteen seeds,
against a declared ceiling of 0.0. On the V1 and V2 constructions the same
register reports 1.0.

## What this does not do to the V2 record

Nothing. `evidence/protected_v2/PUBLICATION_METRICS_V2.json` and everything
beside it stand as the record of what the V1 construction produced, and its H3 —
`NOT_SUPPORTED` with all eleven systems at `correct_cannot_check_rate` 1.0 —
remains correctly readable as an instrument with no resolving power rather than
as a comparative finding. `evidence/audit/P4_PANEL_RESOLUTION_2026-08-22.json`
records that reading (`metric_resolution: SATURATED`,
`verdict_could_have_differed: false`) and `tests/unit/p4/test_p4_metric_headroom.py`
pins it. `RESULT.md` §3 is explicit: nothing here licenses restating V2's number.
V3 is a different battery.
