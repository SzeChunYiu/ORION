# QG-13 automatic normal-form theorem miner — protocol V1

Date frozen: 2026-08-21.
Parent: ORION-QG #740. Lane: #767.
Frozen base: `beac25450b5d95dd766345dcee872fed840f833b` (canonical ORION `main` at freeze).
Authority ceiling: recovery evidence only; no novelty, paper, R6, or physical-advantage authority.

## Question

Can ORION extract a bounded compiler normal-form theorem packet from **production transition/resource semantics** when the edit is supplied but the conserved quotient dimension, resource-safety cone, and support bound are not?

V1 is recovery-only. It must independently rediscover already-earned R6M/R6I theorem structure before any genuinely new edit is admitted.

## Frozen edit grammar

Exactly two edits:

1. `E_R6M_ZERO_FRAME_LETTER`: zero one selected R6M local frame letter; all other local letters remain fixed.
2. `E_R6I_ZERO_BLOCK_GENERATORS`: zero both independent local generators of one R6I rank-2 block; recompute the dependent third letter by production Pauli multiplication.

No rewrite-rule synthesis is performed. Quartz/QSymb/superoptimization-style rule discovery is donor territory.

## S1 — transition quotient inference

For each edit, enumerate the complete production local option table, compare production state delta before/after, compute the exact GF(2) span, and report rank/basis/change-set statistics. **No expected rank is passed to this stage.**

- R6M domain: `4^7 = 16384` local options for each of six frame slots.
- R6I domain: `4^6 = 4096` local options for each of two block deletions.

## S2 — resource safety inference

### R6M

Re-enumerate the complete R6S local single-letter exchange domain, preserving semantically inert partner/Tag coordinates:

`2 resource kinds × 3 F3 positions × 3 zeroed letters × 4 partner × 4 Tag × 4 target × 4 otherA × 4 otherB = 18432`.

Infer the largest realized F3 increase separately for central/noncentral deletion. The induced linear objective cone is derived from the enumeration; the coefficient `2` is not supplied.

### R6I

Enumerate the complete local block-deletion domain:

`3 central choices × 15 nonzero generator-letter pairs × 4^3 target letters × 4^2 Tag letters = 46080`.

Recompute the dependent third letter exactly and record unit-objective `Delta C`. The maximum is discovered, not supplied.

## S3 — theorem packet

A candidate packet may be emitted only when:

- the edit changes a finite GF(2) quotient of inferred dimension `d`;
- the admitted global syndrome is nonzero, so a zero-sum dependence subset is proper;
- the edit removes active support while preserving the quotient;
- the local resource delta is non-increasing in the inferred objective region;
- equal-cost edits strictly reduce the support measure.

V1 uses the donor-owned linear-dependence schema over `F_2^d`: more than `d` active vectors are dependent, so a proper zero-sum subset can be deleted. Linear algebra receives zero novelty credit.

## S4 — parent scoring only after synthesis

After the candidate packets are synthesized, score them against canonical parent evidence already on `main`:

- R6M: `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` and QG-2 objective controls;
- R6I: `QG1_RANK2_ALL_N_RESULTS.json`.

Parent evidence may not select a rank, basis, resource maximum, or cone facet.

## Three-process harness discipline

The generic ORION ResearchWorkspace executes three isolated Python capability calls:

1. production theorem miner;
2. generic independent verifier, which reconstructs the R6M/R6I state equations without importing production `_DELTA` arrays;
3. native ORION-Q verifier, which checks production-family identities, parent boundaries, and the non-authorizing claim ceiling.

A dual receipt binds all three process request/result digests. Deterministic replay of the theorem miner is mandatory.

## Honest terminals

- `QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS`
- `QG13_QUOTIENT_OR_RESOURCE_INFERENCE_REFUTED`
- `QG13_PARENT_RECOVERY_MISMATCH`
- `QG13_GENERIC_NATIVE_DISAGREEMENT`
- `QG13_CANNOT_CHECK`

Every V1 terminal carries `new_theorem_authority=false` and `novelty_authority=false`.

## Next gate

Only a protected positive V1 recovery permits V2 to freeze a genuinely new edit. First target: combined R6I support deletion for QG-9 #762, where support-five tightness remains open.
