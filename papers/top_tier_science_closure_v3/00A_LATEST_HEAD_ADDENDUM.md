# Latest-head addendum

**Current main reviewed:** `1657c1f5f3b7152f71c6e0e72fedc2bfa439ef98`  
**Incremental range:** `703b87db22dce3981f13b407b56f4a656310632f..1657c1f5f3b7152f71c6e0e72fedc2bfa439ef98`  
**Commits reviewed:** 5  
**Scientific authority delta of this addendum:** NONE.

This addendum supersedes any statement elsewhere in this package that PR #1739 is open or that its ORION-13 analysis is pending. The remaining ORION-01–25 dispositions are unchanged except for the integrity/package refinements below.

## Changes and consequences

### ORION-13 analysis is now current main

PR #1739 merged as `a888bb4c7c0905609653ba57e79f47bcea70f6f8`. The committed battery reproduces the published aggregates and reports:

- confirmatory holdout: `b=6,c=0`, exact two-sided McNemar `p=0.03125`;
- disjoint initial holdout: `b=4,c=0`, `p=0.125`, not significant alone;
- ten total discordant pairs, all favouring the governed mapping;
- `pooled_significance_test = NOT_COMPUTED_BY_PROTOCOL`;
- the flat predicate comparator is constant always-merge on both holdouts because every pair is predicate-equal;
- ten listed coordinates never differ and all separating cases are polarity-driven; a predicate/modality/polarity reduced rule matches the full mechanism on all 64 cases.

The scientific consequence is claim narrowing, not promotion: the evidence supports polarity-sensitive obstruction detection on structured projections. It does not establish broad ten-coordinate necessity, a competitive-baseline advantage, raw-text integration, or external semantic utility. The journal package remains superseded: the current built manuscript is 47 pages and the packaged PDF is 20 pages, so re-rendering and a fresh claim-to-PDF audit remain mandatory.

### Programme drift debt is now explicit

`432578ae6c421f3df9f419eb1b3fa8db635f78a5` records pre-existing content-binding debt for ORION-11, ORION-12, ORION-13 and ORION-20. The debt must be reconciled causally; bulk digest regeneration is forbidden.

`7b78a59ced7ce8731d96f28bcced55445e8ce344` adds ORION-05 to the journal-package staleness ratchet. Its apparent 40/40 missing count is a path-convention artefact; when resolved from repository root the actual state is 25 matching, 12 drifted and 3 absent. The next repair must settle the path convention and missing artifacts, not claim forty vanished files.

### ORION-16 binding checker is repaired but one fail-closed gap remains

`decbd670f95599cace6fdffa9b13dd4ea5aafc02` makes the subject-commit check use the same non-self-referential path set as the writer and re-pins ORION-16 to permanent main ancestor `87e2bcb33`, with all 80 compared files matching. This closes the specific writer/checker mismatch. It does not close the programme-level gap that an unresolvable subject commit still degrades to non-failing `CANNOT_CHECK`; that condition needs a regression test and fail-closed release rule after remaining pins are reconciled.

### ORION-11 rubric bytes are loadable again; identity naming remains inconsistent

`1657c1f5f3b7152f71c6e0e72fedc2bfa439ef98` re-pins the adjudication rubric body after the sanctioned namespace rename, and the verified loader now succeeds. A separate naming inconsistency remains: the loaded `rubric_id` is still `P1.adjudication-rubric.v1` while the document header says `ORION-11.adjudication-rubric.v1`. This is an identity-governance repair, not a reason to alter the rubric's scientific content or the ORION-11 retraction.

## Current authority rule

Use `1657c1f5f3b7152f71c6e0e72fedc2bfa439ef98` as the latest reviewed main head. Use the per-paper files for designs and boundaries, with this addendum controlling any conflict. None of the five incremental commits establishes external replication, top-tier acceptance, production transfer, or protected Task-3 closure.
