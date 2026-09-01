# V3's nine were real: the offset-3 envelope is refuted, not an artefact

**Status:** `ENVELOPE_REFUTED__V3_VIOLATIONS_CONFIRMED_GENUINE`
**Scientific authority delta:** `NONE`. `promotes_no_claim` continues to hold.

## The question, and why it was left open

`../vocabulary-minimality-v4-per-panel-dedupe/PROTOCOL_V4.md` was frozen before the V4 run,
at commit `74795c473`, and predicted:

> V3's nine violations all lie **beyond** V2's prefix, in `H2_n3` (5) and `H4_n3` (4), both
> panels whose enumeration V3 contaminated. If cross-panel skipping produced them, they
> should not survive. If they are genuine members of the frozen space, they should reappear.

`RESULT_V4_2026-09-01.md` recorded that prediction as `CANNOT_CHECK`, because
`run_per_panel_v4.py` emits none of the protocol's three terminals and reports no prefix
control. That was the right call about the runner's *terminals*. It was too pessimistic
about the runner's *data*.

## The answer

The V4 receipt serialises `full_census_rows_v2`: 13,458 rows, each carrying `C_DP`,
`C_Dplus`, `C_Dxx`, `f_Bprime`, `panel` and `regime`. The envelope is a function of those
fields, so it can be computed directly rather than inferred from a terminal.

Instances exceeding offset 3, over the whole per-panel-dedupe census:

| quantity | instances over 3 | panels |
|---|---:|---|
| `f_B' − C_Dxx` | **9** | `H2_n3` 5, `H4_n3` 4 |
| `C_D+ − C_Dxx` | 0 | — |
| `C_DP − C_Dxx` | 0 | — |

Nine, in `H2_n3` and `H4_n3`, split five and four. That is V3's result exactly — the same
count, the same two panels, the same division between them.

**The nine reappeared. They are genuine members of the frozen space, not a cross-panel
skipping artefact.**

The offsets are 4 (×8) and 5 (×1), and all nine sit in the `split` regime.

## Which quantity the envelope is, and how that was settled rather than assumed

`BPRIME_FIBRE_CRITERION_V1.json` reports three offsets and the protocol says only "offset
3", so the quantity had to be identified rather than guessed. Only one of the three produces
any instance above 3 at all, and it produces exactly nine in exactly the two panels V3
named. The other two produce zero. That is an unambiguous identification, and it would have
failed loudly had the wrong quantity been chosen.

## What this establishes, and what it does not

**Established.** V3's nine violations survive the per-panel dedupe fix at eighteen times the
coverage — 13,458 rows against the 740 V2 evaluated. The `ENVELOPE_SURVIVES_20X_COVERAGE`
terminal is **refuted**: the envelope does not survive, because nine instances exceed it.
`REVIVAL_PASS_V1.md`'s one-sided bound stays withdrawn, and V3's nine are confirmed rather
than assumed, which is what the protocol asked for.

**Not established.** The prefix control was still never run. `PROTOCOL_V4.md` wanted it to
make V2's rows and V4's comparable, and no such comparison is made here.

That turns out not to matter for this question, and the reason is worth stating: the prefix
control existed so that a *partial* V2 census could be compared against a *larger* V4 one.
Computing the envelope over the complete V4 census answers the question directly, without
needing the two to be nested. A stronger route, not a substitute for a weaker one.

The prefix control remains unrun and remains the right thing to build if some later question
needs V2 and V4 rows compared row-for-row. Nothing here needs that.

## Scope

The frozen unit-cost R6M grammar and the ten registered panels. Says nothing about all `n`,
promotes no claim, moves no other terminal.
