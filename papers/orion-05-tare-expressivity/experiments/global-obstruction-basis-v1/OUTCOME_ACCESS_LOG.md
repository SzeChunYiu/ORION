# Outcome access log — ORION05.GLOBAL_OBSTRUCTION_BASIS.v1

- **First outcome access:** 2026-08-28 ~20:25Z, by the orchestrating session,
  via `tail` of two census task logs (`census_0.log`, `census_100.log`)
  during a throughput diagnosis while the array was running. Exposed fields:
  per-instance `outcome`/`gap` for instances 0, 1, 2000, 2001.
- **Chronology:** strictly AFTER the prospective-clarifications commit
  `c8f83be9e` and the independent-checker commit `2c2c94ac7` (both pushed
  before the access). The clarification window is therefore closed as of
  this access: no further predicate, threshold, terminal, decision-order,
  or clarification changes are admissible for this campaign.
- **Steering boundary:** no execution parameter was changed after access;
  the census array and controls job continue exactly as submitted
  (3551911, 3551909). Grading happens only via the frozen decision order
  and the independent checker.
