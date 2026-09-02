# ORION05-GF2 two-block grammar protocol V1 (registered before any outcome run)

Date registered: 2026-09-03
Base revision: `4f2a223ae383cb7a999c86538befc8bd28d1357d` (origin/main)
Lane directory: `development/orion-05-gf2-two-block-grammar-2026-09-03/`
Driver: `research/extensions/orion-q/orion05_gf2_two_block_tare2_shared_tag_dp.py`
Parent context: ORION-paper issue #78 (decision (b) separate filing),
issue #47/#48 stretch conditions, ORION issue #1511 (three-round programme
consumed; specialist fallback terminal retained), and
`papers/orion-05-tare-expressivity/manuscript/sections/06-limitations.tex`
("Larger Tag ranks, other block grammars, other term counts, and different
factor rules require separate proofs").

## Aim

ORION-05's frozen theorem O5-P1/O5-P2 fixes the three-block shared-one-bit-Tag
TARE-M2 grammar (six terms) and proves support-two sufficiency with a sharp
support-one threshold (kappa = 2). The block-count / term-count axis is named
as un-proved in the frozen limitations section and is not consumed by
ORION-01, ORION-09/10, or the QG lanes (verified 2026-09-03: QG Paper A owns
Tag-rank growth; QG-13V4 owns the R6I grammar; QG-20 owns R6M rank-kappa
slack; R6I/R6K own dependent TARE-3 rank-two constructions with a two-bit
Tag). This study takes the first exact rung of that axis: the **two-block
(four-term) shared-one-bit-Tag TARE-M2 grammar** under the direct k-restriction
of the frozen R6M objective, and asks whether the support-one threshold
survives the removal of the third block.

## Frozen imported machinery (no semantic reimplementation)

The driver imports `max_r6m_exact_three_tare2_shared_factor_dp` (the frozen
512-state R6M referee) and uses, through that import:

- `p10.h.local_symp`, `p10.h.local_mul`, `p10.h.local_wt` (local Pauli
  algebra) and `p10.codes`, `p10.key_from_codes`, `p10.symp`, `p10.mul`,
  `p10.wt` (global Pauli algebra);
- `canonical_json`;
- the module identity constants as binding asserts (`PARITY_STATES == 512`,
  `ACCEPTING_STATES == (135, 263)`, the module's local tables `_SY/_LM/_LW`).

The two-block grammar itself (letter list, parity map, acceptance set, factor
table, cost scale) is **registered by this protocol as new content**; the
Pauli algebra and the objective's functional form are imported, not copied.
The driver also builds independent brute-force enumerators that use only the
imported `p10` algebra, mirroring the frozen referee's own DP-versus-brute
methodology (`_brute_config_n1` / `_brute_config_n2` in the R6M module).

## Registered two-block grammar (frozen definitions)

Instance: two ordered anticommuting target pairs
`((PA0,PA1),(PB0,PB1))`, each `P` an `n`-qubit Pauli key, plus configuration
`(perm_b, centrals)` with `perm_b in {0,1}` (block-B pair order flip) and
`centrals in {0,1}^2`.

Letters per qubit: `(rA0, rA1, rB0, rB1, s)` — four frame letters and one
shared one-bit Tag letter (base-4 option code, `rA0` most significant;
`4^5 = 1024` options).

Six parity bits (LSB first):
`b0=<rA0,rA1>`, `b1=<rB0,rB1>`, `b2=<s,rA0>^<s,rB0>`, `b3=<s,rA1>^<s,rB1>`,
`b4=<s,rA0>`, `b5=<s,rA1>`; 64 XOR-DP states.
Acceptance: `b0=1, b1=1, b2=0, b3=0, b4!=b5` — states `(19, 35)`.

Objective (direct k-restriction of the frozen R6M form; frame cost charged on
excess support `wt-1`, i.e. the canonical scale on which the frozen referee's
`-18` three-block offset lives; the two-block offset is `12`):

```
cost = sum_q [ sum_{j in {A,B}} ( m0_j*lw(r_j0) + m1_j*lw(r_j1) )
               + 2*lw(s)
               + sum_{k in {0,1}} F2[ lm(p_kA, r_Ak), lm(p_kB, r_Bk) ] ] - 12
m0_j = 2 if centrals_j == 0 else 4 ;  m1_j = 2 if centrals_j == 1 else 4
F2[a,b] = 1 if (a == b and a != 0) else lw(a) + lw(b)
```

`F2` is the two-block restriction of the donor-owned R6L all-equal Restore
common-factor rule (lineage R6L/R6J/R6M). The circuit identities behind the
factor rule and the shared Tag are donor-owned and receive zero novelty
credit; only the finite-domain threshold question is under test.

Target-pair conventions follow the frozen referee: block A keeps canonical
order, block B applies `perm_b`; restore letters are `lm(p, r)` per slot.

## Registered questions

- **Q1 (referee exactness).** Does the 64-state two-block XOR DP agree with an
  independent unrestricted brute enumerator (1024-option enumeration at n=1;
  global s/orientation/pair enumeration at n=2) on the complete n=1
  configuration domain and on registered hostile n=2 panels, per
  configuration?
- **Q2 (support-one threshold at k=2).** On the **complete n=2 instance
  space** (all ordered instances over the complete ordered-anticommuting-pair
  set `M` enumerated by `p10.symp`; `M^2` ordered instances), is the
  unrestricted optimum strictly below the support-one family optimum on at
  least one instance — either as a cost gap or as family infeasibility —
  under both registered support-one families?
  - **F1f** (frames-only): every frame letter of weight <= 1 in both blocks;
    Tag unrestricted.
  - **F1a** (all letters): F1f plus Tag weight <= 1.

Instance optimum = min over the 8 configurations (2 `perm_b` x 4 `centrals`).
The sweep runs all 8 configurations per instance. As a structural consistency
check, the permutation symmetry `cost((PA,PB), perm_b=1, c) ==
cost((PA,swap(PB)), perm_b=0, c)` is asserted for every `c` on a
deterministic 1-in-144 sample of instances (the swap of an ordered pair is
itself in the complete ordered space).

## Registered domains (frozen)

- **D1 complete n=1**: all `6 x 6` ordered instances over the 6 ordered
  anticommuting 1-qubit pairs, all 8 configurations each; DP vs brute per
  configuration.
- **D2 hostile n=2 panels** (registered): six named panels
  `gf2_n2_a..gf2_n2_f`, each an ordered pair of target pairs drawn from the
  frozen referee's hostile panel construction (identical / swapped / mixed /
  weight-two patterns), all 8 configurations; DP vs brute per configuration.
- **D3 complete n=2 sweep**: all `M^2` ordered instances, unrestricted DP
  optimum over 4 centrals; F1f and F1a family optima by the restricted brute
  enumerator; brute verification of (a) all D2 cells, (b) every cell claimed
  as a gap or family-infeasible witness (both arms re-run independently), and
  (c) a deterministic 1-in-97 systematic sample of D3 cells.

## Hard gates (executed, not logged; abort on violation)

- **G1**: anti-instrument import gate — refuse to run under a trace function
  or with `coverage` loaded; refuse if the frozen R6M module identity asserts
  fail.
- **G2**: D1 complete agreement DP == brute, all cells.
- **G3**: D2 hostile panel agreement DP == brute, all cells.
- **G4**: perm-absorption sample assert (1-in-144 of D3).
- **G5**: every claimed witness (cost gap or family-infeasible) is re-verified
  by the independent brute arm with exact letter reconstruction; any mismatch
  aborts.
- **G6**: result envelope fields present and correct (schema id, base
  revision, protocol sha256, result digest, authority ceiling,
  `novelty_authority: false`, `physical_quantum_advantage_claim: false`).

## Terminals (frozen at registration)

- **T1** `ORION05_GF2_TWO_BLOCK_SUPPORT_ONE_SUFFICIENT_COMPLETE_N2` — no
  instance of D3 has unrestricted optimum strictly below the F1f family
  optimum (and same for F1a); support-one suffices on the complete n=2
  two-block domain. Contrast: the three-block R6O witness (5 < 6) on the same
  n and objective form. Interpretation authority: the support threshold is
  block-count-coupled at n=2; finite-domain only, no all-n claim.
- **T2** `ORION05_GF2_TWO_BLOCK_SHARPNESS_WITNESS_UNRESTRICTED_BELOW_SUPPORT_ONE`
  — at least one D3 instance has unrestricted optimum strictly below the F1f
  family optimum (cost gap or family infeasibility); the witness is reported
  with letters, configuration, and both-arm costs. Interpretation authority:
  the support-one threshold survives block removal on n=2; finite-domain only.
- **T3** `ORION05_GF2_REFUTED_DP_BRUTE_MISMATCH` — any G2/G3/G5 cross-check
  fails; no threshold claim is emitted.

Distinctness rule: "could not check" (import failure, machinery mismatch,
abort) is reported as an abort with the failing gate, never as T1/T2.

## Artifacts

- `development/orion-05-gf2-two-block-grammar-2026-09-03/result/ORION05_GF2_RESULT.json`
  (canonical JSON, schema `ORION05.GF2.TwoBlockTare2SharedTag.v1`);
- `development/orion-05-gf2-two-block-grammar-2026-09-03/RUN_ORION05_GF2.log`;
- registration commit contains protocol + driver only, before any outcome run.

## Authority ceiling

Grammar-family finite-domain exact discriminant for the ORION-05 tier-B
record only. No all-n theorem, no generic TARE or global block-encoding
claim, no production/runtime/hardware/physical-resource claim, no novelty
adjudication, no venue or submission authority, no consumption or alteration
of ORION-01/09/10 claims, no protected Task-3/P9 access, no threshold
retuning of any historical adverse record.
