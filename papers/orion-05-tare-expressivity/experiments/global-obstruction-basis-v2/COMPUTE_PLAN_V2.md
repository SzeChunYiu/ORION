# ORION05.GLOBAL_OBSTRUCTION_BASIS.v2 — Stage 1 compute plan (DESIGN; LUNARC execution only)

**Reviewed base:** `e19a3b7cd0140d1f413e802a1188a2948726df6f` — `main` is at that commit
unchanged, so no rebase was required.

**HARD CONSTRAINT, inherited from the v1 plan and re-affirmed here:** no control or census
solve runs on the Mac. Local use is limited to `--smoke`, which performs **zero** solver
instances. This constraint was tested rather than assumed: a local attempt at the three
Stage 0 controls held one core at 100% for over two minutes on six solves and was killed.

## Domain, verified

`combinations_with_replacement(1..15, 6)` = 38,760, minus the 5,005 all-distinct sets =
**33,755** repeated-target multisets. `--smoke` recomputes this and asserts it equals the
protocol's figure. The confirmatory 5,005-row distinct-target domain is not touched by this
stage.

## Cost — this is the finding that matters before anyone queues it

The v1 plan measured a single `max_support=2` solve at **>100 s locally, with an unknown
tail**, and ran the 5,005-row census as 334 array tasks at 8 h walltime for a
**~600 core-hour** request.

**Stage 1's domain is 6.7× that census.** Same per-instance cost, so:

| scenario | per-instance | total |
|---|---|---|
| at the v1 observed floor (~100 s) | 100 s | **~940 core-hours** |
| at the v1 array timeout (1,800 s) | 1,800 s | **~16,900 core-hours** |

That is between 1.6× and 28× the entire v1 allocation, for what the protocol calls a
*control-discovery* stage. It should not be queued as an afterthought to the confirmatory
run, and the estimate should be stated in the allocation request rather than discovered
mid-array.

## What makes it tractable

The protocol's own selection rule is the lever: *"scan in lexicographic order; freeze the
first 3 instances with C1>C2."* Only a prefix of the domain need be solved, and the run can
stop as soon as three positives are frozen. Cost is therefore governed by **how early
positives appear**, not by 33,755.

Two consequences:

- If positives are common, this is cheap and the full-domain figures above never apply.
- If positives are **rare or absent**, the run necessarily walks the whole domain and the
  16,900 core-hour ceiling is live. That case is also the scientifically decisive one, so it
  must be funded rather than truncated — truncating it would convert a real negative into an
  unreported absence.

`--array-chunk` and `--start` keep the scan lexicographic across tasks so the "first three"
rule survives parallel execution: chunks are ordered, and a positive in chunk *k* only
freezes once all chunks `< k` have reported.

## Order of operations, each step gating the next

1. `--smoke` anywhere (zero solves): enumeration and domain-size binding.
2. **Stage 0 controls** on LUNARC: `r6o-16`, `r6o-17`, `r6o-19` must return **4/4, 5/5, 6/6**
   under the all-matchings estimand, demonstrating the historical fixed-matching gap is
   erased. Any deviation → stop with `CANNOT_CHECK_CONTROL_FAILURE`.
3. **Stage 1 scan** in lexicographic chunks, stopping at three frozen positives.
4. Stage 2 freeze and the 5,005-row confirmation run **only** after a separate freeze commit
   for those three controls.

## Theory reading — decided in advance, not after

This stage discriminates two registered candidates, and both outcomes are informative:

- **No positive gap anywhere** → supports **O05-C2** (matching relaxation erases the
  historical gaps) and falsifies **O05-C3** (a gap-preservation class). Terminal:
  `CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS`, and confirmation does not run.
- **Positives found** → they are C3's candidate class, and become the frozen controls.

Neither is a fallback for the other. The protocol forbids relabelling the V1 5,005 rows as
confirmatory, and forbids changing control expectations after confirmatory outcomes.

## Independent optimum

For any row used in a universal-basis claim the protocol requires a **second implementation**
to establish the all-matchings optimum; reusing `solve_six_targets` is explicitly not
independent. That checker is not written yet and is **not needed unless Stage 1 yields
positives** — the requirement attaches to rows entering a basis claim. If Stage 1 returns the
CANNOT_CHECK terminal, no such row exists.
