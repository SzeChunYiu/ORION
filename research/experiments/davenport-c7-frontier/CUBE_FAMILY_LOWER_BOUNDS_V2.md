# Explicit binary-cube families realising the `D_2` and `D_3` lower bounds for `C_n^3`, `n` odd — V2

Status: **proved (hand proof below) and machine-verified for `p = 3, 5, 7, 11`**; novelty: **not claimed** — the values coincide with the Freeze–Schmid lower bounds cited in `PROGRESS_LEDGER_V1.md`, so these are almost certainly a re-derivation of their construction (priority CANNOT_CHECK: the donor text was not readable from this host). Value to the packet: an explicit, independently checkable witness for `D_3(C_7^3) ≥ 36`, and a uniform description of the extremal objects that the D3 search must extend or refute.
Checker: `verify_cube_family_v2.py` (pure Python; verifies the exact packing numbers by exhaustive recursion over atoms).

## Notation

`G = C_n^3` with basis `e_1, e_2, e_3`; `e_12 = e_1+e_2`, `e_13 = e_1+e_3`, `e_23 = e_2+e_3`, `e_123 = e_1+e_2+e_3`; `Q = {e_1,e_2,e_3,e_12,e_13,e_23,e_123}` is the nonzero binary cube. For a sub-multiset `b` of a sequence supported on `Q` write `c_i(b)` for its `i`-th coordinate sum as an integer (not reduced mod `n`). The zero-sum packing number `pk(S)` is the maximum number of pairwise disjoint nonempty zero-sum subsequences.

## Theorem 1 (`D_2`). Let `n ≥ 3` be odd and

    S_2(n) = e_1^{n−1} e_2^{n−1} e_3^{n−1} e_12^{(n+1)/2} e_13^{(n−1)/2} e_23^{(n−1)/2},   |S_2(n)| = (9n−7)/2.

Then `pk(S_2(n)) = 1`; hence `D_2(C_n^3) ≥ (9n−5)/2`.

*Proof.* Coordinate totals of `S_2(n)` are `(2n−1, 2n−1, 2n−2)`, all `< 2n`, so every zero-sum sub-multiset `b` has `c_i(b) ∈ {0, n}`. A nonempty zero-sum `b` with a single nonzero coordinate sum is impossible: if `c_2(b) = c_3(b) = 0` then `b_2 = b_3 = b_12 = b_13 = b_23 = 0` and `c_1(b) = b_1 ≤ n−1 < n`; the other two coordinates are symmetric. So every nonempty zero-sum block has at least two coordinates with `c_i = n`. Two disjoint blocks would need at least four (block, coordinate) incidences, but each coordinate total is `< 2n`, so each coordinate can carry at most one block: at most three incidences. Hence `pk ≤ 1`; and `e_1^{(n−1)/2} e_2^{(n−1)/2} e_12^{(n+1)/2}` is a zero-sum block, so `pk = 1`. ∎

## Theorem 2 (`D_3`). Let `n ≥ 3` be odd and

    S_3(n) = e_1^{n−1} e_2^{n−1} e_3^{n−1} e_12^{n−1} e_13^{(n+1)/2} e_23^{(n−1)/2} e_123^{(n+1)/2},   |S_3(n)| = (11n−7)/2.

Then `pk(S_3(n)) = 2`; hence `D_3(C_n^3) ≥ (11n−5)/2`, in particular `D_3(C_7^3) ≥ 36`.

