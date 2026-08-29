# ORION-17 rule-disagreement cohort v1 (external, outcome-blind)

**Terminal: `COHORT_ACQUIRED__OUTCOME_BLIND__NO_OUTCOME_AUTHORITY`.**

Read this section first, because the headline number is easy to misread.

## The disagreement count is definitional, not a result

The protocol's two strata are *defined* as the region where the rules disagree:

- `small_fewedge_dense` = `density>=1.5 AND modules<49 AND edges<216`
  → density says **unsound**, both absolute-size rivals say **sound**.
- `large_manyedge_sparse` = `density<1.5 AND modules>=49 AND edges>=216`
  → density says **sound**, both rivals say **unsound**.

So every admitted repository disagrees with both rivals **by construction**. The
disagreement count in `COHORT_V1.json` is a *correctness check on the selector* —
anything below the accepted total would be a bug — and it is **not evidence for or
against the density rule**. A brief that asks "how many disagree, and if they never
disagree that is the finding" has the logic inverted: disagreement is the
eligibility criterion, not a sampled property.

All the discriminating content lives in the **outcome** phase — which rule is
*correct* inside the disagreement region — and that phase is deliberately not
touched here. Nothing in this directory moves the protocol's
`PROSPECTIVE_RULE_SUPPORTED__UNIQUE_MECHANISM_NOT_IDENTIFIED` terminal.

## Scope correction

The task I was given described 10 repositories in one stratum. The frozen
protocol specifies **`n_total: 20`, two strata of 10**. The decisive check is the
protocol's own `primary_gate`: `density_wins_total_min: 15` and
`density_wins_each_stratum_min: 7`. A single 10-repository stratum cannot satisfy
that gate at all. I built both strata.

## Measurement is the campaign's own, and it reproduces

Metrics are computed with the campaign's own `build_import_graph`, imported as the
**only** symbol from `transitions/measure_p7_closure_retention_v1.py`, exactly as
the campaign's `theory/density-prospective-v1/o17_density.py` does. The selector is
therefore structurally incapable of computing a policy outcome — a stronger
guarantee than instructing it not to.

I validated the builder against the published held-out table before selecting
anything:

| package | published m/e | reproduced m/e at today's HEAD |
|---|---|---|
| requests | 19 / 16 | **19 / 16** exact |
| tornado | 74 / 412 | **74 / 412** exact |
| networkx | 583 / 1245 | **583 / 1245** exact |
| django | 906 / 3336 | 906 / **3315** (−21, −0.6%) |
| sympy | 1566 / 13622 | 1566 / **13591** (−31, −0.2%) |

Module counts reproduce **5/5 exactly** and edge counts 3/5 exactly, the two
deltas being sub-1% on the two most actively developed repositories: the builder is
validated. The thresholds 1.5 / 49 / 216 are treated as fixed historical constants
and are neither re-derived nor re-fitted. Every repository in this cohort is pinned
to a commit SHA, so these measurements are exactly reproducible.

## The exclusion list is derived, not guessed

The protocol forbids reusing development/evaluation repositories and says the rival
cutpoints are "integer cutpoints strictly between max observed sound and min
observed unsound counts across 8 calibration+evaluation projects". The 8 are the 3
calibration domains (numpy, scipy, flask) and the 5 held-out packages (requests,
networkx, django, tornado, sympy). The arithmetic closes exactly:

- modules: max sound 24 (flask), min unsound 74 (tornado) → (24+74)/2 = **49** ✓
- edges: max sound 19 (flask), min unsound 412 (tornado) → (19+412)/2 = 215.5 → **216** ✓

That both frozen thresholds fall out of this set is the evidence that the exclusion
list is complete rather than a guess. All 8 are excluded by project name and by
repository slug.

## Blindness argument

1. **The ordering was fixed before any measurement.** Candidates are enumerated
   from the public PyPI download-rank list
   (`hugovk.github.io/top-pypi-packages`), most-downloaded first. Download rank is
   independent of retention-policy soundness, which is only observable by running a
   policy over commit history.
2. **No discretion at the qualifying step.** The rule is "accept the first 10
   qualifying candidates per stratum in rank order". Stratum assignment is a pure
   function of two integers.
3. **Every candidate examined is recorded**, accepted or rejected, with its
   measured counts, in `CANDIDATES_EXAMINED_V1.jsonl`. The rejects table is what
   makes this auditable.
4. **The selector cannot see outcomes.** It imports one graph-building function and
   no policy code.
5. Shards measure only; the acceptance rule is applied once at merge time over the
   union sorted by rank, which is identical to a single sequential pass.

**Scale.** 1,749 candidates examined down to download rank 2,063; 1,054 usable.
The cohort is complete: 10 + 10.

**A disk failure that would have biased stratum B, and its repair.** The 10-way
parallel sweep filled the disk while cloning very large generated monorepos
(`google-cloud-python`, `azure-sdk-for-python`), and 28 candidates failed with
`No space left on device`. Those failures were **not random** — they hit large
repositories, which is exactly the population stratum B draws from, and 23 of them
sat at ranks *below* accepted members, so silently dropping them would have broken
the "first 10 in rank order" rule in the one stratum where it mattered.

All 28 were re-measured one at a time with a **sparse checkout** (only the package
subtree fetched) behind a free-space guard. One of them, **`faker` at rank 406**,
qualifies and is now in the cohort; the other 27 were excluded by the same
package-directory rule applied to every other candidate. **Zero candidates remain
unmeasured for disk reasons**, and the repair rows supersede the failure rows so
each project is counted once.

