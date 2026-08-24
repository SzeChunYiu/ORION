# Non-quantum math M1 — the one-unit `D_k(C_5^3)` tail corridor

Date: 2026-08-24

Base: `0dc9e07badae039743a6966dd9198586a497d72f`

Status: **FROZEN BEFORE THE M1 ANALYZER AND DUAL-HARNESS RUN; ALL PARENT CONSTANTS AND DONOR RECURRENCES ALREADY KNOWN**

Primary owner: `NON_QUANTUM_MATH`

Authority ceiling: derived generalized-Davenport theorem over `C_5^3` under the exact registered parent constants and cited donor inequalities.

## Scientific gap

The archive contains the exact constants `D_2(C_5^3)=20` and `D_3(C_5^3)=25`, an exact short-zero-sum threshold `s_{<=6}(C_5^3)=24`, and a donor lower bound for all `k`. As isolated constants these remain computational. Their strongest immediate conceptual consequence has not been isolated as a theorem: every later `D_k` is confined to two consecutive values, and a single `D_4` decision determines whether the expected linear regime is already permanent.

## Donor inputs

Let `D_k(G)` be the least length forcing `k` pairwise-disjoint nonempty zero-sum subsequences.

The following are donor mathematics, not M1 novelty:

1. Freeze--Schmid Theorem 4.1, specialized to `C_5^3`, gives

   `D_k(C_5^3) >= 5k+10`

   for every `k>=2`.

2. Freeze--Schmid Proposition 3.1(3) gives, for every positive integer `l`,

   `D_{k+1}(G) <= max(D_k(G)+l, s_{<=l}(G)-1)`.

3. `s_{<=5}(C_5^3)=eta(C_5^3)=33` is classical.

The 2026-08-24 primary-source recheck used Freeze and Schmid, *Remarks on a generalization of the Davenport constant*, Discrete Mathematics 310 (2010), 3373--3389, arXiv:0905.4248. The recurrence was previously overclaimed as internal and is already retracted in the archive.

## Registered ORION inputs

- `D_2(C_5^3)=20`. Its decisive short-zero-sum upper route is now donor-derived through Zhao's 2025 lemma; no novelty credit is assigned.
- `D_3(C_5^3)=25`, with a 24-term lower witness and a structure-compressed complete upper search.
- `s_{<=6}(C_5^3)=24`.

These give

`D_4 <= max(D_3+6, s_{<=6}-1) = max(31,23) = 31`.

The donor lower bound gives `D_4>=30`, hence `D_4 in {30,31}`.

## Main theorem

For every integer `k>=4`,

`5k+10 <= D_k(C_5^3) <= 5k+11`.

Proof. The lower inequality is the donor Theorem 4.1 specialization. For the upper inequality, the base is `D_4<=31=5*4+11`. Apply Proposition 3.1(3) with `l=5` and `s_{<=5}=33`:

`D_{k+1} <= max(D_k+5,32)`.

If `D_k<=5k+11` for `k>=4`, then `D_k+5<=5(k+1)+11`, while `32<=5(k+1)+11`. Induction proves the upper bound.

## Exact-tail conditional

If `D_4(C_5^3)=30`, then for every `k>=2`,

`D_k(C_5^3)=5k+10`.

The cases `k=2,3` are the exact registered constants. At `k=4` this is the hypothesis. For `k>=4`, the same recurrence gives

`D_{k+1} <= max(5k+10+5,32) = 5(k+1)+10`,

and the donor lower bound gives equality.

No converse tail theorem is claimed from `D_4=31`. In particular, M1 does not prove that an upper-line value at `k=4` propagates forever.

## Machine corroboration

Source and independent lanes must separately:

1. bind the D2 and D3 result identities and file hashes;
2. bind the exact `s_{<=6}=24` parent field;
3. bind the donor correction and lower-bound audit files;
4. evaluate the lower and upper recurrences through at least `k=10,000`;
5. verify the base interval `D_4 in {30,31}`;
6. verify that the conditional `D_4=30` recurrence equals `5k+10` at every checked step;
7. reject any attempted `D_4=31` tail-propagation claim.

Finite recurrence evaluation corroborates the induction; the human induction above carries all-`k` authority.

## Current exact-D4 boundary

The existing bounded support search reports that a hypothetical length-31 total-zero sequence with no zero-sum of length at most five must have support at least 23. Its receipt explicitly has `theorem_authority=false` and `external_replay_required=true`. M1 may record that frontier only as local exploratory evidence. It is not used to prove the tail corridor, `31 in C_0(C_5^3)`, or exact `D_4`.

The unique decisive mathematical gap remains:

`D_4(C_5^3)=30` or `31`.

A proof of `31 in C_0(C_5^3)` would force `D_4=30` and therefore close the exact tail. A length-30 four-disjoint-free obstruction would force `D_4=31` but would not, by itself, determine every later value.

## Authority boundary

This theorem does not establish novelty of the recurrence, lower bound, eventual arithmetic progression, or exact D2. It does not prove exact D4, `C_0` membership, a classification of extremal witnesses, or any statement outside `C_5^3`. Search failure is not novelty evidence. The local support-23 receipt remains non-aggregable, replay-pending evidence. No quantum, physical-resource, or venue authority is granted by the harness. CI is skipped and is not evidence.
