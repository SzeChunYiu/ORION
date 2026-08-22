# ORION-RG X1-F — exact 3-wise Davenport constant of `C_5^3`

Issue: `SzeChunYiu/ORION#915`. Parents `#916` (exact `D_2`), `#912`, `#901`,
umbrella `#896`.

## Authority

`mathematical_proposal: true`, `mathematical_result_credit: false`,
`proof_authority: false` beyond what is machine-checked here, `novelty_claim:
false`. Root state of `#896` unchanged: `OPEN`. No credit taken over
Davenport-constant theory, Freeze–Schmid, Olson's constant, or exhaustive search.

## Result

```
D_3(C_5^3) = 25
```

`#915` carried `25 <= D_3 <= 33`. The `eta_T` ladder (`#916`) narrowed that to
`[25, 26]`. This atom closes it at 25.

## Lower bound — established here, not cited

`#915` attributes `D_3 >= 25` to Freeze–Schmid but the witness is not reproduced
in the issue text, so it is rebuilt rather than assumed. Extending the
Freeze–Schmid 19-term `k=2` witness by five elements gives

```
e1^4 e2^4 e3^9 (1,1,0)^2 (1,0,1)^2 (0,1,1)^3            (length 24)
```

i.e. the `k=2` witness with `e3` raised from multiplicity 4 to 9. Verified twice
(independent Python `k`-disjoint DP, and the C control harness):
minimum zero-sum length 5, **two** disjoint zero-sums exist, **three** do not.
Hence `D_3 >= 25`.

## Upper bound — a structure theorem, then a complete search

Let `|M| = 25` with no three pairwise disjoint nonempty zero-sums.

1. Lemma A with `k = 2` and `D_2 = 20`: every zero-sum of `M` has length `>= 6`.
2. `f_6(C_5^3) = 23 < 25`, so `M` has a zero-sum of length `<= 6`.
3. Therefore `M` has a zero-sum `A` with `|A| = 6` **exactly**.
4. `C = M A^{-1}` has 19 elements and no two disjoint zero-sums — otherwise
   those two together with `A` would be three.
5. `C` has rank 3: a rank-`<=2` sequence of length 19 already has two disjoint
   zero-sums, since `D(C_5^2) = 9` and `19 - 9 = 10 >= 9`.
6. So `C` is `GL(3,5)`-equivalent to one of the **98,622** normalized length-19
   witnesses enumerated in `#916`, and that enumeration is complete.

The search then has only two moves.

**Pass 1** (`x1f_d3_pass1_extension_filter.c`). For each of the 98,622
witnesses, enumerate every six-element extension subject to three constraints,
each of which is forced by the structure theorem rather than chosen:

- the six added elements sum to zero (`A` is a zero-sum);
- they are enumerated in nondecreasing order (`A` is a multiset, so each
  multiset is generated exactly once);
- the extended sequence keeps minimum zero-sum `>= 6` (step 1).

Output: **230,983** length-25 candidates. Zero witnesses were skipped for
already carrying a short zero-sum, confirming step 1 on the whole family.

**Pass 2** (`x1f_d3_pass2_exact_three_disjoint.c`). Exact three-disjoint test on
every candidate, carrying `R1`/`R2`/`R3` boards (one, two, three nonempty parts
indexed by their partial sums) advanced by the coordinate shift realising `+v`.
Candidates are grouped by their 19-element prefix so the expensive `R3` state
for `C` is built once per group: 45,970 groups, 0 rebuild failures.

Result: **0** of the 230,983 candidates have no three disjoint zero-sums.
No length-25 sequence exists, so `D_3 <= 25`. ∎

## Validating the rejector before believing it

A rejector that always answers "three disjoint exist" would also report zero
survivors. The control harness `x1f_kdisjoint_control_harness.c` runs the *same*
`R3` machinery on sequences whose answer is known independently:

| input | two disjoint | three disjoint | expected |
|-------|--------------|----------------|----------|
| Freeze–Schmid 19-term `k=2` witness | no | no | both no |
| the length-24 lower-bound witness | **yes** | **no** | yes / no |
| that witness plus one element (length 25) | yes | yes | yes |
| `e1^5 e2^5 e3^5 (1,1,1)^10` | yes | yes | yes |

The second row is the one that matters: a checker that could not say "no" at
length 24 would be worthless at length 25. All four controls pass, and the
length-24 verdict agrees with the independent Python DP.

## Consequences

- The `k`-wise sequence for `C_5^3` now reads `D_1 = 13`, `D_2 = 20`,
  `D_3 = 25` — increments `7, 5`. The second increment equals `exp(C_5^3) = 5`,
  the first does not, so `D_k = D + (k-1)exp` fails at `k = 2` and then holds at
  `k = 3`. Whether `D_k(C_5^3) = 5k + 10` for all `k >= 2` is open and is the
  obvious next atom.
- **Lemma B is not tight here.** It gives
  `max(eta_6, D_2 + 6) = max(24, 26) = 26`; the true value is 25. So `C_5^3` at
  `k = 2` joins `C_2^4` at `k = 1` as a case where the single-threshold ladder
  loses by exactly one. That is now 9 tight out of 11 decided steps. Both gaps
  point the same way — the ladder commits to one threshold `T` — so a
  multi-threshold refinement is the named next mechanic, and it now has two
  failing instances to be tested against rather than one.
- For `#912` (C45 split), exact `D_3 = 25` is stronger than the `D_3 <= 28` that
  issue needed to upgrade its 133-term quotient packing from 23 to 24 blocks.

## Reproduction

```
cc -O3 -o pass1 research/orion-rg/x1f_d3_pass1_extension_filter.c
cc -O3 -o pass2 research/orion-rg/x1f_d3_pass2_exact_three_disjoint.c
./pass1 d2_witnesses.txt d3_candidates.txt      # witnesses from #916's enumerator
./pass2 d3_candidates.txt
python3 research/orion-rg/x1f_d3_lower_bound_witness.py
```
