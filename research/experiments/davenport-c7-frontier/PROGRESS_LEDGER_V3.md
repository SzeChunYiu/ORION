# C7^3 frontier progress ledger — V3

Status: **active exploratory programme; no novelty authority; no `D_3(C_7^3)` closure**. Extends `PROGRESS_LEDGER_V2.md` (which extends V1). Lane: `claude/orion-research-frontier-3ck9yt`, built on the merged ChatGPT-lane packet `shadow/davenport-c7-frontier-20260903` (PR #2198).

## The move this revision makes

V1 and V2 worked one prime at a time: exhaustive frames at `n = 3, 5`, a spectrum proof at `n = 7`, and a single-instance elimination of the binary cube at length 37. The lane's own `QG47 → QG48` record supplies the correction: an exhaustive EMPTY at a fixed slice is attributable to **the slice dimension**, not to structural absence, and the repair is to raise the parameter rather than to re-run the slice. Applied here, the parameter is `n` itself. Every object in the packet — the cube, the extremal families, the packing profile — is defined for all odd `n`, so V3 computes it as a function of `n`.

## New results in V3

| ID | Claim / finding | Status | Boundary / checker |
|---|---|---|---|
| C7-CUBE-5 | Complete packing profile of the binary cube: `c_j(n)` and `z_j(n)` for `j ≤ 4` and every odd `n ≤ 13`, all affine in `n` (`c = 3n−3, (9n−7)/2, (11n−7)/2, 6n−4, 7n−7`; `z = 3n−2, (9n−5)/2, 5n−3, 6n−3`). | EXACT FINITE for `n ≤ 13`; closed forms conjectural beyond | `cube_packing_profile_v3.py` (independent Python), `tools/cube_profile_v3.c`. |
| C7-CUBE-6 | **The cube fails to host a `D_3` obstruction by a margin that grows linearly**: it would need `z_3(n) ≥ (11n−3)/2` and has `z_3(n) = 5n−3`, shortfall `(n+3)/2` (5 at `n = 7`). | EXACT FINITE for `n ≤ 13` | Strictly strengthens `SUPPORT7_BINARY_CUBE_THEOREM_V1.md`, which proved only the single instance `z_3(7) < 37`; the true value is 32. |
| C7-CUBE-7 | The cube is extremal in length for `D_2`, `D_3` (`c_1, c_2` match the conjectured `D_k − 1`) but **not** for `D_4` (`c_3 = 6n−4 < (13n−7)/2` for `n ≥ 5`), so the `k = 4` lower bound needs an eighth support point — and one suffices. | EXACT FINITE | `tools/cube_profile_v3.c` scans over eighth points. |
| C7-FAM-1 | Explicit family `S_4(n) = e_1^{n−1} e_2^{n−1} e_3^{n−1} e_12^{n−1} e_13^{(n+1)/2} e_23^{(n−1)/2} e_123^{n−1} (e_1+e_2+2e_3)^{(n+3)/2}`, length `(13n−7)/2`, packing number 3, giving `D_4(C_n^3) ≥ (13n−5)/2`. | VERIFIED `n = 3, 5, 7, 9`; hand proof OPEN | `cube_packing_profile_v3.py`, `tools/famcheck_v3.py`. At `n = 3` it is exactly extremal (`D_4(C_3^3) = 17`). |
| C7-CONJ-1 | **`D_k(C_n^3) = ((2k+5)n−5)/2 = D(C_n^3) + (k−1)n + (n−1)/2` for all odd `n`, `k ≥ 2`** — the `D_k` sequence is arithmetic with difference `exp(G)` from `k = 2` on, sitting a `k`-independent `(n−1)/2` above the naive value. | CONJECTURE; agrees with every computed value | `DK_ARITHMETIC_CONJECTURE_V3.md`. |
| C7-MECH-1 | The `(n−1)/2` defect is the arithmetic shadow of an index-2 sublattice: the `(e_12,e_13,e_23)` minor of the cube incidence matrix has determinant −2, the rescaled packing problem is a fixed rational polytope independent of `n`, and its half-integral vertices are the `(n±1)/2` multiplicities of the extremal families. | MECHANISM (explains shape; not a proof) | `CUBE_PACKING_PROFILE_V3.md` §5. Falsifiable prediction: the same half-defect for any determinant-2 rank-3 configuration — untested. |
| C7-INV-1 | **Refuted:** `D_k`-extremal sequences are not cube-like. At `n = 3`, only 3.0 % of the 529 `D_2`-extremal sequences contain any `GL(3,3)`-image of the cube (24.7 % at `k = 3`, 60.5 % at `k = 4`). | EXACT FINITE (complete enumeration, `n = 3`) | `tools/cubelike_v3.py`. Closes the "classify extremal = classify cube" route. |
| C7-INV-2 | Conjecture R: every `D_k`-extremal sequence contains an element of multiplicity `n−1`. Holds for all 529 + 7 317 + 8 921 sequences at `n = 3` (`k = 2,3,4`), all 7 847 at `n = 5, k = 2`, all 4 014 found so far at `n = 5, k = 3`; and capping the cube at `n−2` strictly lowers `c_1, c_2` at every computed `n`. | CONJECTURE with complete-enumeration support | `EXTREMAL_STRUCTURE_V3.md`. This is the cheapest lever on the `u = 8` residual of the reduction lemmas. |
| C7-EXH-6 | `D_3(C_5^3) = 25` re-verified by an independent reverse-point-order run: identical 7 716 438 leaves and 0 obstructions, different node count (1 038 218 799 vs 848 752 855). | EXACT FINITE, doubly certified | `run_exhaustive_analogs_v2.sh`. |

## Where the frozen question now stands

`D_3(C_7^3) = 36` is unresolved. What has changed is the shape of the remaining problem:

1. The obstruction, if it exists, is a zero-sum sequence `T` of length 37 with `pk(T) = 3`, multiplicities `≤ 6`, no zero-sum subsequence of length `≤ 7`, shortest block of length `8, 9` or `10`, and every one-element deletion `D_3`-extremal (`OBSTRUCTION_REDUCTION_LEMMAS_V2.md`).
2. It is **not** supported on the binary cube, and not narrowly: that geometry is short by `(n+3)/2 = 5` elements (C7-CUBE-6).
3. It is **not** to be found by classifying cube-like extremal sequences (C7-INV-1).
4. Both the `p = 3` and `p = 5` analogues are closed and both obey the conjectured formula; `p = 5` is closed twice over.
5. The remaining lever with the best cost/benefit is Conjecture R, which would pin a multiplicity-6 element in the `u = 8` case.

## Open residuals (V3)

1. `D_3(C_7^3)` itself; the complete search frame `7 36 6 7 2 --planecap 26` is specified but out of reach of plain DFS.
2. Upper bounds in the cube profile table for `j ≥ 2` (the lower-bound families are proved for all odd `n`; the matching upper bounds are verified only for `n ≤ 13`). The proof route is a finite profile-tuple case analysis with integral rounding — specified in `CUBE_PACKING_PROFILE_V3.md` §5, not executed.
3. A hand proof of `S_4`, and the general `S_k`.
4. Conjecture R.
5. Priority / donor saturation: unchanged and now also blocked by host egress policy (C7-DONOR-1).
6. `η`-type input: the short-zero-sum induction `D_{k+1} ≤ D_k + n` cannot use `η(C_n^3) ≥ 8n−7`; the zero-sum spectrum bound (length `≤ 10` at `n = 7`) is one step short of the needed `n+1 = 8`.

## Claim ceiling

Nothing in V3 proves `D_3(C_7^3) = 36` or `≥ 37`. Nothing establishes novelty or priority: the `k = 2` value, the eventual-arithmetic theorem and the step inequality are donor-owned, and the host could not read the donor texts. Rows marked RUNNING/PARTIAL are execution status, not results.