*Proof.* Coordinate totals are `(3n−1, 3n−2, (5n−1)/2)`, all `< 3n`, so `c_i(b) ∈ {0, n, 2n}` for every zero-sum sub-multiset `b`. As before a nonempty zero-sum block cannot have a single nonzero coordinate sum: `c_2 = c_3 = 0` forces `b_2=b_12=b_23=b_123=b_3=b_13=0` and `c_1 = b_1 ≤ n−1`; `c_1 = c_3 = 0` forces `b_1=b_12=b_13=b_123=b_3=b_23=0` and `c_2 = b_2 ≤ n−1`; `c_1 = c_2 = 0` forces `c_3 = b_3 ≤ n−1`. So each block has `≥ 2` nonzero coordinates. Suppose `A, B, C` are pairwise disjoint nonempty zero-sum blocks. For each coordinate `i`, `Σ_{X∈{A,B,C}} c_i(X) ≤ total_i < 3n`, so at most two blocks have `c_i > 0`, and if two do then both have `c_i = n`. Counting incidences: `≥ 6` and `≤ 6`, so every block has exactly two nonzero coordinates (each equal to `n`), and the blocks miss pairwise distinct coordinates. Say `c_3(A) = 0`, `c_2(B) = 0`, `c_1(C) = 0`. Then

    A: b_3=b_13=b_23=b_123=0,  b_1 + b_12 = n,  b_2 + b_12 = n;
    B: b_2=b_12=b_23=b_123=0,  b_1 + b_13 = n,  b_3 + b_13 = n;
    C: b_1=b_12=b_13=b_123=0,  b_2 + b_23 = n,  b_3 + b_23 = n.

The multiplicity of `e_1` gives `(n − b_12^A) + (n − b_13^B) ≤ n−1`, i.e. `b_12^A + b_13^B ≥ n+1`; likewise `e_2` gives `b_12^A + b_23^C ≥ n+1` and `e_3` gives `b_13^B + b_23^C ≥ n+1`. But `b_13^B ≤ (n+1)/2` and `b_23^C ≤ (n−1)/2`, so `b_13^B + b_23^C ≤ n`, a contradiction. Hence `pk ≤ 2`. The blocks `e_1^{(n−1)/2} e_2^{(n−1)/2} e_12^{(n+1)/2}` and `e_1^{(n−1)/2} e_3^{(n−1)/2} e_13^{(n+1)/2}` are disjoint zero-sums (they use `n−1` copies of `e_1` in total), so `pk = 2`. ∎

Both proofs use only that `n` is odd (so that `(n±1)/2` are integers) and never that `n` is prime.

## Machine verification

`verify_cube_family_v2.py` recomputes `pk(S_2(p))` and `pk(S_3(p))` for `p ∈ {3,5,7,11}` by exhaustive recursion over minimal zero-sum sub-multisets and asserts the values 1 and 2. For `p = 7` the witnesses are

    S_2(7) = e_1^6 e_2^6 e_3^6 e_12^4 e_13^3 e_23^3            (length 28, pk = 1),
    S_3(7) = e_1^6 e_2^6 e_3^6 e_12^6 e_13^4 e_23^3 e_123^4     (length 35, pk = 2).

Independently, the box dynamic programme `tools/boxmax.c` (a differently structured program, mixed-radix DP over all `(p)^7` multiplicity vectors on `Q`) reports for every tested `p`

    max{ |S| : supp S ⊆ Q, pk(S) ≤ 1 } = (9p−7)/2,   max{ |S| : supp S ⊆ Q, pk(S) ≤ 2 } = (11p−7)/2,
    max{ |S| : supp S ⊆ Q, pk(S) ≤ 3 } = 6(p−1)+2       (p = 3, 5, 7, 11),

with the witnesses above returned as maximisers. So within the binary cube the `D_3` lower bound `(11p−5)/2` is **sharp** for `p ≤ 11`: no cube-supported sequence of length `(11p−5)/2` has packing number `≤ 2`. This is the exact-support counterpart, at length 36, of the length-37 elimination in `SUPPORT7_BINARY_CUBE_THEOREM_V1.md`, and it also shows that the cube does **not** reach the conjectural `D_4` value `(13p−5)/2` (an eighth support point is necessary for `k = 4`).

## Claim ceiling

Nothing here bounds `D_3(C_n^3)` from above. No priority is claimed for the families `S_2`, `S_3` or the inequalities; they are recorded because they make the donor bound explicit and checkable inside the repository and because the maximisers exhibit a uniform multiplicity pattern `(n−1, …, (n+1)/2, (n−1)/2, …)` that the extremal-structure analysis relies on.
