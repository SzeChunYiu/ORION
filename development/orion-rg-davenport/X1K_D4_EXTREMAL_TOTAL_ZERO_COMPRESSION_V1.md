# ORION-RG X1-K — total-zero extremal compression and C0 gate V1

Issue: #981. Coordinates #980, #899, #912, #915, #916.

## Authority

`conditional_structural_derivation: true`

`exact_D4_authority: false`

`C0_membership_authority: false`

`novelty_claim: false`

This packet strengthens the search state under the **conditional assumption** `D_4(C_5^3)=31`. It uses donor Freeze--Schmid Proposition 3.1 and the already committed ORION exact values/short-zero-sum thresholds. It does not claim that 31 belongs to `C_0(C_5^3)`.

## E0 — donor object that matches the obstruction

Fan--Gao--Wang--Zhong--Zhuang (EJC 19(3), 2012, #P31) define `C_0(G)` to be the set of integers `t in [D(G)+1, eta(G)-1]` such that **every zero-sum sequence of length exactly t contains a short zero-sum subsequence**.

For `C_5^3`, their Proposition 26(2) proves only

`C_0(C_5^3) subset [eta(C_5^3)-5, eta(C_5^3)-1] = [28,32]`.

The 2026-08-23 hostile search did not surface a later determination of membership at 31. This is a `NOT_FOUND`, not novelty proof.

Therefore

`31 in C_0(C_5^3)`

is a donor-aware theorem target that exactly attacks the hypothetical D4=31 extremal described below.

## E1 — total-zero extremal representation

Freeze--Schmid characterize `D_k(G)` as the maximum length of a total zero-sum sequence `B` whose maximum factorization length into nontrivial zero-sum factors is `k`; an extremal sequence of length `D_k(G)` may be taken in their `A_k(G)`.

Assume for contradiction

`D_4(C_5^3)=31`.

Then there exists a total zero-sum sequence `B` with

- `|B|=31`;
- `max L(B)=4`.

Freeze--Schmid Proposition 3.1(2) says that if `M` is the minimum length of a minimal zero-sum sequence dividing an extremal length-`D_4` sequence, then

`D_4 <= D_3 + M`.

Since ORION proved `D_3=25`, the assumption `D_4=31` forces

`M>=6`.

But ORION proved `s_{<=6}(C_5^3)=24`, so every 31-term sequence contains a zero-sum subsequence of length at most 6, and an inclusion-minimal one has length at most 6.

Hence every length-31 extremal `B` has minimum atom length exactly 6 and, in particular,

**B contains no zero-sum subsequence of length at most 5.**

Equivalently, the hypothetical extremal is a length-31 **zero-sum short-free** sequence. Therefore

`D_4(C_5^3)=31  =>  31 notin C_0(C_5^3)`.

Contrapositive:

`31 in C_0(C_5^3)  =>  D_4(C_5^3)=30`,

because X1-K already has the donor lower bound 30 and ORION/Freeze--Schmid upper bound 31.

This implication is the preferred symbolic route before a full D4 packing census.

## E2 — forced four-atom length types under D4=31

The same representation compresses the hypothetical 31-term extremal much further.

### First atom

Choose a minimal zero-sum `U_1|B`. By E1, `|U_1|=6`.

Freeze--Schmid Proposition 3.1(1) gives

`max L(B U_1^{-1}) <= 3`.

The complement has length 25, exactly `D_3(C_5^3)`. By the extremal characterization it is a D3-extremal total zero-sum sequence with maximum factorization length exactly 3.

### Second atom

Every atom dividing the complement also divides B, so its atom lengths are at least 6. Since the complement has length 25 and `s_{<=6}=24`, it contains another exact six-term atom `U_2`.

Remove it. The new total-zero complement has length 19 and maximum factorization length at most 2.

### Third atom

ORION's exact short-zero-sum spectrum gives

`s_{<=7}(C_5^3)=19`.

Since no atom has length at most 5, the 19-term complement contains a minimal zero-sum `U_3` with

`|U_3| in {6,7}`.

### Final atom

Removing `U_3` leaves a nonempty total zero-sum sequence of length 13 or 12 with maximum factorization length at most 1. Therefore it is itself a minimal zero-sum atom `U_4`.

Consequently every hypothetical D4=31 extremal admits a four-atom factorization with one of exactly two length patterns:

`(6,6,6,13)`

or

`(6,6,7,12)`.

All atoms are minimal zero-sum and the entire 31-term sequence has no short zero-sum of length at most 5.

This is strictly smaller than the ordinary 30-term obstruction grammar `A_6 B_6 C_t Z`: the total-zero extremal representation freezes the complete four-factor length pattern.

## E3 — primary theorem target

Preferred target:

> **C0-31 theorem candidate.** Every 31-term zero-sum sequence over `C_5^3` contains a nonempty zero-sum subsequence of length at most 5.

Equivalently:

`31 in C_0(C_5^3)`.

If proved, E1 closes exact `D_4(C_5^3)=30` without an arbitrary D4 search.

The result would also add a concrete `C_0(C_5^3)` membership not supplied by the 2012 containment theorem, subject to a fresh primary-source novelty audit before credit.

## E4 — Property-C deficit-one route

Known donor facts:

- `eta(C_5^3)=33`;
- `C_5^3` has Property C;
- therefore every length-32 short-free sequence has the form `U^4` for eight pairwise-distinct support elements.

A hypothetical E3 counterexample has length 31, exactly one below this Property-C extremal length.

Freeze the **deficit-one stability question**:

> Classify length-31 short-free sequences over `C_5^3`; in particular determine whether a zero-sum member can exist.

Do not assume every 31-term short-free sequence extends to a 32-term Property-C extremal. Extension failure is itself a structural state.

### Extension dichotomy

Let S be length31 short-free. For a nonzero `x`, `S*x` fails to be short-free only if the new copy x participates in a short zero-sum, because S itself is short-free. Thus failure at x is equivalent to

`-x in Sigma_{<=4}(S)`

using a nonempty subsequence of at most four terms from S.

Hence exactly one of:

1. **EXTENDABLE:** some nonzero x is not in `-Sigma_{<=4}(S)`; then `S*x` is a length32 short-free Property-C sequence and S is a one-copy deletion from `U^4`;
2. **SATURATED:** every nonzero group element lies in `Sigma_{<=4}(S)`; the obstruction is a full short-subset-sum covering state.

This dichotomy turns 'near Property C' into two explicit theorem grammars instead of an unsupported stability assumption.

For a zero-sum S, the EXTENDABLE branch additionally imposes a sum constraint on the deleted Property-C support/multiplicity pattern; the SATURATED branch supplies a strong covering invariant to attack directly.

## E5 — factor-pattern route

If E4 is difficult, attack only sequences satisfying both:

- zero-sum short-free length31;
- a minimal-zero-sum factorization of type `(6,6,6,13)` or `(6,6,7,12)`.

### `(6,6,6,13)` branch

The length-13 atom is a maximal-length minimal zero-sum sequence. Removing any one of its terms gives a maximal length-12 zero-sum-free sequence, so the existing X1-G inverse census can be reused as a finite structural donor/ORION atlas rather than re-enumerating arbitrary 13-atoms.

### `(6,6,7,12)` branch

The length-12 atom is minimal zero-sum and requires separate classification/extension handling; do not infer maximal-ZSF structure from it.

The two branches should remain separate because their inverse information is materially different.

## E6 — compute-to-compress authorization

Before any large computation, the only authorized discovery computations are:

1. decide existence of a length31 **total-zero short-free** sequence, not arbitrary D4 packing;
2. classify its E4 EXTENDABLE vs SATURATED state;
3. if survivors exist, classify only the two E2 factor-length patterns;
4. reuse the X1-G length13/minimal-ZS and length12/ZSF atlases where logically valid;
5. preserve the first survivor as a `D4=31` obstruction candidate and verify its max factorization length independently.

A full length30/31 multiset scan is fallback only after these compressed grammars fail.

## E7 — bounded support control already observed

A private discovery check on 2026-08-23 examined all total-length-30 multiplicity vectors supported on the six-point support underlying the standard Freeze--Schmid/ORION lower construction and found no vector with zero-sum packing number below four.

This is **bounded discovery evidence only** and has not been granted repository result authority. Its only scheduling consequence is that a hypothetical ordinary length30 obstruction cannot be obtained by merely retuning multiplicities on that exact six-point support; new support geometry would be required.

Do not cite this as theorem until independently reimplemented and archived if it becomes load-bearing.

## E8 — hostile prior-art state

Primary-source findings checked before compute:

- Fan et al. 2012 define `C_0(G)` and prove for `C_5^3` only the containment `C_0(C_5^3) subset [28,32]`;
- their Property-C lemmas do not directly establish 31 for `C_5^3` (the simple `eta-1` lemma requires a coefficient condition not met by `eta(C_5^3)=8(5-1)+1`);
- web searches for explicit `31 in C_0(C_5^3)` / exact `C_0(C_5^3)` did not surface a later resolution.

Status: `PRIOR_ART_NOT_FOUND_FOR_C0_31__NOT_A_NOVELTY_CERTIFICATE`.

## Strong terminals

- `X1K_C0_31_C5CUBED_PROVED__IMPLIES_D4_30`;
- `X1K_C0_31_DONOR_OWNED`;
- `X1K_D4_31_EXTREMAL_FACTOR_TYPES_66613_OR_66712_VALIDATED`;
- `X1K_LENGTH31_SHORTFREE_EXTENDABLE_PROPERTY_C_REDUCTION`;
- `X1K_LENGTH31_SHORTFREE_SATURATED_SIGMA_LE4_OBSTRUCTION`;
- `X1K_D4_31_EXPLICIT_EXTREMAL_FOUND`;
- `X1K_CANNOT_CHECK`.

## Claim boundary

The scientific target is native additive combinatorics: exact D4, C0 membership, deficit-one Property-C stability, and the structure of extremal zero-sum sequences. ORION-Q terminology is research provenance only and must not substitute for a mathematical proof or novelty audit.