**One revision, disclosed.** The first package-directory detector matched only the
PyPI project name, and silently dropped 21 of the 90 candidates it saw, whose import name
differs from their project name. I replaced it with a general rule (name match,
else the unique top-level package, else reject as ambiguous) and re-ran from
scratch. The revision was made before any outcome existed anywhere, and
`package_dir_not_found` is independent of soundness — but it changed which
candidates were eligible, so it is recorded rather than buried. The superseded log
is kept as `CANDIDATES_EXAMINED_V0_NARROW_DETECTOR.jsonl`.

## A measurement artifact in the campaign builder, and why it is bounded

While screening the cohort I found a real artifact in the campaign's builder, and
it is worth recording because any future cohort must screen for it.

`module_name` names modules relative to the **repo root**. So a package in a `src/`
layout whose internal imports are **absolute** (`from pkg.x import y`) has every
module named `src.pkg.*`, no import target matches, and it measures **zero**
internal edges. Observed live: `textual` (247 modules, 0 edges), `cfn-lint`
(564 modules, 0 edges).

**The threat is one-directional, and that bounds it completely: the artifact can
only *lower* measured density.** It therefore cannot admit anything to the dense
stratum, so stratum A needs no screening at all; it can only falsely admit to the
**sparse** stratum.

So the screen is part of stratum B's **eligibility criteria**, applied uniformly in
rank order, not an afterthought on the accepted set: a candidate qualifies for
`large_manyedge_sparse` only if its density is below 1.5 under **both** the campaign
convention **and** a re-rooted cross-check that removes the `src.` prefix. The screen
is structural and outcome-blind — it re-measures an import graph and consults no
policy, no history, no outcome.

**It caught one.** `transformers` measures density 1.290 under the campaign
convention but **1.586** re-rooted, crossing the threshold: it is genuinely dense
and was admitted to the sparse stratum only because absolute imports failed to
resolve. It is rejected from the cohort and the next qualifying candidate in rank
order takes its place. Every rejection and its measurements are recorded under
`artifact_screen` in `COHORT_V1.json`.

I first hypothesised something stronger — that a layout confound reached the
original result, since in the campaign's 8 projects both *sound* packages (flask,
requests) are `src`-layout while all six *unsound* ones are flat. I tested it
**against the graph builder** and that mechanism is refuted: measuring flask and
requests from the repo root and from the `src` root gives identical counts (19/16
and 24/19), because both use *relative* imports, which resolve regardless of prefix.

**CORRECTED 2026-08-29 — the confound is real; it just lives one level down.**
The earlier sentences "I tested it and it is refuted" and "the frozen thresholds are
unaffected" were wrong, and are withdrawn. Reading the outcome code
(`measure_p7_closure_retention_v1.py`) shows `donor-coarse` buckets a module by
`m.split(".")[1]`. For a `src/` layout every module of package P is named
`src.P.x`, so that component is `P` for *all* of them: the bucket set collapses to
`{P}` and the policy reopens everything. It has degenerated to always-reopen, which
cannot falsely retain, so such a package is "sound" for a reason unrelated to
density, module count or edge count. Verified: `requests` preserve=0 (reproducing
the campaign's own held-out row), `flask` preserve=0, and the flat control
`tornado` preserve=32,285. Both of the campaign's "sound" packages are therefore
degenerate. See `STUDY_NOTE_V1.md` for what this does to the threshold's support.

The builder is deliberately **not** "fixed": the thresholds were derived under its
convention, so changing it would make these numbers incommensurable. This is a
screen, not a correction.

*Known incompleteness:* the artifact can also silently **suppress** a candidate — a
genuinely dense package measuring 0 edges is passed over for stratum A. The two
observed cases are far too large for stratum A, so no admitted member is affected,
but a small `src`-layout package with absolute imports could have been missed. This
is a completeness limit, not a validity one: stratum A's members all qualify
legitimately in rank order.

## Structural caveat the outcome phase should know

Four of the ten `large_manyedge_sparse` members are **generated API-client SDKs** —
`openai`, `anthropic`, `cohere`, `llama-cloud` — whose large flat module counts and
few internal imports are a property of code generation. The other six
(`setuptools`, `xlsxwriter`, `faker`, `streamlit`, `spacy`, `cdp-use`) are ordinary
hand-written packages, so the stratum is mixed rather than dominated.

This is a consequence of blind selection, not a violation of it: large *and* sparse
is an intrinsically rare combination, and generated clients are one place it
naturally occurs. But generated code may differ from hand-written code in ways that
bear on retention soundness, so whoever runs the outcome phase should treat SDK
membership as a possible stratum-level confound — and can, if it matters, compare
the four against the six. Stratum A has no comparable skew.

This cohort also supplies, incidentally, the thing the density manuscript names as
its weakest point: it says "a second small-and-dense package would strengthen it,
and none is reported here". Stratum A contains ten.

## What I could not get

- `CANNOT_CHECK` — **exact historical re-measurement of the 5 held-out packages.**
  `HELD_OUT_DENSITY.json` records no commit SHAs, so the two edge-count deltas above
  cannot be attributed between builder drift and repository churn. Module counts
  matching 5/5 exactly makes builder infidelity unlikely, but that is an inference,
  not a check.
- **No outcome, by design.** The `donor-coarse` policy was not run on any
  repository in this cohort. Scoring the three rules requires the campaign's policy
  runner over commit history and belongs to a separate, later step under the
  protocol's gate (`>=15/20` overall, `>=7/10` per stratum).
