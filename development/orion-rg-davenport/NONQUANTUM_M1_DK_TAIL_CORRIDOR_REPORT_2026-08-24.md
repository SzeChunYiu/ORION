# Non-quantum math M1 — dual-harness report

Date: 2026-08-24

Owner: `NON_QUANTUM_MATH`

Base revision: `0dc9e07badae039743a6966dd9198586a497d72f`

## Admitted scientific result

For every integer `k>=4`,

`5k+10 <= D_k(C_5^3) <= 5k+11`.

If `D_4(C_5^3)=30`, then `D_k(C_5^3)=5k+10` for every `k>=2`.

The all-`k` authority is the induction written in the frozen protocol. Evaluating the same recurrence through `k=10,000` in both computational derivations is corroboration, not the proof's infinite step.

## Exact evidence identities

- Protocol SHA-256: `fbf7c471fbd2bdf1ceb3717db0c424729971111d4ca229af295b37b8653000b8`.
- Source signed result digest: `7223f3f47d27eacbd6d5d398ef188c7022913e510552c7407bb3f8c71f952261`.
- Source result file SHA-256: `580d244780de9ba9df76f5918575402a8da1bed603676a5a17840895fba87953`.
- Generic signed verification digest: `80bb34bedd4cb935f58fb55371f3d76b2d9376e701b969be8c0e4672e4936dab`.
- Generic result file SHA-256: `3f3f400f29c7e0d31a62e9e005a249bb17355299a4e0f4891d905e429b4b4aa5`.
- Native manifest digest: `e2613e9d98c19a44e8bfb5e6ffd4a012b8f51a4a8d962bb1b16185f5cddea1e3`.
- Dual receipt digest: `f69bde4893351cb1e33da8d2d2538f745cd34280aa3951de2b7a082c3ced5ad2`.
- Dual receipt file SHA-256: `0140bf2eec532f9eaa3d23b4cf79086d8a0e4d74ff3edb4b803696c3c89eca6c`.

Bound parent files:

- `D_2(C_5^3)=20` result SHA-256: `5a0f8eb28ae47067534f001cd9571915ba6ce78bc1fd3a2bfa992f80faf4146c`.
- `D_3(C_5^3)=25` result SHA-256: `4f559c48062d0c0ec6cfce45359445b2c85e718556ef8d0c3581b54510aadd0c`.
- support-frontier result SHA-256: `75662f1beeb208c77b59939385a310acf649f310114bf819cfc5a3be99fe9307`.
- D2 donor-correction SHA-256: `347a6cd967d4716c05aeec5241b454935ce92457075328963b07aaab910fbbde`.
- lower-bound audit SHA-256: `276cada148b2d719bd8996aecf3dfa17a9fc842278387e96930337c6e916886c`.
- prior-art audit SHA-256: `04b93e12f328f2ba4da2b6097d12a806dbdb5cd45e04217d505890f3f2b468f6`.
- D4 protocol SHA-256: `39719afd49ef0f2bb9d82008cc1311847703ae685f961796ca9e27626ebcbf82`.

## Terminal and validation

Source, generic, and native lanes agreed on:

`NONQUANTUM_M1_C5CUBED_ALL_K_GE4_ONE_UNIT_CORRIDOR__D4_30_IMPLIES_EXACT_TAIL_5K_PLUS10`

Generic decision: `ACCEPT_C5_CUBED_TAIL_CORRIDOR`.

Native decision: `ACCEPT_C5_CUBED_TAIL_CORRIDOR`; phase `ACCEPT_RECORDED`; run status `TERMINAL`; two cycles with statuses `ADVANCED`, `TERMINAL`.

The five focused tests passed. The complete dual harness was run four times; source, generic, and dual receipt file hashes were byte-identical on all four runs.

## Recorded adverse execution

The first source execution returned `NONQUANTUM_M1_DK_TAIL_CORRIDOR_REJECTED` with result digest `d23f59217356572eb9193b6818196f87795584ad4071be6ef217cb4c22028b08`. Every mathematical check was true, but the admission expression incorrectly included the deliberately false flag `d4_31_tail_propagation_claimed`. The guard was repaired to require this boundary flag to remain false. No theorem, threshold, parent evidence, or metric changed after the rejection.

## Remaining scientific authority boundary

This iteration does not decide whether `D_4(C_5^3)` is 30 or 31. It does not prove `31 in C_0(C_5^3)`, does not give theorem authority to the local support-23 frontier, and does not infer a permanent upper-line tail from `D_4=31`. The support frontier remains external-replay-required and is unused in this theorem.

The lower bound and recurrence are donor mathematics; exact D2 is donor-derived and is not claimed as ORION novelty. No novelty, venue, quantum, CI, or physical-resource authority is admitted. The decisive next gap is exact D4/C0, not additional recurrence rows.
