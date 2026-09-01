# Does the papers' own code express the amplification scenario?

**Status:** `ASYMMETRIC_GAP_CONFIRMED__ONE_SIDE_COMPLICATED`
**Scientific authority delta:** `NONE`.

`AMPLIFICATION_CHECK_V1.json` states plainly that it checks *my* formalisation, not the
papers' implementations. This measures the papers' code directly, so that scope caveat
can be replaced by a fact.

## ORION-18 cannot express repair, and this is the direction that matters

Across all **12** ORION-18 Python files:

| | files |
|---|---|
| mentioning `repair` / `revalidat` / `reopen` | **1** |
| mentioning `obligation` / `authoriz` (control) | **11** |

The control fires strongly — up to 52 occurrences in a single file — so the measurement
discriminates. And the one repair-shaped hit is not a mechanism: it is the string
`"reopen_plan"` appearing in `check_benchmark_contracts_v2.py` as the *name of a hard
obligation*. ORION-18 obligates the existence of a reopen plan; it does not model
reopening.

**So the paper's own checker could not represent the counterexample.** Not because the
scenario is wrong, but because the vocabulary is absent. That is the honest closure of the
"my model versus their implementation" gap: they do not disagree — one of them cannot state
the question.

This is the direction that matters, because the attack is *repair promotes authority*, and
ORION-18 is the side that would have to notice.

## ORION-16's side is more complicated than its formal core suggested

Across all **20** ORION-16 Python files:

| | files |
|---|---|
| mentioning `authoriz` / `root_class` / `permission` | **10** |
| mentioning `repair` / `revalidat` / `certif` (control) | **17** |

Half its code touches authority vocabulary, while its `FORMAL_CORE_V2_1` mentions authority
only four times. **This partly complicates the "formally disjoint" claim** made in
`A6_COMPOSITION_ROUTE_V1.md`: the disjointness is real at the level of the formal cores,
but ORION-16's implementation already reaches across the seam that its theory does not.

I have **not** checked whether those mentions model authority or merely use the word, and I
am not going to assert either reading without looking. Two possibilities, with different
consequences:

- If the code genuinely models authority, the composition is **more tractable** than the
  formal cores suggest, because one side already has the vocabulary and the theory simply
  has not caught up.
- If the mentions are incidental, the disjointness claim stands unchanged.

Either way the ORION-18 side is unaffected, and the ORION-18 side is where the attack has
to be noticed.

## What this changes

The counterexample's status improves. It is no longer only *argued from definitions and
checked against my model*: the paper that would have to detect it demonstrably has no
vocabulary in which to do so, measured over its whole implementation with a control.

What it does not change: the counterexample still needs encoding against a repair-aware
authority model that the programme does not yet have. Building that model **is** the
composition work, and it is the same work either way.

## Open item, named so it is not lost

Determine whether ORION-16's ten authority-mentioning files model authority or merely
mention it. That single check decides whether `A6_COMPOSITION_ROUTE_V1.md`'s disjointness
framing needs amending.
