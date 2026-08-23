# QG-7d J7 — confirmatory PA pinned comm-s2 theorem packet

Date: 2026-08-21
Issue: #836
Base lineage: `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`
Parent QG-7c digest: `0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6`
Exploratory derivation disclosure: issue comment `5374778547`.
Status: **FROZEN BEFORE PROTECTED CONFIRMATORY J7 OUTCOME.**

This packet is confirmatory, not a pre-blinded discovery. The J6/J7 grammar was derived after exploratory inspection of the exact PA residual domain. The theorem claim, if earned, rests on complete finite-domain proof plus independent reconstruction, not on prospective statistical inference.

## Parent PA domain

Reconstruct the exact QG-7c T4b PA sector for all

`ja in {0,1}, R_b in {1,2}, R_a in {1,2}, p in {1,2}`

and all `(coreB,envB,coreA,envA)` states.

Required parent fingerprints:

- total PA failures = `103048`;
- `ja=0`: 8 parameter cells x `12431` failures each;
- `ja=1`: 8 parameter cells x `450` failures each;
- aggregate PA census inherited from QG-7c:
  - delta1 = `97072 + 3600 = 100672`;
  - delta2 = `2376`.

The parent G1–G4 formulas must be reconstructed from the committed QG-7c transition/F3 algebra, not from the serialized failure list.

## J6 — global anchored Tag relocation with branch assignment

For each parent-failing PA state, recover the six target letters on the two touched coordinates `(b,a)` from the abstract old residual letters and the frozen old frames.

Enumerate both relocation coordinates `q in {b,a}`. For each:

1. choose one nonidentity local shared-Tag letter `s in {X,Y,Z}` at q;
2. for each of the three blocks independently choose one of the two local nonidentity letters anticommuting with s as its label-1 frame;
3. set the label-0 frame of every block to s;
4. independently choose each block target permutation `sigma_j in {0,1}`;
5. put identity frames on the other touched coordinate;
6. compute exact two-coordinate F3 change against the parent residual state;
7. use the exact structural change `old pinned PA structural cost 6 -> D+ structural cost 2`, but derive/check these values from the frozen objective primitives.

J6 is therefore a complete two-coordinate D+-normalization library with global Tag relocation and independent block branch assignment.

Exploratory replication fingerprint: J6 left 42 residuals over the complete PA parent-failure domain. This number is **not** sufficient for theorem authority, but a confirmatory run should reproduce it or fail closed as a derivation mismatch.

## J7 — B′ handoff on J6 residuals

For every state still positive under `min(parent G1–G4, J6)`, construct its exact two-qubit target triple from the recovered target letters and evaluate the **unchanged committed B′ family** from QG-5b.

Requirements:

- B′ may use Tag at b with home a or Tag at a with home b;
- anchored/phantom per-block options and independent `sigma_j` are exactly the frozen QG-5b grammar;
- at least one phantom block is required, as in B′;
- every selected B′ member must pass the committed proof-carrying witness verifier;
- compare absolute B′ cost to the exact original pinned PA configuration cost (`old two-coordinate F3 + structural 6`).

Strong PA closure condition:

`min(parent G1–G4, J6, B′) <= 0`

for every one of the 103,048 parent PA failures.

Expected exploratory outcome: zero final residuals. Protected confirmation must recompute, not read, that result.

## Composition / all-n PA authority

A J7 terminal state is either:

- D+ (zero comm-s2 blocks), or
- B′ (anchored/phantom blocks, no label-0 comm-s2 block).

Thus the selected pinned comm-s2 block is eliminated. J7 touches only the two PA coordinates `(b,a)` and its exact F3 domain contains the full adversarial local environment of all three blocks at both coordinates. No other qubit is modified.

Therefore the PA exchange strictly decreases `#comm_s2` and composes across arbitrary n by the same qubit-local replacement argument used by QG-7c, provided the machine checker verifies the terminal shape predicate and no outside-coordinate mutation.

This authorizes **PA subfamily all-n closure only**. PP phantom-home and mutually-pinned comm-s2 chain sectors remain OPEN.

## Independent generic ORION

Generic ORION must independently rebuild phase-free local Pauli multiplication, F3, parent G1–G4 PA transition tables, J6, and the two-coordinate B′ grammar. It must reproduce:

- 103,048 parent PA failures;
- parent delta histogram `100672 x +1`, `2376 x +2`;
- the exploratory J6 residual fingerprint (42) as a reproducibility check;
- zero J7 final residuals.

No production QG-7c/J6 transition table may be imported by the generic verifier.

## Native ORION-Q authority

Allowed positive decision:

`ACCEPT_PA_ALL_N_CLOSURE`

with mandatory fields:

- `PA_ALL_N=true`;
- `PP_ALL_N=false`;
- `CHAIN_ALL_N=false`;
- `GLOBAL_BDOUBLEPRIME_COMPLETENESS=false`.

## Positive terminal

`QG7D_PA_PINNED_COMM_S2_CLOSED_ALL_N_MACHINE_CHECKED__PP_CHAIN_OPEN`

Honest alternatives:

- `QG7D_J7_CONFIRMATORY_REPLICATION_MISMATCH`;
- `QG7D_J7_PA_RESIDUAL_REMAINS`;
- `QG7D_GENERIC_NATIVE_DISAGREEMENT`;
- `QG7D_CANNOT_CHECK`.

## Authority boundary

No global B″ completeness, R6, novelty, chemistry, protected-subject or physical quantum-advantage authority follows. The only earned object may be the all-n PA pinned-comm-s2 normalization lemma under the frozen unit-support R6M grammar.