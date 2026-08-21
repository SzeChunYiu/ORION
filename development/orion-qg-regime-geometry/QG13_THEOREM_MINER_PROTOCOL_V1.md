# QG-13 automatic normal-form theorem miner — protocol V1

Date frozen: 2026-08-21.
Parent programme: ORION-QG #740. Lane: #767.
Stacked parent branch: `shadow/orion-qg-qg8-objective-support-phase` after protected QG-8 receipt commit `5ff775c09130b723a93a17342e7b49fd6bb6fec7`.
Authority ceiling: candidate theorem extraction only; no novelty, paper, R6, or physical-advantage authority.

## Question

Can ORION infer a bounded quantum-compiler normal-form theorem packet from **production transition/resource semantics** when the edit template is given but the quotient dimension, resource cone, and support bound are not?

This tranche is a recovery control only. It must recover already-earned R6M/R6I results without importing the parent proof implementations. A successful recovery authorizes a later new-theorem attempt; it is not itself novelty.

## Donor / novelty freeze

V1 is frozen against the following zero-credit parent territory: Quartz-style automatic generation and theorem-prover validation of quantum rewrites; PLDI-style synthesized quantum-circuit optimizers; 2026 QSymb compact symbolic rewrite synthesis; VOQC/CertiQ/Giallar compiler verification; CEGIS/equality-saturation/superoptimization; and generic polyhedral or sparse-support mathematics. The V1 recovery terminal earns no novelty credit. The only candidate future residual is automatic extraction of a proof-carrying *normal-form theorem packet* from production transition/resource semantics after the edit is already specified.

## Frozen edit grammar

Exactly two edit templates are admitted in V1:

- `E_R6M_ZERO_FRAME_LETTER`: choose one of the six R6M frame slots at one qubit and replace its non-identity local letter by identity; partner frames, Tag, targets, permutation, centrals, and all other qubits are unchanged.
- `E_R6I_ZERO_BLOCK_GENERATORS`: choose one R6I rank-2 block at one qubit and replace both independent generator letters by identity; the dependent third local letter is recomputed by the production Pauli product; Tag pair, targets, permutation, centrals, other block, and other qubits are unchanged.

No rewrite-rule synthesis is performed. Quartz/QSymb-style rewrite discovery is donor territory.

## S1 — transition quotient inference

For each production edit:

1. enumerate the complete local option table used by the production exact DP;
2. compute `change = delta_before XOR delta_after` for every local option;
3. compute an exact GF(2) basis and rank from the realized changes;
4. report basis bitmasks, changed-bit union, unique change count, and domain size.

No expected rank is passed to this stage.

R6M production domain: all `4^7 = 16384` local options `(RA0,RA1,RB0,RB1,RC0,RC1,S)` and all six frame slots.
R6I production domain: all `4^6 = 4096` options `(RA0,RA1,RB0,RB1,S0,S1)` and both block deletions.

## S2 — resource safety inference

### R6M

Enumerate the complete R6S single-letter exchange context, including semantically inert partner/Tag letters so the exact frozen domain is preserved:

`2 resource kinds × 3 F3 slot positions × 3 zeroed letters × 4 partner × 4 Tag × 4 target × 4 otherA × 4 otherB = 18432`.

Record exact resource vector after-before:

`(Delta U_c, Delta U_nc, Delta F3, Delta Tag, Delta Rot)`.

Derive the linear nonincrease cone from the worst realized `Delta F3` separately for central and noncentral deletions. The analyzer must obtain the facet coefficient from the enumeration; `2` is not supplied as an expected value.

### R6I

Enumerate the complete block-deletion unit-objective domain:

`3 central choices × 15 nonzero generator-letter pairs × 4^3 targets × 4^2 Tag letters = 46080`.

Recompute the dependent third letter exactly and record scalar unit-objective `Delta C`. No expected maximum is passed to the enumeration.

## S3 — theorem packet synthesis

A candidate theorem packet may be produced only if:

- transition changes form a finite GF(2) quotient of inferred dimension `d`;
- the production/parent acceptance condition supplies a nonzero global syndrome coordinate, making any zero-sum dependence subset proper;
- the edit removes active support and preserves the inferred quotient;
- local resource deltas are non-increasing in the reported objective region;
- ties strictly reduce support in the proof schema.

V1 proof schema: over `F_2^d`, more than `d` active syndrome vectors are linearly dependent. A zero-sum proper subset can therefore be deleted. Linear dependence itself receives zero novelty credit.

## S4 — parent recovery opened only after synthesis

After theorem packets are frozen in memory, read parent receipts only to score recovery:

- R6M: `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json` and committed QG-8 result `QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json`.
- R6I: canonical `QG1_RANK2_ALL_N_RESULTS.json`.

Recovery requires the synthesized packet to match the parent support bound/objective cone, but the parent files may not be used to choose a rank, basis, resource bound, or facet.

## Honest outcomes

- `QG13_AUTOMATIC_THEOREM_MINER_RECOVERS_R6M_AND_R6I_PARENT_THEOREMS`
- `QG13_QUOTIENT_OR_RESOURCE_INFERENCE_REFUTED`
- `QG13_PARENT_RECOVERY_MISMATCH`
- `QG13_COMPOSITION_CONDITION_MISSING`
- `QG13_CANNOT_CHECK`

## Dual harness

Generic ORION harness runs the production analyzer and a separately implemented verifier that reconstructs the DP state equations without importing production `_DELTA` arrays. It independently recomputes the resource domains.

Native ORION-Q campaign sees only serialized analyzer/verifier receipts and may record `ACCEPT_RECOVERY` or `REJECT`. It cannot authorize novelty or a new theorem.

## Next gate after successful recovery

Only a positive protected V1 recovery permits V2 to freeze a **new edit template**. Priority target: combined R6I support deletion from QG-9 #762, because support-five tightness remains open.
