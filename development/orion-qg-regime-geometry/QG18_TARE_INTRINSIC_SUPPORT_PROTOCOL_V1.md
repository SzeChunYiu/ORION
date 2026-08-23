# QG-18 — TARE intrinsic support number: receipt-derived necessity protocol V1

Date: 2026-08-22
Issue: #835
Parent programme: #740
Branch: `codex/orion-qg-qg18-kappa2-20260822`
Status: **FROZEN BEFORE QG-18 DUAL-HARNESS EXECUTION.**

Authority ceiling: exact intrinsic-support corollary for the frozen unit-objective R6M/TARE grammar only; no novelty/R6/physical-advantage authority.

## 1. Research question

R6S already proves that every frozen R6M/TARE optimum admits all six frame Paulis with global support <=2 for every n. Therefore `kappa_TARE <= 2`.

QG-18 asks whether support 2 is necessary. A single feasible support-2 compilation of cost U2 together with an exact support<=1 family optimum C_cap1 satisfying

`U2 < C_cap1`

proves that no support<=1 compilation is globally optimal on that instance. Combined with R6S, this yields the exact intrinsic support number

`kappa_TARE = 2`.

No unrestricted DP equality is required for the lower-bound implication because global optimum `C_DP <= U2 < C_cap1`.

## 2. Evidence status and prospective boundary

This is a **receipt-derived corollary lane**, not a blind new-witness search.

QG-7 is an already-earned result and serialized fourth-regime witnesses whose analyzer also reported `C_Dplus = dxx_search(..., max_weight=1)`. R6P documents `dxx_search` as the exact D++ optimum or its exact weight-restricted sub-family. Thus the existing QG-7 receipt may already contain the cap-1 strict gap needed by QG-18.

QG-18 receives zero discovery/novelty credit for re-reading that old value. The new obligation is only to bind the equivalence

`C_Dplus == C_cap1`

and independently reconstruct the selected witness's support-2 feasibility/cost and cap-1 optimum from primitive Pauli/TARE semantics through the dual harness.

No post-outcome candidate widening is allowed.

## 3. Frozen parent bindings

Mandatory parent files:

- `research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json`
  - required schema `ORIONQG.QG7.BprimeCompleteness.v1`;
  - required terminal `QG7_FOURTH_SUPPORT2_REGIME_FOUND`;
  - required result digest `159d174fbb17a66aeb39a3efb53cf4c505f0a86ce8ef1dff76337d00837d152f`.
- `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`
  - required authority contains `DXX_EQUALS_DP_ALL_N`;
  - all theorem gates true;
  - no R6/novelty authority.

## 4. Frozen witness selection

Select exactly:

`QG7_BPRIME_COMPLETENESS_RESULTS.arm1_hostile_search.fourth_regime_candidates_verbatim[0]`.

No scan over later witnesses is permitted if this row fails QG-18. Failure produces a binding/disagreement terminal rather than candidate substitution.

Expected historical metadata are controls, not authority sources:
- panel `H1_n3`;
- n = 3 parsed from the panel;
- QG-7 recorded `C_DP=7`, `C_Dxx=7`, `C_Dplus=8`, `f_Bprime=8`.

## 5. Production-side cap-1 binding

Recompute on the selected target triples:

`C_cap1_prod = r6p.dxx_search(target_pairs, n, max_weight=1, want_witness=True)['C_Dxx']`.

The R6P enumerator's exact family is the frozen D++ grammar with every frame Pauli restricted to `wt<=max_weight`, shared Tag support unrestricted and minimized exactly, both target orders admitted per block, central choice/cost semantics exact, and the all-three F3 Restore factor rule exact. Therefore with `max_weight=1` this is precisely the exact support<=1 TARE family for the QG-18 support definition.

Required production binding:

`C_cap1_prod == selected_QG7.C_Dplus`.

## 6. Production-side feasible support-2 witness

Use the selected row's serialized `dxx_witness_verbatim` without modification.

Require:
- `r6p.verify_dxx_witness(...) == True`;
- every serialized frame Pauli support is <=2;
- at least one frame Pauli support is exactly 2;
- recomputed witness cost `U2` equals the serialized `C_Dxx`;
- `U2 < C_cap1_prod`.

The strict inequality alone proves `C_DP < C_cap1` because the support-2 witness is feasible, regardless of whether its cost is opened as the unrestricted optimum.

## 7. Independent generic ORION referee

Generic ORION must **not import R6P/R6O/QG-7 analyzer code for the mathematical recomputation**. It may read only the serialized selected witness/targets and parent authority metadata after the primitive calculation is defined.

Rebuild from primitive binary symplectic Pauli semantics:

1. Pauli key `(x,z)` multiplication by bitwise XOR;
2. support `popcount(x|z)`;
3. symplectic product mod 2;
4. local residual letters from target-frame multiplication;
5. all-three F3 rule: local triple cost is 1 when all three residual letters are the same nonidentity Pauli, otherwise the number of nonidentity residual letters;
6. Tag cost `2*wt(S)`;
7. frame extra cost with multiplier 2 on the selected central frame and 4 on the noncentral frame.

### Independent support-2 check

Recompute acceptance, shared ordered labels, frame support, target permutations, frame-extra cost, F3 Restore cost, Tag cost and total U2 from the serialized witness. Required U2 = 7.

### Independent exact cap-1 brute

At n=3 enumerate all nonzero weight<=1 Pauli keys and every ordered anticommuting frame pair. For each nonzero shared Tag S and each allowed ordered label orientation `(0,1)` or `(1,0)`:

- enumerate all matching frame pairs for each of the three blocks;
- enumerate both target orders per block;
- compute exact total unit objective using primitive frame-extra/Tag/F3 rules;
- take the global minimum.

Required cap-1 optimum must independently equal the production value. Serialize one exact minimizing witness.

No production DP or R6P D++ table may supply this lower bound.

## 8. Intrinsic-support theorem step

If:

- R6S parent proves universal support<=2;
- generic and production agree on exact `C_cap1`;
- independently verified feasible support-2 witness has `U2<C_cap1`;

then:

1. this instance has no support<=1 optimum, so the universal intrinsic support number is >1;
2. R6S gives universal intrinsic support number <=2;
3. hence `kappa_TARE=2` exactly for the frozen unit-objective grammar.

This is a logical corollary from an old QG-7 witness plus a newly explicit independent cap-1 binding, not a new physical/compiler method.

## 9. Native ORION-Q responsibilities

Native lane states:
- `KAPPA2_COROLLARY`
- `CAP1_BINDING_GAP`
- `SUPPORT2_WITNESS_GAP`
- `R6S_PARENT_GAP`
- `GENERIC_DISAGREEMENT`
- `CANNOT_CHECK`.

A positive requires generic and production values/witness checks to agree exactly.

## 10. Honest terminals

Positive:

`QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS`

Negative/fail-closed:
- `QG18_CAP1_BINDING_GAP`
- `QG18_SUPPORT2_WITNESS_REPLAY_FAILED`
- `QG18_GENERIC_NATIVE_DISAGREEMENT`
- `QG18_R6S_PARENT_BINDING_GAP`
- `QG18_CANNOT_CHECK`.

If the selected first QG-7 witness does not survive the exact independent cap-1 check, do not select another QG-7 witness in V1.

## 11. Claim boundary

Unit raw support-count objective only. No transfer to QG-2/QG-8 reweighted objectives. No novelty credit for finite enumeration, Pauli algebra, support-capped optimization, or the already-known QG-7 witness. No physical quantum advantage. The protected stretched-N2 subject remains sealed.
