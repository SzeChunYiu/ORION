# ORION-Q / ORION-QG post-cut freshness adjudication V1

Adjudication date: 2026-08-21
Original portfolio cut: `ca7df1055a43f97eaf8d142a62011c4c261af368`
Current-main refresh point reviewed: `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`

Purpose: decide whether scientific changes merged after the original publication cut materially alter any Q/QG manuscript. This is a freshness decision, not a blanket permission to import every later result.

## Post-cut science reviewed

Current main added, among other implementation/protocol files:
- QG-9 R6I theorem ladder culminating in `QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED`;
- exact intrinsic support number `kappa_R6I = 1` by support-0 infeasibility;
- QG-16 objective-indexed support-1 cone, with global sharpness explicitly `OPEN`;
- QG-6 production conserved-syndrome rank analysis: R6M rank 2 recovers the existing support-2 theorem; R6I rank 5 is only a sound loose upper bound and is superseded as a tight support statement by the QG-9 support-1 theorem;
- QG-17 protocol/code, but no committed QG17 result receipt on the reviewed main point.

Key source receipts:
- `research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`;
- `research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json`;
- `research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`.

## Paper-by-paper disposition

### ORION-01 — NO REOPEN

ORION-01's load-bearing theorem is about the **R6M three-block grammar under the raw support objective**. Post-cut QG-9/QG-16 concern the distinct R6I rank-2 dependent-triple grammar.

QG-6 independently recovers the R6M support-2 scale from a rank-2 conserved-syndrome quotient, but it does not strengthen ORION-01's theorem authority beyond R6S and carries no novelty authority. It is useful explanatory/companion evidence for ORION-09, not required for ORION-01's support-ceiling paper.

**Disposition:** keep ORION-01 on the original evidence cut. Optionally cite QG-6 in Discussion as later independent structural interpretation only if doing so does not distract from the exact R6S proof.

### ORION-02 — NO REOPEN FOR SCIENTIFIC CLAIM

The QG-9 ladder is an additional example of ORION-02's successor discipline: progressively stronger proof systems first stop at looser support bounds, then whole-system Tag relocation closes support 1. However ORION-02 already has enough independent negative/donor/successor chains to establish its bounded methodological case.

Importing the new chain would require re-binding the complete eligible-transition denominator and receipt index. It is not needed to establish the paper's current claim.

**Disposition:** do not reopen ORION-02 merely to add another success story. Mention post-cut continuation only in a dated repository note or future revision after the transition inventory is regenerated.

### ORION-03 — PROSPECTIVE FREEZE REMAINS VALID, WITH CUSTODY RECHECK REQUIRED

The reviewed current-main additions do not include a QG7D or QG15C result receipt. QG-17 has a protocol but no result receipt and is not one of the two frozen ORION-03 additional instances.

**Disposition:** ORION-03-V1/QG-7d and ORION-03-V2/QG-15c remain prospectively frozen relative to the original cut and the reviewed current-main point. Before either Lane A/B execution, recheck that no result-bearing QG7D/QG15C receipt has appeared on any authority-bearing branch intended to supply the deferred outcome. If an outcome becomes visible before instrument receipts freeze, that instance is contaminated and must terminate rather than be backdated.

### ORION-04 — NO REOPEN

The post-cut additions are quantum compiler theory and do not change ORION-04's exact-synthetic typed/scoped-state experiments or their donor boundary.

### ORION-10 — NO REOPEN

ORION-10's load-bearing object is static forecasting for the R6M/TARE support-two family and the exact 10<11 refutation/repair sequence. QG-9/QG-16 concern R6I and do not alter the R6M R6S theorem, the QG5 refutation, or the B-prime/F2 repair.

QG-6's R6M rank-2 quotient is an explanatory cross-check, but ORION-10's certificate does not require it.

**Disposition:** keep ORION-10 on original cut; QG-6 may be a companion structural citation, not certificate authority.

### ORION-09 — **REOPEN REQUIRED**

ORION-09 is explicitly a cross-family regime-geometry/framework paper. The new R6I results materially change the strongest available story:

1. Earlier fixed-Tag/local edit proof systems progressively reached support <=4, <=3 and <=2 but did not establish tightness.
2. A whole-system edit—relocating/rebuilding the shared Tag after localizing each block to one anticommuting core—proves `C_DP = C_cap1` for every n in the frozen R6I grammar.
3. Support 0 is infeasible, so the intrinsic support number is exactly `kappa_R6I = 1`.
4. QG-16 then derives an objective-indexed all-n cone in which the support-1 certificate continues to hold:
   - `2*t_nc >= 5*t_r`;
   - `t_c+t_nc >= 5*t_r`;
   - `2*t_nc >= 2*t_r+2*t_tag`;
   - `t_c+t_nc >= 2*t_r+2*t_tag`.
   Under `t_c <= t_nc`, the certificate reduces to two halfspaces recorded in the receipt.
5. Outside the cone means only **this proof certificate does not apply**; global boundary sharpness remains OPEN.
6. QG-6 supplies a more general syndrome-dimension upper-bound principle. It exactly recovers the R6M rank-2/support-2 relationship, while its R6I rank-5 bound is loose relative to the later exact `kappa_R6I=1`. This is itself instructive: conserved-syndrome dimension can certify a safe search/support ceiling without characterizing the intrinsic optimum.

These additions strengthen ORION-09's framework claim that a regime-geometry object contains multiple logically distinct components: tight intrinsic support, proof-system-dependent upper bounds, objective-indexed validity regions, exact counterexamples and representation-dependent boundary descriptions.

**Disposition:** ORION-09 must receive a V3/current-main synchronization before second review. Do not submit V2 as the final scientific manuscript.

## Publication-cut policy after adjudication

A single portfolio cut is no longer scientifically optimal.

- ORION-01/ORION-02/ORION-03/ORION-04/ORION-10 retain the original frozen cut for their current manuscript evidence, with explicit later-work freshness notes where needed.
- ORION-09 receives a paper-specific refresh cut at `main@c5ba39fef4f25c46de5fb69bf07f50530f4693ca` and must bind only the named new receipts above plus its previously authorized evidence.
- Future current-main advances do not automatically enter any manuscript. They trigger the same freshness test: **does this change a headline claim, its strongest counterexample/donor, or the scientific boundary?**

## Anti-chasing stop rule

Do not reopen a paper simply because a new related result exists. Reopen only when the new result:
- falsifies or strengthens a headline claim;
- changes the nearest-work/novelty boundary;
- replaces a finite/loose statement with materially stronger authority;
- changes a limitation that affects the paper's interpretation.

By that rule, only ORION-09 reopens in this freshness round.
