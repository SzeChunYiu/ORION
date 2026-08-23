# P11–P13 top-tier theory result receipt V1

**Run:** GitHub Actions `32644815784`  
**Artifact:** `p11-p13-top-tier-theory-v1`, artifact ID `9494570377`  
**Artifact ZIP SHA-256:** `5f5ab973d0dcb64f9c0bdaa8e023519918bb499bb274076f3827d08a8593ea40`  
**Replay:** `P11_P13_TOP_TIER_THEORY_V1_BYTE_REPLAY_GREEN`  
**Programme terminal:** `P11_P13_TOP_TIER_THEORY_V1_GREEN`

## P11 result

Terminal: `P11_TOP_TIER_THEORY_V1_GREEN`.

Independent finite checks confirmed:

- arbitrary finite query-matrix exact witness rank `3`, excluding exact universal linear access dimension `1` or `2` for that family;
- approximate singular-spectrum witness with squared spectrum `(25,9,1)` and `epsilon^2=1.1` has effective approximation rank `2`;
- relative no-answer-laundering parity witnesses for `k=2,3,4`: no constant or single selected coordinate realizes parity, while the registered compositional decoder does;
- distribution-sensitive compile/cache versus universal-materialization example crosses at horizon `H=2` under the frozen costs;
- no-cache closed-form crossover threshold is `5/3`.

These checks bind the finite witnesses accompanying T11.1–T11.3; they do not replace the still-required learned compiler and real-system resource study.

## P12 result

Terminal: `P12_TOP_TIER_THEORY_V1_GREEN`.

Independent finite checks confirmed:

- adaptive resource-location value `1` versus best fixed-locus value `1/2` in the registered strict two-signal witness;
- cross-difference examples `+1`, `-1`, `0` for complementarity, substitution and additivity, invariant to separate affine per-locus cost terms;
- exhaustive `3,375` assignments for the registered marginal-value error witness respected the `2 epsilon` regret bound, with maximum observed regret exactly `2` at `epsilon=1`.

This closes the bounded decision-theory sanity layer for T12.1–T12.3. Open-weight, verifier-backed and cross-domain allocator transfer remain external promotion gates.

## P13 result

Terminal: `P13_TOP_TIER_THEORY_V1_GREEN`.

Independent finite checks confirmed:

- a compact state can support lower responsibility `r1` while failing stricter responsibility `r2`;
- identity state supports the stricter responsibility and therefore the coarser one under partition refinement;
- a representation transport can preserve `r1` support while revoking `r2` support;
- responsibilities with mutually non-refining partitions remain incomparable;
- prospectively fixed Hoeffding calibration with `alpha=0.05`, `delta=0.05` gives upper risk `0.043702...` for `5/1000` collisions (passes), `0.172387...` for `5/100` (fails), and `0.273666...` even for `0/20` (fails), demonstrating that zero observed failures do not self-certify low risk.

This closes bounded theory/calibration witnesses only. Real responsibility shifts, semantic-change transport and independent external authority remain pending.

## Authority boundary

None of these GREEN theory terminals is equivalent to `TOP_TIER_SUBMISSION_READY`. They move the theorem obligations forward while preserving external promotion as `CANNOT_CHECK` until the registered real-system evidence exists.
