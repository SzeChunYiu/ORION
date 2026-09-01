# ORION-11 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `NECESSITY_CLAIM_FALSIFIED__COST_OBSERVATION_RETAINED__PACKAGE_OPEN`

This addendum is part of the frozen ORION-11 paper-content packet. It freezes a
paper whose headline claim was **falsified by its own prospective test**, and
records what survives that falsification without inflating it.

## What was falsified, and by what

The comparative mechanism-necessity reading `ORION-11.NECESSITY.V2.2.4` is
**retracted**. The trigger is
`experiments/r4-faithful-comparator-v1/`, PR #1603, LUNARC job 3550342, verdict
`H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION`.

The test was fair by construction and the anchor reproduction gate passed before any
comparison was read: the necessity arm reproduced at success 1.0 with forbidden rate
0.0, and the repair parent reproduced at its expected 0.49375.

Over 2,882 credential-free mechanical worlds with 480 hidden-shift worlds under an
identical four-unit intervention budget, the primary criterion was protected
root-task success **and** no forbidden high-level mutation, with a success floor of
0.99 and a forbidden ceiling of 0.01.

`activevoi_search_admitted_parent` cleared both components — hidden-shift success
`1.00000`, forbidden high-level mutation rate `0.00000` — with McNemar `b = 0`,
`c = 0`, `p = 1.0` and a bootstrap 95% CI of `[0.0, 0.0]` on the paired difference.
`matches_orion_within_margin: true`.

The margin the paper had frozen, `+0.50625` primary with `+0.5167` on replication,
was **fully recovered by ordered search alone**: giving each parent a single change —
one top-confidence pick replaced by ordered search over the same public repair
diagnostic menu — moved all three repaired parents from `0.49375` to `1.00000`.

One detail should not be smoothed away: only one of the two admitted parents
matched. `darc_search_admitted_parent` reached hidden-shift success `1.0` but a
forbidden high-level mutation rate of `0.2377`, far above the `0.01` ceiling, so it
does **not** match within margin. The falsification rests on
`activevoi_search_admitted_parent` alone, and saying "a faithful comparator matches"
is precise only in that singular.

## What survives

A **measured cost gap, not a necessity result.** Among policies that clear both
registered components, the governed ORION policy reaches the required outcome at a
mean intervention cost of `1.8341` against `2.6676` for the faithful parent that
also clears them, under the identical four-unit budget.

**What produces that gap is not attributed here, and the distinction is
load-bearing.** It is an observation, not a mechanism claim. Theorem C in
`experiments/costed-ordering-v1/THEORY.md` proves that level filtration can never
make ordering cheaper than unconstrained `p/c` ordering — it ties in the
ratio-aligned case and costs strictly more otherwise. So the gap is a *predicted*
property of ordering by `p/c`, which is **donor-owned prior mathematics**, not
something this paper invented.

`scientific_authority_delta` is `NONE` on both the retraction ledger and the
reframed contribution. Neither document creates authority, runs an experiment, or
promotes an adverse or `CANNOT_CHECK` record; the R4 result's own delta reads
`NONE_UNTIL_MERGED`. The committed internal necessity terminal is retained as
history rather than deleted — the falsification is recorded on top of it, not in
place of it.

## Package state: open, and not closed by this freeze

`journal_package/CLAIM_PDF_AUDIT.md` records `Package status: SUPERSEDED`,
`ORION-11.CURRENT_PACKAGE = OPEN`, and `Current submission authority: false`, and
`CANONICAL_SOURCE_DECISION_V1.md` records that no LaTeX PDF build has been run. The
packaged `manuscript.pdf` was rebuilt through the pinned renderer at commit
`7ae62c87c`; the historical exact-render binary it superseded is preserved in git
history, not in the working tree.

This is therefore a freeze of a **scientific position**, not of a submission packet.
The package remains open and no submission authority is claimed.

## Frozen content surface

The content packet consists of `CLAIM_RETRACTION_LEDGER_V1.md`,
`REFRAMED_CONTRIBUTION_V1.md`, the R4 faithful-comparator experiment with its
protocol, policies, world and protected-matrix digests and its primary result,
`experiments/costed-ordering-v1/THEORY.md` carrying Theorem C,
`RSE_SUCCESSOR_BOUNDARY_V1.md`, `CANONICAL_SOURCE_DECISION_V1.md`, the journal
package with its claim/PDF audit, and this addendum. ORION-11's claim is now a
bounded cost observation under a registered protocol; it does not own the ordering
mathematics that predicts it.
