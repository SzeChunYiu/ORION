# Non-quantum math M2 — saturation defects and isolated support-8/9 replay

Date: 2026-08-24

Base: `df58c9d3bd7dedab0011ca2e126bfcf5fcd35429`

Owner: `NON_QUANTUM_MATH`

Status: **FROZEN AFTER A LOCAL TIMING SCOUT REPRODUCED THE ARCHIVED OUTCOMES, BEFORE THE SIGNED SOURCE/GENERIC/NATIVE CAMPAIGN**

This is confirmatory, post-outcome work. The expected support-8 and support-9 outcomes were already present in the archive, and a 2026-08-24 timing scout reproduced them before this protocol was written. No prospective-validation authority is available.

Authority ceiling: a human-readable exponent-`p` saturation-defect lemma and a bounded exact exclusion of support at most nine for the registered `C_5^3` object.

## Object

Let `G` be an elementary abelian exponent-`p` group, where `p` is an odd prime. A sequence `S` is `p`-short-free if it has no nonempty zero-sum subsequence of length at most `p`. Call `S` saturated if every nonzero `x in G` has a representation

`-x = sigma(T)`

for some subsequence `T|S` of length at most `p-1`.

For the exact finite instance, take `G=C_5^3`, `|S|=31`, `sigma(S)=0`, and assume `S` is 5-short-free.

## General saturation-defect lemma

Let a nonzero support point `x` have multiplicity `m<p` in a saturated `p`-short-free sequence. Choose `T|S` with `|T|<=p-1` and `sigma(T)=-x`.

If `T` used at most `m-1` copies of `x`, then one unused copy of `x` from `S` could be appended to `T`, producing a zero-sum subsequence of length at most `p`, contrary to short-freeness. Therefore `T` uses all `m` copies of `x` and has the form

`T=x^m R`,

where `x` is absent from `R`, `|R|<=p-1-m`, and

`sigma(R)=-(m+1)x`.

In particular, multiplicity `m=p-2` is impossible. Then `|R|<=1` and

`sigma(R)=-(p-1)x=x`.

The remainder cannot be empty because `x` is nonzero. If `R` has one term, that term must equal `x`, contradicting the fact that all available copies of `x` were already used in `x^m`.

This proof is symbolic and valid for every odd prime `p`; finite checking of sample primes is corroboration only. No novelty is asserted without donor-first review.

## Why a `C_5^3` support greater than eight is saturated

Suppose a length-31 5-short-free sequence `S` has support greater than eight and is extendable by a nonzero `x` while remaining 5-short-free. The extension has length 32. Donor Property C for `C_5^3` forces every length-32 5-short-free sequence to have exactly eight support points, contradicting the support of `S`. Hence `S` is saturated.

The general lemma with `p=5` excludes multiplicity three from every support-greater-than-eight candidate.

## Support eight

The multiplicity cap is four: five copies of a nonzero point sum to zero, and zero cannot be present. Length 31 on eight points therefore has pattern `4^7 3`.

Let `x` be the multiplicity-three point and `U` the support. Adding one more copy of `x` preserves 5-short-freeness. A new short zero-sum would need all four copies of `x` and at most one other term; `4x+y=0` forces `y=x`, which would require a fifth copy. Thus `U^4` is a length-32 Property-C extremal.

Since `sigma(S)=0`,

`0=4 sigma(U)-x=-sigma(U)-x`,

so `x=-sigma(U)` must lie in `U`.

The frozen checker normalizes an independent triple to the standard basis. Rank at most two is impossible by the donor rank-two short-zero-sum threshold. It then runs byte-array exact-weight reachability and reverse-order two-word bitset reachability. The registered exact row is 564 normalized supports and zero with `-sigma(U) in U`.

## Support nine

For support nine, length 31, multiplicity cap four, and no multiplicity three, let `c_j` count multiplicity-`j` points. Solving

`c_1+c_2+c_4=9`,

`c_1+2c_2+4c_4=31`

gives the unique pattern `c_1=c_2=1`, `c_4=7`, namely `4^7 2 1`.

The frozen checker normalizes every basis multiplicity assignment, enumerates the remaining support canonically, forces the final point from the total-sum equation, and rejects exactly when a zero-sum of length at most five appears. Its byte and reverse bitset engines share only the registered object and arithmetic tables; they use opposite candidate order and different reachability representations. The registered exact row is 6,537,270 nodes in each engine and zero solutions.

## Replay contract

The signed source lane must:

1. bind the two frozen C-source hashes;
2. compile them with the registered warning-clean C11 command;
3. run them in a fresh temporary directory;
4. parse exact JSON rather than terminal prose;
5. bind all registered node, support, forced-candidate, and solution counts;
6. combine the computations only with the human proofs above;
7. delete the temporary executables after the run.

The generic lane must independently verify the signed digest, parent hashes, exact rows, elementary multiplicity equations, and every authority boundary. The native campaign must fail closed if any source, generic, scope, or boundary field differs.

## Strong terminal

`NONQUANTUM_M2_EXPONENT_P_SATURATION_DEFECT_LEMMA__C5CUBED_SUPPORT_LE9_EXCLUDED_BY_ISOLATED_DUAL_REPLAY`

## Authority boundary

This iteration does not exclude support ten or greater, does not upgrade the archived support-23 packet, and does not prove `31 in C_0(C_5^3)` or exact `D_4(C_5^3)`. It is a local isolated replay, not an external independent replication and not prospective evidence. It does not establish novelty of the saturation lemma, Property C, the normalization, or the finite result. No venue, quantum, physical-resource, or CI authority is granted.
