# ORION-Q N2-F4 — Representation/access edits under NO_STRONGER_ORACLE (frozen protocol)

Date frozen: 2026-08-21 (before any outcome artifact exists)
Parent programme: #633; lane issue: #675 (successor family 4); immutable prior negative: #671
Branch: `claude/orion-harness-verification-b17qdj`
Status: **PROTOCOL FREEZE BEFORE OUTCOMES.** Runner: `research/extensions/orion-q/nlanes/n2_f4_access_edits.py`. Gates prespecified; reported honestly whatever they yield.

## Registered design being executed (from #675, authoritative text)

> **Representation/access edits:** same mathematical target but different admissible interface constructions; enforce `NO_STRONGER_ORACLE`.

## Exact-synthetic world (frozen)

`SEED = 20260821`. 60 instances. Each instance: an exact Pauli-sum Hamiltonian on `n = 4` qubits, `A = sum_i a_i P_i`, with `L_raw in {12, 20, 32}` strings drawn **with replacement** from a fixed seeded pool of 40 Pauli strings (duplicates deliberate), coefficients `a_i ~ U(-1,1)` rounded to 6 decimals. The 16x16 matrix is built exactly (numpy, kron of exact Pauli matrices).

Mathematical target: QSVT at frozen degree `d = 32` applied to `A/alpha`. Frozen cost model:
- Query cost `Q = d * alpha` (alpha = subnormalization of the access representation).
- Classical preprocessing counters (frozen accounting units): `merge = L_current`; `regroup(m) = L*ceil(log2(L)) + L`; `sparse_convert = L^2 + 16*L`; `retrain_from_scratch_preproc = 4^n * n = 1024`.
- Scalar decision cost `= Q + mu * P_total`, `mu = 1e-3`. Vector `(Q, ancillas, P_total)` is also reported.

### Admissible representations and alpha derivations (the only lawful derivation tags)

- `l1` (plain LCU): `alpha = sum |a_i|`; ancillas `ceil(log2(L))`.
- `grouped_l2(m)` for `m in {2,4}`, `m | L`, sorted-contiguous grouping (R4B theorem-optimal): `alpha = sqrt(m) * sum_g ||a_g||_2`. (Mathematically `>= l1`; kept as an admissible-but-typically-dominated edit — the mechanism must explore and discard it, never be helped by it.)
- `sparse`: row sparsity `s` and `||A||_max` computed exactly **from the stored representation**; `alpha = s * ||A||_max`; ancillas `ceil(log2(s)) + 1`.
- `merge`: exact duplicate-string merge (sums coefficients of identical strings, drops exact zeros). Same matrix; can strictly lower `l1` alpha and lowers `L` for later edits.

### NO_STRONGER_ORACLE gate (frozen checker)

Every edit carries a derivation tag; the checker **recomputes** the claimed alpha from the representation with the tagged admissible formula and rejects on mismatch `> 1e-9` (`NO_STRONGER_ORACLE`), and rejects any edit whose output matrix differs from the input matrix by `> 1e-10` max-abs (`TARGET_CHANGED`).

### Laundering attempts (hostile; must be caught on every instance)

- `LA1_spectral_smuggle`: presents tag `sparse` but claims `alpha = ||A||_2` (true spectral norm, computed via eigvalsh — information not derivable at admissible cost from the interface). Must be rejected `NO_STRONGER_ORACLE`.
- `LA2_drop_small_terms`: deletes every term with `|a_i| < 0.05` and, if none qualify, the single smallest-magnitude term (so the attempt is never a no-op), then presents an honest `l1` alpha for the truncated operator. Must be rejected `TARGET_CHANGED`.

> **Amendment A1 (2026-08-21, after first run, before any gate re-interpretation):** the original LA2 wording ("deletes `|a_i| < 0.05` terms") was a defective control: on instances with no coefficient below 0.05 it deleted nothing, so the checker correctly accepted an identity edit and F4-G2 mismeasured "laundering caught" (first-run LA2 rejection rate 0.5 for exactly this reason; first-run receipt retained in the results file lineage). A1 repairs only the control construction (never-no-op rule above). The mechanism, world, baselines, scoring and all gate thresholds are unchanged; the residual gate is reported honestly as it falls.

## Candidate ORION mechanism

Exhaustive typed search over admissible edit chains up to length 3 (from `{merge, regroup(2), regroup(4), sparse}`, no repeated edit kind), every step passed through the NO_STRONGER_ORACLE + SAME_TARGET checker; select the chain minimizing frozen scalar cost; emit the chain with per-edit admissibility receipts.

## Strongest non-ORION baselines (first right of refusal)

- `B0_no_edit`: given `l1` representation as-is.
- `B1_best_single_edit`: min scalar cost over all admissible single edits.
- `B2_retrain_from_scratch`: builds merged+sparse representation directly from raw matrix data, ignoring the given interface, paying `retrain_from_scratch_preproc = 1024`.
- `FORBIDDEN_SPECTRAL_BOUND` (bound only, never an arm): `Q = d * ||A||_2` — the cost a genuinely stronger oracle would grant.

## Prespecified gates

| Gate | Statement | Threshold |
|---|---|---|
| F4-G1 | Determinism: pipeline twice in-process, canonical JSON identical | exact equality |
| F4-G2 | Laundering catch: LA1 and LA2 rejected on **all 60** instances | rejection rate = 1.0 |
| F4-G3 | Consistency: best admissible alpha `>= ||A||_2 - 1e-9` on every instance (no admissible chain beats the stronger-oracle bound) | 1e-9 |
| F4-G4 | Same-target: every accepted chain's final representation rebuilds the exact matrix, max-abs deviation | `<= 1e-10` |
| F4-G5 | Residual: fraction of instances where ORION chain scalar cost `< min(B0, B1, B2) - 1e-9` | `>= 0.60` |

Terminal vocabulary: `N2_F4_ACCESS_EDITS_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY`; `N2_F4_ACCESS_EDITS_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY` (honest negative, valid); `N2_F4_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED` (any of G1–G4 fails).

## Determinism and receipt rules

Stdlib + numpy only; fixed seed; one stdout receipt line `ORIONQ_N2_F4_ACCESS_EDITS=<canonical sorted json>`; pretty results to `research/extensions/orion-q/nlanes/N2_F4_ACCESS_EDITS_RESULTS.json`; exit 0 regardless of gates.

## Claim boundary

Exact-synthetic scope only. The cost model (`Q = d*alpha`, frozen preprocessing counters, `mu`) is an accounting proxy, not a compiled circuit estimate; any residual is **accounting-level and contingent on the frozen counters**. No novelty claim for LCU, sparse access, term merging, grouping (donor-owned: TARE, block-encoding compilers, end-to-end access-cost accounting per #675). The contribution under test is only the typed edit-chain search with an enforced NO_STRONGER_ORACLE / SAME_TARGET gate.
