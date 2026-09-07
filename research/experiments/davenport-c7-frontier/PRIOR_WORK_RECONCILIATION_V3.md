# Reconciliation with prior ORION work — V3

Status: **correction record**. Written after auditing two bodies of in-repo work that this packet's V2/V3 records did not account for: the ORION-RG Davenport programme (`development/orion-rg-davenport/`, `research/domains/orion-rg/`, issues #894/#896/#915/#916) and the concurrent ChatGPT-lane advance on `shadow/davenport-c7-frontier-20260903` (merged into this branch at the commit carrying this file). Several V2/V3 claims of independence are withdrawn here.

The lesson is the packet's own: a negative literature search from a host that cannot reach arXiv says nothing about prior art, and it says nothing at all about prior art **inside the repository**. The in-repo search should have come first.

## 1. Results this packet re-derived that ORION already had

| This packet | Prior ORION | Status now |
|---|---|---|
| `D_3(C_5^3) = 25` (exhaustive, `EXHAUSTIVE_ANALOG_RESULTS_V2.md` Thm 4.1) | **ORION-RG X1-F** (`X1F_D3_C5CUBED_PROTOCOL_V1.md`, issue #915): same value, via a structure theorem (`f_6(C_5^3) = 23` forces a length-6 zero-sum) plus a two-pass search over the 98,622 normalized length-19 witnesses. | **Priority is X1-F's.** This packet's run is an *independent replication by a different method* (direct symmetry-reduced DFS with no structure theorem), and was itself run twice. Retained as confirmation, not as a new value. |
| `D_2(C_5^3) = 20` | **ORION-RG X1-F0** (issue #916). | Same: replication. |
| Theorem 2 of `GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` (`D_k + exp ≥ η ⟹ D_{k+1} ≤ D_k + exp`) | **X1-F0 records this as "Lemma B — NOT NEW. This is Freeze–Schmid 2010, Proposition 3.1(3)"**, in the sharper form `D_{k+1} ≤ min_T max(η_T, D_k + T)`. **X1-H** (`X1H_LADDER_REFINEMENT_PROOFS.md`, Thm N1) proves that form is *optimal* among all bounds using only the statistics `{η_T}`, and that multi-threshold peeling collapses to it (Thm N2). | **Withdrawn as a contribution.** My Theorem 2 is the `T = exp(G)` case of a published result, and X1-H already shows the whole family cannot be improved without a finer statistic. The `C_3^3` corollary (Theorem 4) is therefore also a consequence of published machinery. |
| The conjecture `D_k(C_n^3) = ((2k+5)n−5)/2` (`DK_ARITHMETIC_CONJECTURE_V3.md`) | The ChatGPT lane's `PROGRESS_LEDGER_V1.md` (V11) states exactly this as **"the current general target"** for `p ≥ 5`, `k ≥ 2`; ORION-RG states the `n = 5` case as `D_k(C_5^3) = 5k + 10`. | **Not this packet's conjecture.** Restated as a shared target that this packet supplies evidence for. |
| `SUPPORT7_BINARY_CUBE_THEOREM_V1` and its V3 strengthening at `p = 7` | **`SUPPORT7_ALL_THEOREM_V1.md`** (ChatGPT lane) closes **every** support-7 geometry at `p = 7`: 3,418,800 lifts, 14,860 short-free, all four-pack. | The `p = 7` binary-cube statement is a special case of theirs. What is not subsumed is the *uniform-in-`n`* profile (§2). |
| `T_k(n)` for `k = 3`, `n = 5` | X1-F's rebuilt lower-bound witness `e1^4 e2^4 e3^9 (1,1,0)^2 (1,0,1)^2 (0,1,1)^3` is `T_3(5)` up to relabelling — the same "raise one basis multiplicity by `n`" device. | The general-`k`, general-odd-`n` family and its hand proof remain this packet's own; the device and the `k = 2` base (Freeze–Schmid Thm 4.1) do not. |

## 2. What survives as this packet's own contribution

1. **`D2_UNIFORM_SELFCONTAINED_THEOREM_V3.md`** — a self-contained proof that `D_2(C_p^3) = (9p−5)/2` for every prime `p ≥ 5`, from the polynomial-method identity, Olson, Lucas and `T_2(p)`. This is *complementary rather than duplicative*: the value is donor-owned, but every reduction in the merged packet (`FINITE_FIRST_FAILURE_REDUCTION_V1`, `GENERAL_CP3_MULTIWISE_MASTER_REDUCTION_V1`, `PACKING_DEFECT_CORE_FORMALISM_V1`, `CRITICAL_SHORTFREE_SUPPORT_MINIMUM_V1`) currently *assumes* it on the strength of Zhao Lemma 4.4, which this host cannot fetch. The premise is now discharged.
2. **`CUBE_PACKING_PROFILE_V3.md`** — the exact capacities `c_j(n)`, `z_j(n)` of the binary cube for all odd `n ≤ 13`, uniform in `n`. The `p = 7` slice is subsumed by `SUPPORT7_ALL_THEOREM_V1`; the `n`-dependence, the closed forms, and the growing shortfall `(n+3)/2` are not.
3. **`GENERAL_LOWER_BOUND_AND_ETA_INDUCTION_V3.md` Theorem 1** — the family `T_k(n)` for every odd `n` and every `k ≥ 2`, with a hand proof. It gives the target's lower bound without the donor step inequality.
4. **`CORRECTION_MULTIPLICITY_CAP_V3.md`** — the enumeration-cap audit, which applies to this packet's own frames.
5. The retained negatives: pointed congruences add nothing; extremal sequences are not cube-like; rigidity fails for `k ≥ 3`.

## 3. An open question in the ORION-RG lane that this packet touches

`X1K_D4_C5CUBED_PROTOCOL_V1.md` leaves `D_4(C_5^3) ∈ {30, 31}` **open**, and explicitly develops the conditional branch `D_4(C_5^3) = 31`. That value decides the shared conjecture at `n = 5`: `31` would falsify `D_k(C_n^3) = ((2k+5)n−5)/2` at `k = 4`.

Evidence added here, weak but pointed in the direction of 30: neither length-29 witness with packing number 3 known to this packet — the 8-point cube family `S_4(5)` and `T_4(5)` — admits **any** single-element extension keeping packing number `≤ 3` (all 124 nonzero elements tested against each, `tools/d4_extension_test_v3.py`). This does not decide the question; a length-30 obstruction need not extend a length-29 one from these two families.

The structural route to deciding it is already available in the merged packet: by Lemma A with `k = 3` and `D_3 = 25`, a length-30 obstruction has minimum zero-sum `≥ 6`; by `f_6(C_5^3) = 23 < 30` it has one of length `≤ 6`, hence exactly 6; deleting it leaves a length-24 sequence with packing number `≤ 2` and minimum zero-sum `≥ 6` — and that constraint independently forces all multiplicities `≤ 4`, so the enumeration cap is legitimate here (`CORRECTION_MULTIPLICITY_CAP_V3.md` §1). The frame is `5 24 4 5 2`; this session's run of it was terminated incomplete by a container restart at 6,130 witnesses.

## 4. Process correction

`PAPER_OUTLINE_V1.md` listed "donor subtraction" as pre-submission work against the external literature only. It must also list **in-repo subtraction**, and that is now its first item. Any future frontier packet in this repository should begin by reading `development/orion-rg-davenport/` and the other lanes' branches for the same problem, before any search is run.
