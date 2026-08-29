# ORION-17 claim-ledger addendum V4.12

**Status:** additive successor record; does not rewrite the frozen V1 package or
`CLAIM_LEDGER_V4.md`.

- Paper: ORION-17 — Epistemic Navigation in Open Worlds
- Claim ID: `ORION-17.V4.12`
- Date: 2026-08-29
- Governing issue: #1701
- Recovered source commit: `69251dd3d17d9aa199243d77b3e419cdec732a2a`
- Scientific-authority delta of this recovery: `NONE`; this file records the
  authority already carried by the recovered prospective packet.

## Claim

On five held-out Python packages from five distinct organizations
(psf/requests, networkx/networkx, django/django, tornadoweb/tornado, sympy),
covering 2,488 commits, 2,265 usable changes and 1,671,821 certificate decisions,
a decision rule fixed **before any held-out outcome existed** — predict
`donor-coarse` unsound iff the package's internal import graph carries at least
1.5 import edges per module — predicted the observed soundness/unsoundness of
`donor-coarse` correctly in 5 of 5 packages.

The registered disambiguator `tornado` (74 modules, 5.57 edges/module) was
predicted unsound by the density reading and sound by a size reading. It was
observed unsound with 12,773 false closure retentions. `exact-containment`
incurred zero false closure retentions in all five packages. This converts the
post-hoc attribution in `ORION17.CLOSURE_CHAIN_COMPOSITION.v1` section 4 into a
prospectively validated, bounded mechanism claim.

## Evidence and ordering authority

The complete evidence object is
`theory/density-prospective-v1/`, with the parent campaign and preserved adverse
history in `theory/chain-composition-v1/`.

- Predictions were stamped at commit `1db5eaa46`; that tree contains no held-out
  result file.
- Commit `9841b15c4` is recorded as the descendant first containing
  `HELD_OUT_RESULT.json`.
- `STAMPED_PREDICTIONS.md`, `HELD_OUT_DENSITY.json`, and `o17_density.py` are
  recorded byte-identical across the pre-outcome and post-outcome commits.
- `independent_checker/check_density_prediction.py` re-derives the verdict from
  recorded files, imports no ORION-17 module, re-runs no campaign, and reserves
  exit code 3 for `CANNOT_CHECK`.
- The separate LUNARC execution is implementation-independent but was performed
  within the same research programme and by the same researcher. It is **not**
  external-investigator verification.

## Forbidden upgrades

This claim does **not** establish any of the following:

1. Transfer beyond Python import graphs under this campaign construction. The
   threshold was calibrated on three domains and validated on five; other
   ecosystems, build graphs, and module granularities are untested.
2. More than one independent density-versus-size disambiguator. `requests`
   repeats the small-and-sparse confound; the separation rests on `tornado`.
3. A model of failure magnitude. False-retention counts span more than two
   orders of magnitude and the claim concerns where failure occurs, not how
   badly.
4. Completion of blueprint section 4.12's naturalistic multi-hop navigation
   study. That differently defined evidence blocker remains open.
5. Reopening the promotion budget spent by issue #1649. The adverse terminal
   `ARBITRARY_CHAIN_THEOREM_ALREADY_EXISTED` remains unchanged and unretracted.
6. Independent corroboration from ORION-16. Any convergent ORION-16 boundary is
   same-programme, same-researcher evidence.

## Relationship to the frozen ledger

`CLAIM_LEDGER_V4.md` is intentionally left byte-identical to `main` because it is
part of the historical V1 binding. This addendum is the authoritative additive
record for V4.12. It must be included in the V2 content manifest together with
the two recovered theory packets and the standalone manuscript. A later
consolidated ledger may incorporate the row only through an explicitly versioned
successor identity; it must not silently rewrite V1 history.

## Filing boundary

The standalone manuscript under `submission/density_prospective/main.tex` is a
bounded result paper. The strongest defensible headline is prospective
validation of a dependency-density mechanism within the registered Python
campaign. A general law, a universal 1.5 threshold, independent replication, or
top-tier promotion of the broader open-world navigation programme is not earned
by these data alone.
