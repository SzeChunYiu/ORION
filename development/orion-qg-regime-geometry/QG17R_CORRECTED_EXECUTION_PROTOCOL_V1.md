# QG-17R corrected phase-sharpness execution — frozen protocol

Issue: #841. Parent scientific freeze: #814. Base: `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.

PR #815 is scientifically VOID as an outcome: its early scanner assumed every 12x12 support1 frame-pair cell admitted a common valid Tag. Current main already contains the corrected exact-family semantics: infeasible cells are `None` and exact cap1 minimizes over feasible cells only. No preliminary strict-count from #815 may be reused.

This successor changes no candidate generator, objective, candidate order, threshold, or claim gate. It executes the current committed QG-17 scanner/verifiers exactly once under protected custody.

Required preflight:
- 12 ordered support1 local frame pairs;
- `0 < TAG_FEASIBLE_CELLS < 144` (proves infeasible cells exist and are represented);
- every A-frame pair has at least one feasible B partner;
- frozen V5 candidate count remains 211,248;
- objectives remain O0, O_tag_out, O_restore_out, O_nc_out exactly as #814.

Allowed scientific terminals are inherited verbatim:
- `QG17_SUPPORT2_PHASE_WITNESS_FOUND_AT_FROZEN_OUTSIDE_OBJECTIVE`;
- `QG17_NO_SUPPORT2_WITNESS_IN_FROZEN_V5_DOMAIN`;
- generic/native disagreement or CANNOT_CHECK.

A positive is only a finite exact phase witness at the named objective. A negative is only a bounded negative on the frozen V5 domain. `GLOBAL_PHASE_BOUNDARY_COMPLETE` must remain false. No novelty/R6/physical-advantage authority.