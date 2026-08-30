# ORION-17 exact mechanism pivot — 2026-08-29

**Base main:** `467133ddd55a415c6d305a5f7b908dc30e72ee20`  
**Historical rule-disagreement terminal:** `NO_DISCRIMINATION`  
**New identity:** `ORION17.CROSS_BUCKET_EXPOSURE_IDENTITY.v1`  
**Scientific authority delta:** `NONE`

## Why this is a new question, not a rescue

The completed density-vs-size study had no varying informative outcome and contained four layout-degenerate SOUND cases. It cannot identify density, absolute size, or the post-hoc layout observation as the scientific mechanism.

The original donor-coarse implementation itself, however, exposes an exact structural identity. This packet derives that identity directly from the frozen instrument source rather than fitting a feature to the V1 labels.

## Exact mechanism

For changed modules `C`, transitive read set `R(m)` and the instrument bucket map `b`, donor-coarse falsely retains exactly

`{m : R(m) intersects C and b(m) notin b(C)}`.

Consequently donor-coarse is universally sound over **all** possible changed-module sets iff no transitive dependency crosses the coarse bucket partition.

For a singleton changed module `c`, the false-retention count is exactly the number of transitive readers of `c` in other buckets. This yields an explicit counterexample whenever the universal certificate fails.

The same algebra proves the previously observed one-bucket `src/` degeneracy: if every module collapses into one bucket, every nonempty change causes donor-coarse to reopen everything, so false retention is zero mechanically.

## New candidate family

The successor freezes four candidates under a new identity:

- `C0_SAFE`: zero cross-bucket transitive pairs — exact universal-soundness certificate under instrument semantics;
- `C1_MAX_EXPOSURE`: maximum singleton cross-bucket reader count;
- `C2_TOTAL_EXPOSURE`: total cross-bucket transitive pair mass;
- `C3_EXPECTED_EXPOSURE`: training-history-weighted exposure, with protected transition frequencies forbidden.

Only C0 is a theorem. C1–C3 require untouched prospective testing.

## Remaining empirical work

Use correctly rooted untouched repositories, exclude the historical 8 and V1 20, freeze the exact instrument and history split before protected outcomes, and report preservation plus unnecessary reopenings alongside false retention. The practical questions are certificate coverage/efficiency and prospective risk ordering—not whether the failed density threshold can be tuned into success.